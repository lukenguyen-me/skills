#!/usr/bin/env python3
"""Edit supplied icon artwork through GPT Image, Gemini, Grok, or a custom bridge.

One call produces a candidate PNG and a provenance report. Platform exports stay
in export_icons.py. Models are selected explicitly; credentials come from env.
"""

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import uuid

try:
    from PIL import Image, ImageCms, ImageOps
except ImportError as exc:
    raise SystemExit("Install Pillow with ImageCms support in your Python environment.") from exc


class AdapterError(Exception):
    pass


def http(request, timeout):
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise AdapterError(f"Provider HTTP {exc.code}; check model access and settings. No automatic retry.") from None
    except (urllib.error.URLError, TimeoutError):
        raise AdapterError("Provider network/timeout failure. No automatic retry.") from None


def post_json(url, headers, payload, timeout):
    request = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                    headers={**headers, "Content-Type": "application/json"}, method="POST")
    return json.loads(http(request, timeout))


def image_input(path):
    data = Path(path).read_bytes()
    with Image.open(io.BytesIO(data)) as image:
        mime = Image.MIME.get(image.format)
        if getattr(image, "n_frames", 1) != 1:
            raise AdapterError("Choose a still reference image.")
        image.verify()
    if mime not in {"image/png", "image/jpeg", "image/webp"}:
        raise AdapterError("References must be PNG, JPEG, or WebP; rasterize vectors first.")
    return mime, data


def data_uri(path):
    mime, data = image_input(path)
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def standard_image(response, timeout):
    items = response.get("data", [])
    if not items:
        raise AdapterError("Provider returned no image.")
    item = items[0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"], validate=True)
    if item.get("url"):
        if urllib.parse.urlparse(item["url"]).scheme != "https":
            raise AdapterError("Provider image downloads require HTTPS.")
        # Provider credentials are never forwarded to the result image host.
        return http(urllib.request.Request(item["url"]), timeout)
    raise AdapterError("Provider returned no downloadable image.")


def multipart(fields, paths):
    boundary = "icon-edit-" + uuid.uuid4().hex
    chunks = []
    for name, value in fields.items():
        if not isinstance(value, (str, int, float, bool)):
            raise AdapterError("GPT Image options must be scalar form values.")
        value = str(value).lower() if isinstance(value, bool) else str(value)
        chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    for index, path in enumerate(paths):
        mime, data = image_input(path)
        chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; filename="reference-{index}"\r\n'
                      f'Content-Type: {mime}\r\n\r\n'.encode())
        chunks.extend([data, b"\r\n"])
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


class GPTImageAdapter:
    key_env = "OPENAI_API_KEY"

    def edit(self, request, timeout):
        fields = {**request["options"], "model": request["model"], "prompt": request["prompt"], "n": 1}
        body, content_type = multipart(fields, request["images"])
        response = json.loads(http(urllib.request.Request(
            "https://api.openai.com/v1/images/edits", data=body,
            headers={"Authorization": "Bearer " + os.environ[self.key_env], "Content-Type": content_type},
            method="POST",
        ), timeout))
        return standard_image(response, timeout)


class GeminiAdapter:
    key_env = "GEMINI_API_KEY"

    def edit(self, request, timeout):
        if request["options"].get("background"):
            raise AdapterError("This Gemini adapter uses synchronous Interactions; background jobs need a custom bridge.")
        options = {**request["options"]}
        response_format = options.setdefault("response_format", {"type": "image", "mime_type": "image/png"})
        if not isinstance(response_format, dict) or response_format.get("type") != "image":
            raise AdapterError("Gemini response_format must request an image.")
        inputs = [{"type": "text", "text": request["prompt"]}]
        for path in request["images"]:
            mime, data = image_input(path)
            inputs.append({"type": "image", "mime_type": mime, "data": base64.b64encode(data).decode()})
        response = post_json(
            "https://generativelanguage.googleapis.com/v1beta/interactions",
            {"x-goog-api-key": os.environ[self.key_env]},
            {**options, "model": request["model"], "input": inputs}, timeout,
        )
        interaction = response.get("interaction", response)
        for step in reversed(interaction.get("steps", [])):
            if step.get("type") != "model_output":
                continue
            for block in reversed(step.get("content", [])):
                if block.get("type") == "image" and block.get("data"):
                    return base64.b64decode(block["data"], validate=True)
        raise AdapterError("Gemini returned no final image; inspect model access, response status, and prompt.")


