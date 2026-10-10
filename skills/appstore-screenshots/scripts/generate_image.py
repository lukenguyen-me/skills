#!/usr/bin/env python3
"""One image-request contract over Gemini, GPT Image, Grok, or a custom command."""

import argparse
import base64
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

from PIL import Image


class AdapterError(Exception):
    pass


def http(request, timeout):
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        # Provider bodies can echo prompts, credentials, or data URIs.
        raise AdapterError(f"Provider HTTP {exc.code}; check access, model, and settings") from None
    except (urllib.error.URLError, TimeoutError):
        raise AdapterError("Provider network/timeout failure; no automatic retry") from None


def post_json(url, headers, payload, timeout):
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={**headers, "Content-Type": "application/json"}, method="POST",
    )
    return json.loads(http(request, timeout))


def image_input(path):
    data = Path(path).read_bytes()
    with Image.open(io.BytesIO(data)) as image:
        mime = Image.MIME.get(image.format)
        image.verify()
    if mime not in {"image/png", "image/jpeg", "image/webp"}:
        raise AdapterError("References must be PNG, JPEG, or WebP")
    return mime, data


def data_uri(path):
    mime, data = image_input(path)
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def standard_result(response, timeout):
    items = response.get("data", [])
    if not items:
        raise AdapterError("Provider returned no image")
    item = items[0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"], validate=True)
    if item.get("url"):
        if urllib.parse.urlparse(item["url"]).scheme != "https":
            raise AdapterError("Provider image download requires HTTPS")
        # Download without forwarding provider credentials to the image host.
        return http(urllib.request.Request(item["url"]), timeout)
    raise AdapterError("Provider returned no downloadable image")


class GeminiAdapter:
    key_env = "GEMINI_API_KEY"

    def generate(self, request, timeout):
        parts = [{"text": request["prompt"]}]
        for path in request["images"]:
            mime, data = image_input(path)
            parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(data).decode()}})
        config = {**request["options"], "responseModalities": ["TEXT", "IMAGE"]}
        model = urllib.parse.quote(request["model"], safe="")
        response = post_json(
            f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent",
            {"x-goog-api-key": os.environ[self.key_env]},
            {"contents": [{"parts": parts}], "generationConfig": config}, timeout,
        )
        for candidate in response.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if part.get("thought"):
                    continue
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    return base64.b64decode(inline["data"], validate=True)
        raise AdapterError("Gemini returned no final image; check model or prompt")


def multipart(fields, paths):
    boundary = "aso-" + uuid.uuid4().hex
    chunks = []
    for name, value in fields.items():
        if isinstance(value, (dict, list)):
            raise AdapterError("GPT Image options must be scalar form values")
        chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    for index, path in enumerate(paths):
        mime, data = image_input(path)
        chunks.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; filename="reference-{index}"\r\n'
            f'Content-Type: {mime}\r\n\r\n'.encode()
        )
        chunks.extend([data, b"\r\n"])
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


class GPTImageAdapter:
    key_env = "OPENAI_API_KEY"

    def generate(self, request, timeout):
        fields = {**request["options"], "model": request["model"], "prompt": request["prompt"], "n": 1}
        headers = {"Authorization": "Bearer " + os.environ[self.key_env]}
        if request["images"]:
            body, content_type = multipart(fields, request["images"])
            response = json.loads(http(urllib.request.Request(
                "https://api.openai.com/v1/images/edits", data=body,
                headers={**headers, "Content-Type": content_type}, method="POST",
            ), timeout))
        else:
            response = post_json("https://api.openai.com/v1/images/generations", headers, fields, timeout)
        return standard_result(response, timeout)


class GrokAdapter:
    key_env = "XAI_API_KEY"

    def generate(self, request, timeout):
        payload = {**request["options"], "model": request["model"], "prompt": request["prompt"], "n": 1}
        images = [{"type": "image_url", "url": data_uri(path)} for path in request["images"]]
        if len(images) > 5:
            raise AdapterError("Grok adapter accepts at most five references")
        if len(images) == 1:
            payload["image"] = images[0]
        elif images:
            payload["images"] = images
        operation = "edits" if images else "generations"
        response = post_json(
            f"https://api.x.ai/v1/images/{operation}",
            {"Authorization": "Bearer " + os.environ[self.key_env]}, payload, timeout,
        )
        return standard_result(response, timeout)


ADAPTERS = {"gemini": GeminiAdapter, "gpt-image": GPTImageAdapter, "grok": GrokAdapter}


