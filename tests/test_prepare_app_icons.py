"""Behavioral checks for icon geometry, packaging, and preservation of source artwork."""

import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from PIL import Image, ImageCms, ImageDraw


SCRIPT = Path(__file__).resolve().parents[1] / "skills/prepare-app-icons/scripts/export_icons.py"
SPEC = importlib.util.spec_from_file_location("export_icons", SCRIPT)
icons = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(icons)


class IconExportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.logo = self.root / "logo.png"
        image = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        # A fully opaque rectangular mark inside transparent source padding.
        ImageDraw.Draw(image).rectangle((128, 168, 383, 343), fill=(220, 40, 60, 255))
        image.save(self.logo)

    def args(self, out="output", *extra):
        return icons.build_parser().parse_args([
            "export", "--source", str(self.logo), "--source-kind", "logo",
            "--background", "#183153", "--out", str(self.root / out), *extra,
        ])

    def read_report(self, out="output"):
        return json.loads((self.root / out / "asset-report.json").read_text())

    def assert_pixels_in_circle(self, image, radius):
        alpha = image.convert("RGBA").getchannel("A")
        for index, value in enumerate(alpha.getdata()):
            if value:
                x, y = index % image.width, index // image.width
                distance = math.hypot(x + 0.5 - image.width / 2, y + 0.5 - image.height / 2)
                self.assertLessEqual(distance, radius)

    def test_complete_bundle_has_correct_files_and_preserves_inputs(self):
        original = self.logo.read_bytes()
        icons.export_bundle(self.args("output", "--pwa", "--play-store", "--monochrome-from-alpha"))
        self.assertEqual(self.logo.read_bytes(), original)
        output = self.root / "output"
        self.assertEqual((output / "sources/source.png").read_bytes(), original)
        with Image.open(output / "apple/AppIcon.appiconset/AppIcon-1024.png") as image:
            self.assertEqual((image.format, image.mode, image.size), ("PNG", "RGB", (1024, 1024)))
            self.assertEqual(image.getpixel((0, 0)), (24, 49, 83))
            self.assertEqual(image.getpixel((512, 512)), (220, 40, 60))
            profile = ImageCms.ImageCmsProfile(io.BytesIO(image.info["icc_profile"]))
            self.assertIn("sRGB", ImageCms.getProfileDescription(profile))
        with Image.open(output / "apple/icon-composer-layers/01-foreground.png") as foreground:
            self.assertEqual(foreground.getpixel((0, 0))[3], 0)
        with Image.open(output / "android/play-store-icon.png") as listing:
            self.assertEqual((listing.mode, listing.size), ("RGBA", (512, 512)))
            self.assertEqual(listing.getchannel("A").getextrema(), (255, 255))
            self.assertLessEqual((output / "android/play-store-icon.png").stat().st_size, 1024 * 1024)
        report = self.read_report()
        self.assertEqual(report["inputs"]["source"]["sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(report["guidelines"]["status"], "pending")
        self.assertEqual(report["checks"]["visual"], "pending")
        for entry in report["files"]:
            self.assertTrue((output / entry["path"]).is_file())

    def test_android_densities_safe_contours_and_api_fallbacks(self):
        icons.export_bundle(self.args("output", "--platforms", "android", "--monochrome-from-alpha"))
        resources = self.root / "output/android/res"
        widths_dp = []
        for density, side, legacy_side in (("mdpi", 108, 48), ("hdpi", 162, 72),
                                          ("xhdpi", 216, 96), ("xxhdpi", 324, 144),
                                          ("xxxhdpi", 432, 192)):
            with Image.open(resources / f"drawable-{density}/ic_launcher_foreground.png") as image:
                self.assertEqual(image.size, (side, side))
                self.assertEqual(image.getpixel((0, 0))[3], 0)
                self.assert_pixels_in_circle(image, side * 33 / 108)
                bounds = image.getchannel("A").point(lambda alpha: 255 if alpha >= 128 else 0).getbbox()
                widths_dp.append((bounds[2] - bounds[0]) * 108 / side)
            with Image.open(resources / f"mipmap-{density}/ic_launcher.png") as legacy:
                self.assertEqual(legacy.size, (legacy_side, legacy_side))
            with Image.open(resources / f"drawable-{density}/ic_launcher_monochrome.png") as mono:
                self.assert_pixels_in_circle(mono, side * 33 / 108)
                self.assertEqual(mono.getpixel((side // 2, side // 2)), (255, 255, 255, 255))
        self.assertLess(max(widths_dp) - min(widths_dp), 2)
        v26 = ET.parse(resources / "mipmap-anydpi-v26/ic_launcher.xml").getroot()
        v33 = ET.parse(resources / "mipmap-anydpi-v33/ic_launcher.xml").getroot()
        self.assertEqual([node.tag for node in v26], ["background", "foreground"])
        self.assertEqual([node.tag for node in v33], ["background", "foreground", "monochrome"])
        for shape in ("circle", "squircle", "rounded"):
            layer = Image.open(resources / "drawable-xxxhdpi/ic_launcher_foreground.png")
            viewport = layer.crop((72, 72, 360, 360))
            preview = icons.masked_preview(viewport, shape, 288)
            self.assertEqual(preview.getpixel((144, 144))[:3], (220, 40, 60))
            layer.close()

    def test_web_icons_ico_resolutions_and_pwa_manifest(self):
        icons.export_bundle(self.args("output", "--platforms", "web", "--pwa"))
        web = self.root / "output/web"
        with Image.open(web / "favicon.ico") as ico:
            self.assertEqual(ico.ico.sizes(), {(16, 16), (32, 32), (48, 48)})
            for side in (16, 32, 48):
                with Image.open(web / f"favicon-{side}.png") as png:
                    self.assertEqual(ico.ico.getimage((side, side)).tobytes(), png.tobytes())
        with Image.open(web / "apple-touch-icon.png") as touch:
            self.assertEqual((touch.size, touch.mode), ((180, 180), "RGB"))
        manifest = json.loads((web / "manifest-icons.json").read_text())
        self.assertEqual(len(manifest["icons"]), 4)
        for entry in manifest["icons"]:
            with Image.open(web / entry["src"]) as image:
                self.assertEqual(entry["sizes"], f"{image.width}x{image.height}")
                self.assertEqual(image.convert("RGBA").getchannel("A").getextrema(), (255, 255))
        # Check maskable geometry before composition obscures foreground alpha.
        logo, _ = icons.load_image(self.logo)
        for side in (192, 512):
            layer, _ = icons.centered(logo, side, radius=side * 0.4)
            self.assert_pixels_in_circle(layer, side * 0.4)

    def test_flat_icon_remains_full_bleed_and_requires_separate_android_mark(self):
        flat = self.root / "flat.png"
        image = Image.new("RGB", (1024, 1024), "#2468ac")
        image.putpixel((0, 0), (10, 20, 30))
        image.save(flat)
        args = self.args("output", "--source", str(flat), "--source-kind", "flat-icon",
                         "--platforms", "apple", "web")
        icons.export_bundle(args)
        with Image.open(self.root / "output/apple/AppIcon.appiconset/AppIcon-1024.png") as exported:
            self.assertEqual(exported.tobytes(), image.tobytes())
        self.assertFalse((self.root / "output/apple/icon-composer-layers").exists())
        android = self.args("android", "--source", str(flat), "--source-kind", "flat-icon",
                            "--platforms", "android")
        with self.assertRaisesRegex(ValueError, "transparent mark"):
            icons.export_bundle(android)
        self.assertFalse((self.root / "android").exists())
        android.foreground = str(self.logo)
        icons.export_bundle(android)
        self.assertTrue((self.root / "android/android/res/mipmap-anydpi-v26/ic_launcher.xml").exists())

    def test_existing_output_directory_is_never_replaced(self):
        out = self.root / "output"
        out.mkdir()
        sentinel = out / "sentinel.txt"
        sentinel.write_text("existing artwork")
        with self.assertRaisesRegex(ValueError, "refusing to replace"):
            icons.export_bundle(self.args())
        self.assertEqual(sentinel.read_text(), "existing artwork")
        self.assertEqual(list(out.iterdir()), [sentinel])

    def test_invalid_or_empty_sources_fail_without_publishing_output(self):
        invalid = self.root / "invalid.png"
        Image.new("RGBA", (30, 30), (0, 0, 0, 0)).save(invalid)
        with self.assertRaisesRegex(ValueError, "no visible artwork"):
            icons.export_bundle(self.args("output", "--source", str(invalid)))
        self.assertFalse((self.root / "output").exists())
        with self.assertRaisesRegex(ValueError, "#RRGGBB"):
            icons.export_bundle(self.args("output", "--background", "transparent"))
        self.assertFalse((self.root / "output").exists())

    def test_guidelines_are_preserved_and_incomplete_verification_is_rejected(self):
        path = self.root / "guidelines.json"
        record = {"checked_at": "2026-10-10", "status": "verified",
                  "platforms": {"apple": {"urls": ["https://developer.apple.com/design/human-interface-guidelines/app-icons"]}}}
        path.write_text(json.dumps(record, indent=4) + "\n")
        args = self.args("output", "--guidelines", str(path))
        with self.assertRaisesRegex(ValueError, "missing platforms"):
            icons.export_bundle(args)
        self.assertFalse((self.root / "output").exists())
        args.platforms = ["apple"]
        icons.export_bundle(args)
        self.assertEqual((self.root / "output/guideline-check.json").read_bytes(), path.read_bytes())
        self.assertEqual(self.read_report()["guidelines"], record)

    def test_color_profile_conversion_and_invalid_profiles(self):
        profiled = self.root / "profiled.png"
        image = Image.open(self.logo)
        image.save(profiled, icc_profile=ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes())
        converted, info = icons.load_image(profiled)
        self.assertEqual(converted.tobytes(), image.tobytes())
        self.assertEqual(info["color_handling"], "converted-to-sRGB")
        lab_profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("LAB"))
        rgb_profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
        original_rgb = Image.new("RGB", (64, 64), (220, 40, 60))
        lab = ImageCms.profileToProfile(original_rgb, rgb_profile, lab_profile, outputMode="LAB")
        lab_file = self.root / "lab.tiff"
        lab.save(lab_file, icc_profile=lab_profile.tobytes())
        lab_converted, lab_info = icons.load_image(lab_file)
        self.assertEqual(lab_info["original_mode"], "LAB")
        self.assertEqual(lab_converted.getchannel("A").getextrema(), (255, 255))
        for actual, expected in zip(lab_converted.getpixel((0, 0))[:3], (220, 40, 60)):
            self.assertLessEqual(abs(actual - expected), 3)
        broken = self.root / "broken.png"
        image.save(broken, icc_profile=b"invalid profile")
        image.close()
        with self.assertRaisesRegex(ValueError, "embedded profile"):
            icons.load_image(broken)

    def test_safe_fit_keeps_aspect_ratio_with_asymmetric_sparse_contours(self):
        source = Image.new("RGBA", (900, 500), (0, 0, 0, 0))
        draw = ImageDraw.Draw(source)
        draw.ellipse((0, 0, 130, 180), fill="red")
        draw.rectangle((80, 150, 899, 499), fill="red")
        for side in (108, 162, 216, 324, 432):
            layer, factor = icons.centered(source, side, radius=side * 33 / 108)
            self.assert_pixels_in_circle(layer, side * 33 / 108)
            bounds = layer.getchannel("A").getbbox()
            expected_width = math.floor(900 * factor)
            expected_height = math.floor(500 * factor)
            self.assertLessEqual(abs((bounds[2] - bounds[0]) - expected_width), 2)
            self.assertLessEqual(abs((bounds[3] - bounds[1]) - expected_height), 2)

    def test_cli_inspection_explains_actual_visible_bounds(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "inspect", str(self.logo)],
                                capture_output=True, text=True, check=True)
        inspected = json.loads(result.stdout)
        self.assertEqual(inspected["size"], [512, 512])
        self.assertEqual(inspected["visible_bounds"], [128, 168, 384, 344])
        self.assertEqual(inspected["alpha_extrema"], [0, 255])


if __name__ == "__main__":
    unittest.main()