class GrokAdapter:
    key_env = "XAI_API_KEY"

    def edit(self, request, timeout):
        images = [{"type": "image_url", "url": data_uri(path)} for path in request["images"]]
        if len(images) > 5:
            raise AdapterError("The current Grok editing API accepts at most five references.")
        payload = {**request["options"], "model": request["model"], "prompt": request["prompt"], "n": 1}
        payload["image" if len(images) == 1 else "images"] = images[0] if len(images) == 1 else images
        response = post_json("https://api.x.ai/v1/images/edits",
                             {"Authorization": "Bearer " + os.environ[self.key_env]}, payload, timeout)
        return standard_image(response, timeout)


ADAPTERS = {"gpt-image": GPTImageAdapter, "gemini": GeminiAdapter, "grok": GrokAdapter}


def load_custom(path):
    config = json.loads(Path(path).read_text())
    if not isinstance(config, dict) or not isinstance(config.get("id"), str) or not config["id"].strip():
        raise AdapterError("Custom adapter requires an id.")
    command = config.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
        raise AdapterError("Custom command must be a nonempty argument array.")
    caps = config.get("capabilities", {})
    if not isinstance(caps, dict) or caps.get("reference_edit") is not True:
        raise AdapterError("Custom adapter must support reference editing.")
    limit = caps.get("max_reference_images")
    if type(limit) is not int or limit < 1:
        raise AdapterError("Custom max_reference_images must be a positive integer.")
    keys = config.get("required_env", [])
    if not isinstance(keys, list) or not all(isinstance(key, str) and key for key in keys):
        raise AdapterError("required_env must list environment variable names.")
    return config