def load_custom(path):
    config = json.loads(Path(path).read_text())
    if not isinstance(config.get("id"), str) or not config["id"]:
        raise AdapterError("Custom adapter requires an id")
    command = config.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
        raise AdapterError("Custom command must be a nonempty argument array")
    caps = config.get("capabilities", {})
    limit = caps.get("max_reference_images", 0)
    if type(limit) is not int or limit < 0 or type(caps.get("reference_edit", False)) is not bool:
        raise AdapterError("Custom capabilities require a boolean reference_edit and nonnegative integer limit")
    keys = config.get("required_env", [])
    if not isinstance(keys, list) or not all(isinstance(x, str) and x for x in keys):
        raise AdapterError("required_env must contain environment variable names")
    return config


def custom_generate(config, request, timeout):
    caps = config.get("capabilities", {})
    if request["images"] and not caps.get("reference_edit", False):
        raise AdapterError("Selected custom provider does not support reference editing")
    if len(request["images"]) > caps.get("max_reference_images", 0):
        raise AdapterError("Reference count exceeds the custom adapter capability")
    if any(not os.environ.get(key) for key in config.get("required_env", [])):
        raise AdapterError("Custom adapter is missing a required environment key")
    try:
        result = subprocess.run(
            config["command"], input=json.dumps(request), text=True,
            capture_output=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        raise AdapterError("Custom adapter timed out; check its job before retrying") from None
    if result.returncode:
        raise AdapterError(f"Custom adapter exited {result.returncode}; no automatic retry")
    metadata = json.loads(result.stdout)
    source = Path(metadata["output"]).resolve()
    return source.read_bytes()


def validate_request(request):
    for field in ("provider", "model", "prompt", "output"):
        if not isinstance(request.get(field), str) or not request[field].strip():
            raise AdapterError(f"Request requires a nonempty {field}")
    images = request.get("images", [])
    if not isinstance(images, list) or not all(isinstance(x, str) and x for x in images):
        raise AdapterError("images must be an array of local paths")
    request["images"] = [str(Path(path).resolve()) for path in images]
    for path in request["images"]:
        image_input(path)
    output = Path(request["output"]).resolve()
    if output.suffix.lower() != ".png":
        raise AdapterError("Adapter output must have a .png extension")
    if output.exists():
        raise AdapterError("Output already exists; choose a new variant path")
    request["output"] = str(output)
    options = request.setdefault("options", {})
    if not isinstance(options, dict):
        raise AdapterError("options must be an object")
    reserved = {"model", "prompt", "image", "images", "n", "contents", "key", "api_key", "authorization"}
    if reserved.intersection(key.lower() for key in options):
        raise AdapterError("options cannot replace core inputs, variant count, or credentials")
    if any('"' in key or "\r" in key or "\n" in key for key in options):
        raise AdapterError("Invalid option name")
    return request


def generate(request, custom=None, timeout=300):
    request = validate_request(dict(request))
    if custom is not None:
        if request["provider"] != custom["id"]:
            raise AdapterError("Request provider does not match custom adapter id")
        data = custom_generate(custom, request, timeout)
    else:
        factory = ADAPTERS.get(request["provider"])
        if factory is None:
            raise AdapterError("Unknown provider; supply a custom adapter config")
        adapter = factory()
        if not os.environ.get(adapter.key_env):
            raise AdapterError(f"Missing {adapter.key_env}")
        data = adapter.generate(request, timeout)
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        rgba = image.convert("RGBA")
        rgb = Image.new("RGB", rgba.size, "white")
        rgb.paste(rgba, mask=rgba.getchannel("A"))
        buffer = io.BytesIO()
        rgb.save(buffer, format="PNG")
        width, height = rgb.size
    output = Path(request["output"])
    output.parent.mkdir(parents=True, exist_ok=True)
    # Custom commands can already have written the requested output. All other
    # paths are created exclusively so a prior variant is never replaced.
    mode = "wb" if custom is not None and output.exists() else "xb"
    with output.open(mode) as stream:
        stream.write(buffer.getvalue())
    return {"provider": request["provider"], "model": request["model"],
            "output": str(output), "width": width, "height": height}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="Local credential checks; no API calls")
    action.add_argument("--request", help="Shared request JSON file")
    parser.add_argument("--adapter-config", help="Custom command adapter config JSON")
    parser.add_argument("--timeout", type=float, default=300)
    args = parser.parse_args()
    try:
        if args.timeout <= 0:
            raise AdapterError("timeout must be positive")
        custom = load_custom(args.adapter_config) if args.adapter_config else None
        if args.check:
            status = [{"provider": name, "credential_present": bool(os.environ.get(adapter.key_env))}
                      for name, adapter in ADAPTERS.items()]
            if custom:
                status.append({"provider": custom["id"], "capabilities": custom.get("capabilities", {}),
                               "credential_present": all(bool(os.environ.get(key)) for key in custom.get("required_env", []))})
            print(json.dumps(status))
        else:
            print(json.dumps(generate(json.loads(Path(args.request).read_text()), custom, args.timeout)))
    except AdapterError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        print("Invalid request, adapter response, image, or local file; inspect the named inputs", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
