"""Provider contracts, alpha preservation, and the artwork-to-export handoff.

HTTP calls are mocked. Custom command bridges run locally without a provider.
"""

import base64
from email.parser import BytesParser
from email.policy import default
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

from PIL import Image, ImageCms, ImageDraw, UnidentifiedImageError


SCRIPTS = Path(__file__).resolve().parents[1] / "skills/prepare-app-icons/scripts"


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


artwork = load_module("edit_artwork", "edit_artwork.py")
icons = load_module("export_icons", "export_icons.py")


def png_bytes(image, **kwargs):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", **kwargs)
    return buffer.getvalue()


def image_response(data):
    return {"data": [{"b64_json": base64.b64encode(data).decode()}]}


class ArtworkProviderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "original mark.png"
        self.image = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(self.image).rectangle((20, 25, 59, 54), fill=(220, 40, 60, 255))
        self.image.putpixel((20, 24), (110, 140, 210, 128))
        self.profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        self.returned = png_bytes(self.image, icc_profile=self.profile)
        self.source.write_bytes(self.returned)
        self.keys = {"OPENAI_API_KEY": "test-openai-key", "GEMINI_API_KEY": "test-gemini-key",
                     "XAI_API_KEY": "test-xai-key"}
        environment = patch.dict(os.environ, self.keys)
        environment.start()
        self.addCleanup(environment.stop)

    def request(self, provider="gpt-image", filename="candidate.png", **changes):
        return {"provider": provider, "model": "chosen-image-edit-model",
                "prompt": "Preserve the supplied mark; extract its transparent foreground.",
                "images": [str(self.source)], "output": str(self.root / filename),
                "require_transparency": True, "options": {}, **changes}

    def assert_candidate(self, result):
        with Image.open(result["output"]) as image:
            self.assertEqual((image.mode, image.size), ("RGBA", self.image.size))
            self.assertEqual(image.tobytes(), self.image.tobytes())
            self.assertEqual(image.info["icc_profile"], self.profile)
        evidence = json.loads(Path(result["report"]).read_text())
        self.assertEqual(evidence["sha256"], hashlib.sha256(Path(result["output"]).read_bytes()).hexdigest())
        self.assertEqual(evidence["references"][0]["sha256"], hashlib.sha256(self.returned).hexdigest())
        self.assertEqual(evidence["visual_review"], "pending")
        self.assertEqual(evidence["alpha_extrema"], [0, 255])
        self.assertEqual(self.source.read_bytes(), self.returned)
        for secret in self.keys.values():
            self.assertNotIn(secret, Path(result["report"]).read_text())
        return evidence

    def test_gpt_image_multipart_edit_preserves_reference_order_and_alpha(self):
        second = self.root / "second.png"
        second.write_bytes(png_bytes(Image.new("RGB", (12, 12), "blue")))
        request = self.request(images=[str(self.source), str(second)],
                               options={"background": "transparent", "output_format": "png"})
        with patch.object(artwork, "http", return_value=json.dumps(image_response(self.returned)).encode()) as call:
            result = artwork.edit(request)
        self.assertEqual(call.call_count, 1)
        sent = call.call_args.args[0]
        self.assertEqual(sent.full_url, "https://api.openai.com/v1/images/edits")
        self.assertEqual(sent.get_method(), "POST")
        self.assertEqual(sent.get_header("Authorization"), "Bearer test-openai-key")
        message = BytesParser(policy=default).parsebytes(
            f'Content-Type: {sent.get_header("Content-type")}\r\nMIME-Version: 1.0\r\n\r\n'.encode() + sent.data)
        fields, references = {}, []
        for part in message.iter_parts():
            name = part.get_param("name", header="content-disposition")
            data = part.get_payload(decode=True)
            if name == "image[]":
                references.append(data)
            else:
                fields[name] = data.decode()
        self.assertEqual(references, [self.returned, second.read_bytes()])
        self.assertEqual(fields, {"model": request["model"], "prompt": request["prompt"], "n": "1",
                                  "background": "transparent", "output_format": "png"})
        evidence = self.assert_candidate(result)
        self.assertEqual((evidence["provider"], evidence["model"], evidence["transport"]),
                         ("gpt-image", request["model"], "http"))

    def test_gemini_interactions_uses_final_model_image_and_ordered_inputs(self):
        response = {"steps": [
            {"type": "model_output", "content": [{"type": "text", "text": "Edited"},
                {"type": "image", "mime_type": "image/png", "data": base64.b64encode(self.returned).decode()}]},
            {"type": "tool_output", "content": [{"type": "image", "data": "not-final-image"}]},
        ]}
        request = self.request("gemini", options={"response_format": {
            "type": "image", "mime_type": "image/png", "aspect_ratio": "1:1"}})
        with patch.object(artwork, "post_json", return_value=response) as call:
            result = artwork.edit(request)
        url, headers, payload, timeout = call.call_args.args
        self.assertEqual(url, "https://generativelanguage.googleapis.com/v1beta/interactions")
        self.assertEqual(headers, {"x-goog-api-key": "test-gemini-key"})
        self.assertEqual(payload["model"], request["model"])
        self.assertEqual(payload["response_format"], request["options"]["response_format"])
        self.assertEqual(payload["input"], [
            {"type": "text", "text": request["prompt"]},
            {"type": "image", "mime_type": "image/png", "data": base64.b64encode(self.returned).decode()},
        ])
        self.assert_candidate(result)

    def test_gemini_default_image_format_and_unavailable_final_image(self):
        with patch.object(artwork, "post_json", return_value={"steps": []}) as call:
            with self.assertRaisesRegex(artwork.AdapterError, "no final image"):
                artwork.edit(self.request("gemini"))
        self.assertEqual(call.call_args.args[2]["response_format"], {"type": "image", "mime_type": "image/png"})
        self.assertFalse((self.root / "candidate.png").exists())
        with patch.object(artwork, "post_json") as call:
            with self.assertRaisesRegex(artwork.AdapterError, "background jobs"):
                artwork.edit(self.request("gemini", options={"background": True}))
            call.assert_not_called()

    def test_grok_single_and_multiple_reference_json_contract(self):
        second = self.root / "second.png"
        second.write_bytes(png_bytes(Image.new("RGB", (12, 12), "blue")))
        for count in (1, 2):
            with self.subTest(count=count):
                paths = [str(self.source), str(second)][:count]
                request = self.request("grok", f"grok-{count}.png", images=paths, options={"aspect_ratio": "1:1"})
                with patch.object(artwork, "post_json", return_value=image_response(self.returned)) as call:
                    result = artwork.edit(request)
                url, headers, payload, timeout = call.call_args.args
                self.assertEqual(url, "https://api.x.ai/v1/images/edits")
                self.assertEqual(headers, {"Authorization": "Bearer test-xai-key"})
                self.assertEqual((payload["model"], payload["prompt"], payload["n"]),
                                 (request["model"], request["prompt"], 1))
                images = [payload["image"]] if count == 1 else payload["images"]
                self.assertEqual([item["type"] for item in images], ["image_url"] * count)
                for item, path in zip(images, paths):
                    self.assertTrue(item["url"].startswith("data:image/png;base64,"))
                    self.assertEqual(base64.b64decode(item["url"].split(",", 1)[1]), Path(path).read_bytes())
                self.assert_candidate(result)
        with patch.object(artwork, "post_json") as call:
            with self.assertRaisesRegex(artwork.AdapterError, "at most five"):
                artwork.edit(self.request("grok", images=[str(self.source)] * 6))
            call.assert_not_called()

    def test_result_download_uses_https_without_provider_credentials(self):
        with patch.object(artwork, "http", return_value=self.returned) as call:
            data = artwork.standard_image({"data": [{"url": "https://images.example/result.png"}]}, 30)
        self.assertEqual(data, self.returned)
        self.assertEqual(call.call_args.args[0].headers, {})
        with patch.object(artwork, "http") as call:
            with self.assertRaisesRegex(artwork.AdapterError, "HTTPS"):
                artwork.standard_image({"data": [{"url": "http://images.example/result.png"}]}, 30)
            call.assert_not_called()

    def test_opaque_empty_and_corrupt_results_are_not_published(self):
        cases = [(png_bytes(Image.new("RGB", (12, 12), "red")), "opaque image"),
                 (png_bytes(Image.new("RGBA", (12, 12), (0, 0, 0, 0))), "empty transparent"),
                 (b"not an image", None)]
        for index, (data, message) in enumerate(cases):
            request = self.request(filename=f"bad-{index}.png")
            with self.subTest(index=index), patch.object(artwork, "http", return_value=json.dumps(image_response(data)).encode()):
                if message:
                    with self.assertRaisesRegex(artwork.AdapterError, message):
                        artwork.edit(request)
                else:
                    with self.assertRaises(UnidentifiedImageError):
                        artwork.edit(request)
            self.assertFalse(Path(request["output"]).exists())
            self.assertFalse(Path(request["output"] + ".edit.json").exists())

    def test_opaque_result_is_allowed_for_a_flat_master(self):
        data = png_bytes(Image.new("RGB", (12, 12), "red"))
        with patch.object(artwork, "http", return_value=json.dumps(image_response(data)).encode()):
            result = artwork.edit(self.request(require_transparency=False))
        with Image.open(result["output"]) as image:
            self.assertEqual(image.getchannel("A").getextrema(), (255, 255))

    def test_provider_color_profiles_and_exif_orientation_survive_png_normalization(self):
        srgb = ImageCms.ImageCmsProfile(io.BytesIO(self.profile))
        lab_profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("LAB"))
        rgb = Image.new("RGB", (24, 16), (220, 40, 60))
        lab = ImageCms.profileToProfile(rgb, srgb, lab_profile, outputMode="LAB")
        buffer = io.BytesIO()
        lab.save(buffer, format="TIFF", icc_profile=lab_profile.tobytes())
        with patch.object(artwork, "http", return_value=json.dumps(image_response(buffer.getvalue())).encode()):
            result = artwork.edit(self.request(filename="profiled.png", require_transparency=False))
        with Image.open(result["output"]) as image:
            profile = ImageCms.ImageCmsProfile(io.BytesIO(image.info["icc_profile"]))
            self.assertIn("sRGB", ImageCms.getProfileDescription(profile))
            self.assertEqual(image.getchannel("A").getextrema(), (255, 255))
            for actual, expected in zip(image.getpixel((0, 0))[:3], (220, 40, 60)):
                self.assertLessEqual(abs(actual - expected), 3)
        exif = Image.Exif()
        exif[274] = 6
        buffer = io.BytesIO()
        rgb.save(buffer, format="JPEG", exif=exif, icc_profile=self.profile)
        with patch.object(artwork, "http", return_value=json.dumps(image_response(buffer.getvalue())).encode()):
            result = artwork.edit(self.request(filename="oriented.png", require_transparency=False))
        with Image.open(result["output"]) as image:
            self.assertEqual(image.size, (16, 24))
            self.assertEqual(image.info["icc_profile"], self.profile)

    def test_invalid_requests_and_collisions_fail_before_network(self):
        cases = [{"images": []}, {"model": ""}, {"options": {"model": "override"}},
                 {"options": {"API_KEY": "secret"}}, {"options": {"n": 3}},
                 {"options": {"stream": True}}, {"require_transparency": "yes"}]
        with patch.object(artwork, "http") as call:
            for changes in cases:
                with self.subTest(changes=changes), self.assertRaises(artwork.AdapterError):
                    artwork.edit(self.request(**changes))
            output = self.root / "candidate.png"
            output.write_bytes(b"existing")
            with self.assertRaisesRegex(artwork.AdapterError, "already exists"):
                artwork.edit(self.request())
            self.assertEqual(output.read_bytes(), b"existing")
            report = self.root / "report-only.png.edit.json"
            report.write_text("existing report")
            with self.assertRaisesRegex(artwork.AdapterError, "already exists"):
                artwork.edit(self.request(filename="report-only.png"))
            self.assertEqual(report.read_text(), "existing report")
            call.assert_not_called()

    def test_missing_key_and_provider_failure_do_not_fallback_or_retry(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}), patch.object(artwork, "http") as call:
            with self.assertRaisesRegex(artwork.AdapterError, "Missing OPENAI_API_KEY"):
                artwork.edit(self.request())
            call.assert_not_called()
        with patch.object(artwork.GPTImageAdapter, "edit", side_effect=artwork.AdapterError("Provider failed")) as selected, \
                patch.object(artwork.GeminiAdapter, "edit") as gemini, patch.object(artwork.GrokAdapter, "edit") as grok:
            with self.assertRaisesRegex(artwork.AdapterError, "Provider failed"):
                artwork.edit(self.request())
            self.assertEqual(selected.call_count, 1)
            gemini.assert_not_called()
            grok.assert_not_called()
        self.assertFalse((self.root / "candidate.png").exists())

    def test_http_errors_do_not_echo_response_secrets(self):
        error = urllib.error.HTTPError("https://provider.example/private?key=secret", 401,
                                       "secret response", {}, io.BytesIO(b"secret body"))
        with patch.object(urllib.request, "urlopen", side_effect=error):
            with self.assertRaises(artwork.AdapterError) as caught:
                artwork.http(urllib.request.Request("https://provider.example/edit"), 30)
        self.assertIn("HTTP 401", str(caught.exception))
        self.assertNotIn("secret", str(caught.exception))

    def custom_config(self, code=None, **cap_changes):
        bridge = self.root / "bridge.py"
        bridge.write_text(code or '''import json
from pathlib import Path
import sys
request = json.load(sys.stdin)
assert all(Path(path).is_absolute() for path in request["images"])
output = Path(request["output"])
output.write_bytes(Path(request["images"][0]).read_bytes())
(Path(request["images"][0]).parent / "bridge-request.json").write_text(json.dumps(request))
print(json.dumps({"output": str(output)}))
''')
        path = self.root / "adapter.json"
        path.write_text(json.dumps({"id": "custom-provider", "command": [sys.executable, str(bridge)],
                                    "capabilities": {"reference_edit": True, "max_reference_images": 2,
                                                     "transparent_output": True, **cap_changes},
                                    "required_env": []}))
        return artwork.load_custom(path)

    def test_custom_bridge_receives_shared_request_and_stages_before_publication(self):
        request = self.request("custom-provider")
        result = artwork.edit(request, custom=self.custom_config())
        evidence = self.assert_candidate(result)
        received = json.loads((self.root / "bridge-request.json").read_text())
        self.assertEqual(received["images"], [str(self.source.resolve())])
        self.assertEqual(received["model"], request["model"])
        self.assertEqual(received["prompt"], request["prompt"])
        self.assertNotEqual(received["output"], request["output"])
        self.assertFalse(Path(received["output"]).exists())
        self.assertEqual(evidence["transport"], "custom-command")

    def test_custom_capabilities_and_failed_command_leave_final_path_free(self):
        with patch.object(artwork.subprocess, "run") as call:
            with self.assertRaisesRegex(artwork.AdapterError, "transparent_output"):
                artwork.edit(self.request("custom-provider"), self.custom_config(transparent_output=False))
            with self.assertRaisesRegex(artwork.AdapterError, "adapter limit"):
                artwork.edit(self.request("custom-provider", images=[str(self.source)] * 3), self.custom_config())
            call.assert_not_called()
        config = self.custom_config('import sys\nprint("secret stdout")\nprint("secret stderr", file=sys.stderr)\nsys.exit(7)\n')
        with self.assertRaises(artwork.AdapterError) as caught:
            artwork.edit(self.request("custom-provider"), config)
        self.assertIn("exited 7", str(caught.exception))
        self.assertNotIn("secret", str(caught.exception))
        self.assertFalse((self.root / "candidate.png").exists())
        self.assertFalse((self.root / "candidate.png.edit.json").exists())

    def test_custom_transparency_declaration_is_checked_against_actual_pixels(self):
        config = self.custom_config('''import json
from PIL import Image
import sys
request = json.load(sys.stdin)
Image.new("RGB", (16, 16), "red").save(request["output"])
print(json.dumps({"output": request["output"]}))
''')
        with self.assertRaisesRegex(artwork.AdapterError, "opaque image"):
            artwork.edit(self.request("custom-provider"), config)
        self.assertFalse((self.root / "candidate.png").exists())

    def test_check_reports_presence_without_exposing_credentials_or_calling_apis(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "edit_artwork.py"), "--check"],
                                capture_output=True, text=True, check=True)
        status = {row["provider"]: row for row in json.loads(result.stdout)}
        self.assertEqual(set(status), {"gpt-image", "gemini", "grok"})
        for row in status.values():
            self.assertTrue(row["credential_present"])
            self.assertEqual(row["model_access"], "not-checked")
        for secret in self.keys.values():
            self.assertNotIn(secret, result.stdout + result.stderr)

    def test_provider_report_is_matched_and_retained_in_the_platform_bundle(self):
        with patch.object(artwork, "http", return_value=json.dumps(image_response(self.returned)).encode()):
            edited = artwork.edit(self.request())
        flat = self.root / "original-flat.png"
        flat.write_bytes(png_bytes(Image.new("RGB", (512, 512), "#183153")))
        args = icons.build_parser().parse_args([
            "export", "--source", str(flat), "--source-kind", "flat-icon",
            "--foreground", edited["output"], "--background", "#183153",
            "--platforms", "android", "--out", str(self.root / "bundle"),
            "--artwork-report", edited["report"],
        ])
        icons.export_bundle(args)
        bundle = self.root / "bundle"
        self.assertEqual((bundle / "artwork-edit.json").read_bytes(), Path(edited["report"]).read_bytes())
        report = json.loads((bundle / "asset-report.json").read_text())
        self.assertEqual(report["artwork_edit"], {"provider": "gpt-image", "model": "chosen-image-edit-model",
                         "sha256": edited["sha256"], "input_roles": ["foreground"], "bundle_copy": "artwork-edit.json"})
        self.assertEqual((bundle / "sources/foreground.png").read_bytes(), Path(edited["output"]).read_bytes())
        self.assertEqual(report["checks"]["structural"], "passed")
        self.assertEqual(report["checks"]["visual"], "pending")

    def test_unrelated_artwork_report_cannot_be_attached_to_an_export(self):
        report_path = self.root / "unrelated.edit.json"
        report_path.write_text(json.dumps({"provider": "gemini", "model": "chosen-model", "sha256": "0" * 64}))
        args = icons.build_parser().parse_args([
            "export", "--source", str(self.source), "--source-kind", "logo",
            "--background", "#183153", "--platforms", "web", "--out", str(self.root / "bundle"),
            "--artwork-report", str(report_path),
        ])
        with self.assertRaisesRegex(ValueError, "hash must match"):
            icons.export_bundle(args)
        self.assertFalse((self.root / "bundle").exists())


if __name__ == "__main__":
    unittest.main()
