"""Offline behavioral checks for provider transport and screenshot artifacts."""

import base64
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from PIL import Image, ImageFont


SCRIPTS = Path(__file__).resolve().parents[1] / "skills/appstore-screenshots/scripts"


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generation = load_module("generate_image")
layout = load_module("layout")


def png_bytes(colour="red", size=(40, 80), mode="RGB"):
    buffer = io.BytesIO()
    Image.new(mode, size, colour).save(buffer, format="PNG")
    return buffer.getvalue()


class ScreenshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.references = []
        for index, colour in enumerate(("red", "blue", "green")):
            path = self.root / f"ref-{index}.png"
            path.write_bytes(png_bytes(colour))
            self.references.append(str(path))
        self.image = png_bytes()
        self.response = {"data": [{"b64_json": base64.b64encode(self.image).decode()}]}

    def request(self, provider="gpt-image", **updates):
        return {"provider": provider, "model": "selected-image-model", "prompt": "Exact headline and UI",
                "images": self.references[:2], "output": str(self.root / "variant.png"), "options": {}, **updates}

    def assert_artifact(self, result, size=(40, 80)):
        with Image.open(result["output"]) as image:
            self.assertEqual(image.size, size)
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.format, "PNG")

    def test_gpt_edit_sends_multipart_ordered_references(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-secret"}), patch.object(
            generation, "http", return_value=json.dumps(self.response).encode()
        ) as transport:
            result = generation.generate(self.request(options={"size": "1024x1536"}))
        request = transport.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.openai.com/v1/images/edits")
        self.assertEqual(request.data.count(b'name="image[]"'), 2)
        self.assertLess(request.data.index(Path(self.references[0]).read_bytes()),
                        request.data.index(Path(self.references[1]).read_bytes()))
        self.assertIn(b'name="size"\r\n\r\n1024x1536', request.data)
        self.assertNotIn("test-secret", json.dumps(result))
        self.assert_artifact(result)

    def test_gemini_skips_thought_image_and_preserves_reference_order(self):
        response = {"candidates": [{"content": {"parts": [
            {"thought": True, "inlineData": {"data": base64.b64encode(png_bytes("black")).decode()}},
            {"inlineData": {"data": base64.b64encode(self.image).decode()}},
        ]}}]}
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-secret"}), patch.object(
            generation, "post_json", return_value=response
        ) as transport:
            result = generation.generate(self.request("gemini", options={"imageConfig": {"aspectRatio": "9:16"}}))
        url, headers, body, timeout = transport.call_args.args
        self.assertTrue(url.endswith("selected-image-model:generateContent"))
        self.assertEqual(body["generationConfig"]["responseModalities"], ["TEXT", "IMAGE"])
        parts = body["contents"][0]["parts"]
        self.assertEqual(base64.b64decode(parts[1]["inline_data"]["data"]), Path(self.references[0]).read_bytes())
        with Image.open(result["output"]) as image:
            self.assertEqual(image.getpixel((0, 0)), (255, 0, 0))

    def test_grok_multi_edit_is_json_with_data_uris(self):
        with patch.dict(os.environ, {"XAI_API_KEY": "test-secret"}), patch.object(
            generation, "post_json", return_value=self.response
        ) as transport:
            result = generation.generate(self.request("grok", options={"aspect_ratio": "9:16"}))
        url, headers, body, timeout = transport.call_args.args
        self.assertEqual(url, "https://api.x.ai/v1/images/edits")
        self.assertNotIn("image", body)
        self.assertEqual(len(body["images"]), 2)
        self.assertEqual(body["images"][0]["type"], "image_url")
        self.assertTrue(body["images"][0]["url"].startswith("data:image/png;base64,"))
        self.assert_artifact(result)

    def test_grok_single_reference_uses_image_field_and_url_download(self):
        with patch.dict(os.environ, {"XAI_API_KEY": "test-secret"}), patch.object(
            generation, "post_json", return_value={"data": [{"url": "https://cdn.example/image.png"}]}
        ) as api, patch.object(generation, "http", return_value=self.image) as download:
            result = generation.generate(self.request("grok", images=self.references[:1]))
        self.assertIn("image", api.call_args.args[2])
        self.assertNotIn("images", api.call_args.args[2])
        self.assertFalse(download.call_args.args[0].has_header("Authorization"))
        self.assert_artifact(result)

    def test_generate_without_references_uses_generation_endpoints(self):
        for provider, key, endpoint in (
            ("gpt-image", "OPENAI_API_KEY", "https://api.openai.com/v1/images/generations"),
            ("grok", "XAI_API_KEY", "https://api.x.ai/v1/images/generations"),
        ):
            with self.subTest(provider=provider), patch.dict(os.environ, {key: "secret"}), patch.object(
                generation, "post_json", return_value=self.response
            ) as api:
                result = generation.generate(self.request(provider, images=[], output=str(self.root / f"{provider}.png")))
                self.assertEqual(api.call_args.args[0], endpoint)
                self.assert_artifact(result)

    def test_missing_key_and_existing_output_fail_before_network(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(generation, "http") as transport:
            with self.assertRaisesRegex(generation.AdapterError, "Missing OPENAI_API_KEY"):
                generation.generate(self.request())
            output = self.root / "variant.png"
            output.write_bytes(self.image)
            with self.assertRaisesRegex(generation.AdapterError, "already exists"):
                generation.generate(self.request())
            self.assertEqual(output.read_bytes(), self.image)
            transport.assert_not_called()

    def test_failed_provider_never_falls_back_or_creates_output(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "secret"}), patch.object(
            generation, "post_json", return_value={"candidates": []}
        ) as api:
            with self.assertRaisesRegex(generation.AdapterError, "no final image"):
                generation.generate(self.request("gemini"))
            self.assertEqual(api.call_count, 1)
            self.assertFalse((self.root / "variant.png").exists())

    def test_http_errors_hide_response_details(self):
        error = urllib.error.HTTPError("https://example.test", 401, "private-secret", {}, io.BytesIO(b"private-secret"))
        with patch.object(generation.urllib.request, "urlopen", side_effect=error):
            with self.assertRaises(generation.AdapterError) as raised:
                generation.http(generation.urllib.request.Request("https://example.test"), 1)
            self.assertIn("401", str(raised.exception))
            self.assertNotIn("private-secret", str(raised.exception))

    def test_options_cannot_replace_input_or_variant_count(self):
        for field in ("images", "prompt", "model", "n", "api_key"):
            with self.subTest(field=field), self.assertRaises(generation.AdapterError):
                generation.validate_request(self.request(options={field: "replacement"}))

    def test_custom_command_round_trip_without_shell(self):
        bridge = self.root / "bridge with spaces.py"
        bridge.write_text(
            "import json, pathlib, sys\n"
            "r = json.load(sys.stdin)\n"
            "assert all(pathlib.Path(p).is_absolute() for p in r['images'])\n"
            "pathlib.Path(r['output']).write_bytes(pathlib.Path(r['images'][0]).read_bytes())\n"
            "print(json.dumps({'output': r['output']}))\n"
        )
        config_path = self.root / "adapter.json"
        config_path.write_text(json.dumps({"id": "my-provider", "command": [sys.executable, str(bridge)],
                                         "capabilities": {"reference_edit": True, "max_reference_images": 3}}))
        result = generation.generate(self.request("my-provider"), generation.load_custom(config_path))
        self.assert_artifact(result)

    def test_custom_reference_limit_blocks_execution(self):
        custom = {"id": "limited", "command": ["unused"], "capabilities": {"reference_edit": True, "max_reference_images": 1}}
        with patch.object(generation.subprocess, "run") as command:
            with self.assertRaisesRegex(generation.AdapterError, "Reference count"):
                generation.generate(self.request("limited"), custom)
            command.assert_not_called()
        custom["capabilities"]["reference_edit"] = False
        with self.assertRaisesRegex(generation.AdapterError, "does not support"):
            generation.generate(self.request("limited"), custom)

    def test_corrupt_provider_image_is_rejected_without_output(self):
        response = {"data": [{"b64_json": base64.b64encode(b"not an image").decode()}]}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "secret"}), patch.object(
            generation, "http", return_value=json.dumps(response).encode()
        ):
            with self.assertRaises(OSError):
                generation.generate(self.request())
        self.assertFalse((self.root / "variant.png").exists())

    def test_custom_nonzero_exit_is_failure_even_with_output_metadata(self):
        custom = {"id": "broken", "command": ["unused"],
                  "capabilities": {"reference_edit": True, "max_reference_images": 3}}
        result = generation.subprocess.CompletedProcess(["unused"], 2,
                    stdout=json.dumps({"output": self.references[0]}), stderr="private diagnostic")
        with patch.object(generation.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(generation.AdapterError, "exited 2"):
                generation.generate(self.request("broken"), custom)
        self.assertFalse((self.root / "variant.png").exists())

    def test_export_crops_sides_symmetrically_and_keeps_top(self):
        source = self.root / "wide.png"
        image = Image.new("RGB", (100, 100), "red")
        image.paste("blue", (25, 0, 75, 100))
        image.save(source)
        result = layout.export_image(source, self.root / "export.png", 50, 100)
        self.assertEqual(result["crop_box"], (25, 0, 75, 100))
        with Image.open(result["output"]) as output:
            self.assertEqual(output.getpixel((0, 0)), (0, 0, 255))
        self.assert_artifact(result, (50, 100))

    def test_export_trims_bottom_and_flattens_alpha(self):
        source = self.root / "narrow.png"
        source.write_bytes(png_bytes((255, 0, 0, 0), (50, 200), "RGBA"))
        result = layout.export_image(source, self.root / "export.png", 50, 100, "#2563EB")
        self.assertEqual(result["crop_box"], (0, 0, 50, 100))
        self.assert_artifact(result, (50, 100))
        with Image.open(result["output"]) as output:
            self.assertEqual(output.getpixel((0, 0)), (37, 99, 235))

    def test_layout_refuses_to_overwrite(self):
        output = self.root / "approved.png"
        output.write_bytes(self.image)
        with self.assertRaises(FileExistsError):
            layout.export_image(self.references[0], output, 50, 100)
        self.assertEqual(output.read_bytes(), self.image)

    def test_scaffold_exact_dimensions_and_capture_content(self):
        # Pillow includes a small font suitable for portable layout tests.
        font = self.root / "font.ttf"
        font.write_bytes(ImageFont.load_default(size=12).font_bytes)
        result = layout.compose(self.references[0], self.root / "scaffold.png", font,
                                "TRACK", "YOUR PROGRESS", "#2563EB", width=500, height=1100)
        self.assert_artifact(result, (500, 1100))
        with Image.open(result["output"]) as image:
            self.assertEqual(image.getpixel((0, 0)), (37, 99, 235))
            self.assertEqual(image.getpixel((250, 550)), (255, 0, 0))
        with self.assertRaisesRegex(ValueError, "safe area"):
            layout.compose(self.references[0], self.root / "bad.png", font, "EXTREMELYLONGVERB",
                           "YOUR PROGRESS", "#2563EB", width=500, height=1100)

    def test_showcase_accepts_mixed_orientations(self):
        landscape = self.root / "landscape.png"
        landscape.write_bytes(png_bytes("green", (160, 90)))
        result = layout.showcase([self.references[0], landscape], self.root / "showcase.png")
        self.assert_artifact(result, (272, 138))


if __name__ == "__main__":
    unittest.main()