def custom_edit(config, request, timeout):
    if request["provider"] != config["id"]:
        raise AdapterError("Request provider does not match the custom adapter id.")
    caps = config["capabilities"]
    if len(request["images"]) > caps["max_reference_images"]:
        raise AdapterError("Reference count exceeds the custom adapter limit.")
    if request["require_transparency"] and caps.get("transparent_output") is not True:
        raise AdapterError("Custom adapter must declare transparent_output for a foreground request.")
    if any(not os.environ.get(key) for key in config.get("required_env", [])):
        raise AdapterError("Custom adapter is missing a required environment key.")
    # A bridge writes into staging so a failed or invalid result cannot occupy
    # the final variant path. The parent publishes a normalized PNG after checks.
    with tempfile.TemporaryDirectory(prefix="icon-provider-") as staging:
        child_request = {**request, "output": str(Path(staging) / "candidate.png")}
        try:
            result = subprocess.run(config["command"], input=json.dumps(child_request),
                                    text=True, capture_output=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            raise AdapterError("Custom adapter timed out; inspect its job before retrying.") from None
        if result.returncode:
            raise AdapterError(f"Custom adapter exited {result.returncode}. No automatic retry.")
        metadata = json.loads(result.stdout)
        return Path(metadata["output"]).read_bytes()


def validate_request(request):
    if not isinstance(request, dict):
        raise AdapterError("Request must be a JSON object.")
    request = dict(request)
    for field in ("provider", "model", "prompt", "output"):
        if not isinstance(request.get(field), str) or not request[field].strip():
            raise AdapterError(f"Request requires a nonempty {field}.")
    images = request.get("images")
    if not isinstance(images, list) or not images or not all(isinstance(x, str) and x for x in images):
        raise AdapterError("Provide at least one existing artwork path in images; this adapter edits references.")
    request["images"] = [str(Path(path).resolve()) for path in images]
    for path in request["images"]:
        image_input(path)
    output = Path(request["output"]).resolve()
    report = Path(str(output) + ".edit.json")
    if output.suffix.lower() != ".png":
        raise AdapterError("Candidate output must have a .png extension.")
    if output.exists() or report.exists():
        raise AdapterError("Candidate or report already exists; choose a new variant path.")
    request["output"] = str(output)
    require_alpha = request.setdefault("require_transparency", False)
    if type(require_alpha) is not bool:
        raise AdapterError("require_transparency must be boolean.")
    options = request.setdefault("options", {})
    if not isinstance(options, dict):
        raise AdapterError("options must be an object.")
    reserved = {"model", "prompt", "image", "images", "input", "contents", "n", "stream",
                "key", "api_key", "apikey", "authorization", "access_token", "token"}
    for key in options:
        if not isinstance(key, str) or not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", key):
            raise AdapterError("Option names must be identifiers.")
        if key.lower() in reserved:
            raise AdapterError("options cannot replace core inputs, credentials, or the synchronous single-variant workflow.")
    return request


def edit(request, custom=None, timeout=300):
    if not math.isfinite(timeout) or timeout <= 0:
        raise AdapterError("timeout must be a positive finite number.")
    request = validate_request(request)
    references = [{"path": path, "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}
                  for path in request["images"]]
    if custom is not None:
        data = custom_edit(custom, request, timeout)
    else:
        factory = ADAPTERS.get(request["provider"])
        if factory is None:
            raise AdapterError("Unknown provider; supply a custom adapter config.")
        adapter = factory()
        if not os.environ.get(adapter.key_env):
            raise AdapterError(f"Missing {adapter.key_env}.")
        data = adapter.edit(request, timeout)
    with Image.open(io.BytesIO(data)) as returned:
        returned.load()
        if getattr(returned, "n_frames", 1) != 1:
            raise AdapterError("Provider result must be a still image.")
        # Preserve decoded pixels, alpha, and color profile. The platform exporter
        # converts to sRGB and flattens only assets that require an opaque image.
        image = ImageOps.exif_transpose(returned)
        profile = image.info.get("icc_profile")
        if image.mode in {"CMYK", "LAB"} and not profile:
            raise AdapterError("Provider result needs an embedded color profile for CMYK/LAB conversion.")
        if profile and image.mode in {"CMYK", "LAB", "L", "LA"}:
            alpha = image.getchannel("A") if image.mode == "LA" else None
            color = image.getchannel("L") if image.mode == "LA" else image
            srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
            try:
                image = ImageCms.profileToProfile(color, ImageCms.ImageCmsProfile(io.BytesIO(profile)),
                                                 srgb, outputMode="RGB").convert("RGBA")
            except (OSError, ValueError, ImageCms.PyCMSError):
                raise AdapterError("Provider result has an incompatible embedded color profile.") from None
            if alpha is not None:
                image.putalpha(alpha)
            profile = srgb.tobytes()
        else:
            image = image.convert("RGBA")
        extrema = image.getchannel("A").getextrema()
        if extrema[1] == 0:
            raise AdapterError("Provider returned an empty transparent image.")
        if request["require_transparency"] and extrema[0] == 255:
            raise AdapterError("Provider returned an opaque image; a transparent foreground was required.")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", icc_profile=profile)
        png = buffer.getvalue()
        width, height = image.size
    output = Path(request["output"])
    report = Path(str(output) + ".edit.json")
    metadata = {
        "provider": request["provider"], "model": request["model"], "output": str(output),
        "width": width, "height": height, "mode": "RGBA", "alpha_extrema": list(extrema),
        "sha256": hashlib.sha256(png).hexdigest(), "visual_review": "pending",
    }
    evidence = {**metadata, "generated_at": datetime.now(timezone.utc).isoformat(),
                "transport": "custom-command" if custom else "http",
                "prompt": request["prompt"], "options": request["options"],
                "require_transparency": request["require_transparency"], "references": references}
    serialized = json.dumps(evidence, indent=2) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(png)
    try:
        with report.open("x", encoding="utf-8") as stream:
            stream.write(serialized)
    except OSError:
        output.unlink()
        raise
    return {**metadata, "report": str(report)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="Check local key presence without calling providers.")
    action.add_argument("--request", help="Shared edit request JSON file; paths resolve against the working directory.")
    parser.add_argument("--adapter-config", help="Custom command adapter config JSON.")
    parser.add_argument("--timeout", type=float, default=300)
    args = parser.parse_args()
    try:
        custom = load_custom(args.adapter_config) if args.adapter_config else None
        if args.check:
            result = [{"provider": name, "key_env": factory.key_env,
                       "credential_present": bool(os.environ.get(factory.key_env)),
                       "model_access": "not-checked"} for name, factory in ADAPTERS.items()]
            if custom:
                result.append({"provider": custom["id"], "capabilities": custom["capabilities"],
                               "credential_present": all(bool(os.environ.get(key)) for key in custom.get("required_env", [])),
                               "model_access": "not-checked"})
        else:
            result = edit(json.loads(Path(args.request).read_text()), custom, args.timeout)
        print(json.dumps(result, indent=2))
    except AdapterError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        print("Invalid request, provider response, image, or local file; inspect the named inputs.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
