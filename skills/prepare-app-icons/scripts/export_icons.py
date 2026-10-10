#!/usr/bin/env python3
"""Export existing raster artwork into platform-specific icon bundles.

Defaults reflect the 2026-10-10 guideline snapshot in the skill references.
This helper performs structural checks; visual and native rendering need review.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

try:
    from PIL import Image, ImageCms, ImageDraw, ImageFont, ImageOps
except ImportError as exc:
    raise SystemExit("Install Pillow with ImageCms support in your Python environment.") from exc


SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
SRGB_BYTES = SRGB.tobytes()
ANDROID_DENSITIES = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
ANDROID_CANVAS_DP = 108
ANDROID_SAFE_DIAMETER_DP = 66
ANDROID_VIEWPORT_DP = 72
ANDROID_INSET_DP = (ANDROID_CANVAS_DP - ANDROID_VIEWPORT_DP) / 2


def load_image(path):
    path = Path(path)
    if path.suffix.lower() in {".svg", ".pdf"}:
        raise ValueError("Rasterize the vector with a native renderer first; retain the original.")
    with Image.open(path) as opened:
        if getattr(opened, "n_frames", 1) != 1:
            raise ValueError(f"Choose a still source image: {path}")
        original_mode = opened.mode
        original_format = opened.format
        image = ImageOps.exif_transpose(opened)
        profile = image.info.get("icc_profile")
        if profile:
            try:
                color = image if image.mode in {"RGB", "CMYK", "LAB", "L"} else image.convert("RGB")
                rgb = ImageCms.profileToProfile(
                    color, ImageCms.ImageCmsProfile(io.BytesIO(profile)), SRGB, outputMode="RGB"
                )
            except (OSError, ValueError, ImageCms.PyCMSError) as exc:
                raise ValueError(f"Cannot convert the embedded profile to sRGB: {path}") from exc
            rgba = rgb.convert("RGBA")
            if image.mode in {"RGBA", "LA", "PA"}:
                rgba.putalpha(image.getchannel("A"))
            elif "transparency" in image.info:
                rgba.putalpha(image.convert("RGBA").getchannel("A"))
        elif original_mode in {"CMYK", "LAB"}:
            raise ValueError(f"Provide a color profile or an sRGB export for {original_mode} input: {path}")
        else:
            rgba = image.convert("RGBA")
        rgba.load()
    alpha = rgba.getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError(f"Source has no visible artwork: {path}")
    info = {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "format": original_format,
        "original_mode": original_mode,
        "size": list(rgba.size),
        "visible_bounds": list(bounds),
        "alpha_extrema": list(alpha.getextrema()),
        "color_handling": "converted-to-sRGB" if profile else "assumed-sRGB-unprofiled-input",
    }
    return rgba, info


def trim_alpha(image):
    """Remove only fully transparent outer padding, retaining antialiased edges."""
    bounds = image.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError("Source has no visible artwork.")
    return image.crop(bounds)


def resize(image, size):
    # Premultiplied alpha avoids dark or colored fringes around transparent edges.
    return image.convert("RGBa").resize(size, Image.Resampling.LANCZOS).convert("RGBA")


def centered(image, side, fraction=1.0, radius=None, margin=4):
    """Fit visible artwork uniformly in a square, or conservatively in a circle."""
    image = trim_alpha(image)
    factor = side * fraction / max(image.size)
    if radius is not None:
        cx, cy = image.width / 2, image.height / 2
        extent = 0.0
        alpha = image.getchannel("A")
        # Row extrema bound every visible pixel's entire footprint, including corners.
        for y in range(image.height):
            bounds = alpha.crop((0, y, image.width, y + 1)).getbbox()
            if bounds:
                dx = max(abs(bounds[0] - cx), abs(bounds[2] - cx))
                dy = max(abs(y - cy), abs(y + 1 - cy))
                extent = max(extent, math.hypot(dx, dy))
        # Allow for filter support and integer centering without clipping the artwork.
        factor = min(factor, max(0.1, radius - margin) / extent)
    new_size = tuple(max(1, math.floor(edge * factor)) for edge in image.size)
    scaled = resize(image, new_size)
    layer = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    layer.alpha_composite(scaled, ((side - scaled.width) // 2, (side - scaled.height) // 2))
    return layer, factor


def flatten(layer, color):
    background = Image.new("RGBA", layer.size, (*color, 255))
    background.alpha_composite(layer)
    return background.convert("RGB")


def outside_circle(image, radius):
    alpha = image.convert("RGBA").getchannel("A")
    cx, cy = image.width / 2, image.height / 2
    for y in range(image.height):
        bounds = alpha.crop((0, y, image.width, y + 1)).getbbox()
        if bounds:
            dx = max(abs(bounds[0] - cx), abs(bounds[2] - cx))
            dy = max(abs(y - cy), abs(y + 1 - cy))
            if math.hypot(dx, dy) > radius + 1e-6:
                return True
    return False


def save_png(root, relative, image, files, opaque=False, radius=None, max_bytes=None):
    if opaque and image.convert("RGBA").getchannel("A").getextrema() != (255, 255):
        raise ValueError(f"Expected opaque output: {relative}")
    if radius is not None and outside_circle(image, radius):
        raise ValueError(f"Artwork exceeds circular safe zone: {relative}")
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", icc_profile=SRGB_BYTES, optimize=True)
    if max_bytes is not None and path.stat().st_size > max_bytes:
        raise ValueError(f"File exceeds {max_bytes} bytes: {relative}")
    with Image.open(path) as checked:
        checked.load()
        if checked.size != image.size or checked.mode != image.mode or checked.format != "PNG":
            raise ValueError(f"Export round-trip failed: {relative}")
        if checked.info.get("icc_profile") != SRGB_BYTES:
            raise ValueError(f"sRGB profile missing: {relative}")
    files.append({"path": relative, "size": list(image.size), "mode": image.mode,
                  "format": "PNG", "bytes": path.stat().st_size, "sRGB": True,
                  "opaque": image.convert("RGBA").getchannel("A").getextrema() == (255, 255),
                  "safe_radius_px": radius})


def write_text(root, relative, value):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_json(root, relative, value):
    write_text(root, relative, json.dumps(value, indent=2) + "\n")


def check_metadata(root):
    catalog = root / "apple/AppIcon.appiconset/Contents.json"
    if catalog.exists():
        for entry in json.loads(catalog.read_text())["images"]:
            path = catalog.parent / entry["filename"]
            with Image.open(path) as icon:
                if f"{icon.width}x{icon.height}" != entry["size"]:
                    raise ValueError("Apple catalog size does not match its image.")
    android = root / "android/res"
    namespace = "{http://schemas.android.com/apk/res/android}"
    for path in android.glob("mipmap-anydpi-*/*.xml"):
        for child in ET.parse(path).getroot():
            reference = child.attrib[namespace + "drawable"]
            if reference.startswith("@drawable/"):
                name = reference.split("/", 1)[1]
                for density in ANDROID_DENSITIES:
                    if not (android / f"drawable-{density}/{name}.png").is_file():
                        raise ValueError(f"Missing Android resource: {reference} ({density})")
            elif reference.startswith("@color/"):
                name = reference.split("/", 1)[1]
                colors = [item.attrib.get("name") for item in ET.parse(
                    android / "values/ic_launcher_background.xml"
                ).getroot()]
                if name not in colors:
                    raise ValueError(f"Missing Android color: {reference}")
    class Links(HTMLParser):
        def handle_starttag(self, tag, attrs):
            values = dict(attrs)
            if tag == "link" and not (root / "web" / values["href"].lstrip("/")).is_file():
                raise ValueError(f"Missing web icon: {values['href']}")
    head = root / "web/head.html"
    if head.exists():
        Links().feed(head.read_text())
    manifest = root / "web/manifest-icons.json"
    if manifest.exists():
        for entry in json.loads(manifest.read_text())["icons"]:
            with Image.open(manifest.parent / entry["src"]) as icon:
                if entry["sizes"] != f"{icon.width}x{icon.height}" or icon.format != "PNG":
                    raise ValueError("Manifest metadata does not match its icon.")


def masked_preview(image, shape, side=160):
    """Approximate visual masks only; these never become platform exports."""
    image = resize(image.convert("RGBA"), (side, side))
    mask = Image.new("L", (side, side), 0)
    if shape == "squircle":
        pixels = mask.load()
        for y in range(side):
            for x in range(side):
                if abs((x + 0.5 - side / 2) / (side / 2)) ** 4 + abs(
                    (y + 0.5 - side / 2) / (side / 2)
                ) ** 4 <= 1:
                    pixels[x, y] = 255
    else:
        draw = ImageDraw.Draw(mask)
        if shape == "circle":
            draw.ellipse((0, 0, side - 1, side - 1), fill=255)
        else:
            draw.rounded_rectangle((0, 0, side - 1, side - 1), radius=side * 0.22, fill=255)
    image.putalpha(mask)
    return image


def create_preview(root, panels, favicons, files):
    rows = math.ceil(len(panels) / 4)
    sheet = Image.new("RGB", (880, rows * 215 + (180 if favicons else 0)), "#eeeeee")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, (label, image) in enumerate(panels):
        x, y = (index % 4) * 220 + 25, (index // 4) * 215 + 10
        draw.text((x, y), label, fill="black", font=font)
        sheet.paste(image, (x, y + 25), image)
    if favicons:
        top = rows * 215
        for index, (size, icon) in enumerate((item for item in favicons.items() if item[0] <= 48)):
            x = index * 210 + 25
            draw.text((x, top + 5), f"Favicon {size}px (actual size)", fill="black", font=font)
            for y, background in ((top + 25, "white"), (top + 95, "#202020")):
                draw.rectangle((x, y, x + 100, y + 60), fill=background)
                sheet.paste(icon, (x + 5, y + 5), icon)
    save_png(root, "preview.png", sheet, files, opaque=True)


def adaptive_xml(monochrome=False):
    mono = '    <monochrome android:drawable="@drawable/ic_launcher_monochrome" />\n' if monochrome else ""
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
            '    <background android:drawable="@color/ic_launcher_background" />\n'
            '    <foreground android:drawable="@drawable/ic_launcher_foreground" />\n'
            f'{mono}</adaptive-icon>\n')


def export_bundle(args):
    out = Path(args.out)
    if out.exists() or out.is_symlink():
        raise ValueError(f"Use a new output directory; refusing to replace {out}")
    if args.pwa and "web" not in args.platforms:
        raise ValueError("--pwa requires web in --platforms.")
    if args.play_store and "android" not in args.platforms:
        raise ValueError("--play-store requires android in --platforms.")
    for name in ("apple_scale", "favicon_scale"):
        if not 0 < getattr(args, name) <= 1:
            raise ValueError(f"--{name.replace('_', '-')} must be greater than 0 and at most 1.")
    color = None
    if args.background:
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", args.background):
            raise ValueError("--background must be an opaque #RRGGBB color.")
        color = tuple(int(args.background[i:i + 2], 16) for i in (1, 3, 5))
    source, source_info = load_image(args.source)
    inputs = {"source": source_info}
    if args.source_kind == "flat-icon":
        if source.width != source.height or source.getchannel("A").getextrema() != (255, 255):
            raise ValueError("A flat-icon must be an opaque unmasked square. Supply original artwork for masked icons.")
        logo = None
        separable_logo = False
    else:
        logo = trim_alpha(source)
        separable_logo = source_info["alpha_extrema"][0] < 255
    if args.foreground:
        logo, inputs["foreground"] = load_image(args.foreground)
        logo = trim_alpha(logo)
        separable_logo = inputs["foreground"]["alpha_extrema"][0] < 255
    needs_logo = "android" in args.platforms or args.pwa
    if needs_logo and not separable_logo:
        raise ValueError("Android/PWA needs a separable transparent mark. Provide --foreground, or export Apple/web alone.")
    if color is None and (args.source_kind == "logo" or needs_logo):
        raise ValueError("Choose an opaque brand background and pass --background '#RRGGBB'.")
    favicon_source = source
    if args.favicon_source:
        favicon_source, inputs["favicon_source"] = load_image(args.favicon_source)
    monochrome = None
    if args.monochrome_source or args.monochrome_from_alpha:
        if "android" not in args.platforms:
            raise ValueError("Monochrome options require android in --platforms.")
        mono_source = logo
        if args.monochrome_source:
            mono_source, inputs["monochrome_source"] = load_image(args.monochrome_source)
            if mono_source.getchannel("A").getextrema()[0] == 255:
                raise ValueError("Monochrome source must have transparent surroundings, not an opaque tile.")
        monochrome = Image.new("RGBA", mono_source.size, "white")
        monochrome.putalpha(mono_source.getchannel("A"))
    artwork_bytes = None
    artwork_edit = None
    if args.artwork_report:
        artwork_bytes = Path(args.artwork_report).read_bytes()
        evidence = json.loads(artwork_bytes)
        if not isinstance(evidence, dict):
            raise ValueError("Artwork report must be a JSON object.")
        for field in ("provider", "model"):
            if not isinstance(evidence.get(field), str) or not evidence[field].strip():
                raise ValueError(f"Artwork report requires a nonempty {field}.")
        digest = evidence.get("sha256")
        roles = [role for role, info in inputs.items() if info["sha256"] == digest]
        if not roles:
            raise ValueError("Artwork report output hash must match a supplied raster input.")
        artwork_edit = {"provider": evidence["provider"], "model": evidence["model"],
                        "sha256": digest, "input_roles": roles, "bundle_copy": "artwork-edit.json"}
    guideline_bytes = None
    guidelines = {"status": "pending", "reason": "The exporter does not check current online guidance."}
    if args.guidelines:
        guideline_bytes = Path(args.guidelines).read_bytes()
        guidelines = json.loads(guideline_bytes)
        if not isinstance(guidelines, dict):
            raise ValueError("Guideline record must be a JSON object.")
        if guidelines.get("status") not in {"verified", "partial", "offline"}:
            raise ValueError("Guideline record status must be verified, partial, or offline.")
        if not guidelines.get("checked_at"):
            raise ValueError("Guideline record needs the actual checked_at date.")
        if guidelines["status"] == "verified":
            missing = set(args.platforms) - set(guidelines.get("platforms", {}))
            if missing:
                raise ValueError("Verified guideline record is missing platforms: " + ", ".join(sorted(missing)))

    warnings = []
    files, panels, favicons = [], [], {}
    def note_scale(label, factor):
        if factor > 1:
            warnings.append(f"{label} upscales raster artwork {factor:.2f}x; prefer a higher-resolution/vector source.")

    if args.source_kind == "flat-icon":
        master = resize(source, (1024, 1024)).convert("RGB")
        note_scale("Flat master", 1024 / source.width)
    else:
        master_layer, factor = centered(logo, 1024, args.apple_scale)
        master = flatten(master_layer, color)
        note_scale("Flat master", factor)

    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".app-icons-", dir=out.parent) as temporary:
        root = Path(temporary) / "bundle"
        root.mkdir()
        if "apple" in args.platforms:
            relative = "apple/AppIcon.appiconset/AppIcon-1024.png"
            save_png(root, relative, master, files, opaque=True)
            write_json(root, "apple/AppIcon.appiconset/Contents.json", {
                "images": [{"filename": "AppIcon-1024.png", "idiom": "universal",
                            "platform": "ios", "size": "1024x1024"}],
                "info": {"author": "xcode", "version": 1},
            })
            if separable_logo:
                layer, factor = centered(logo, 1024, args.apple_scale)
                save_png(root, "apple/icon-composer-layers/01-foreground.png", layer, files)
                write_text(root, "apple/icon-composer-layers/setup.txt",
                           f"Import the 1024px foreground into Icon Composer. Set background {args.background or 'from the original icon'}.\n"
                           "This folder is a foreground handoff, not a native .icon file.\n"
                           "Review default, dark, clear and tinted appearances, then save and test the native icon through Xcode.\n")
            warnings.append("Apple output is a default iOS/iPadOS catalog; Composer handoff and appearance variants need native review.")
            panels.append(("Apple (approximate mask)", masked_preview(master, "rounded")))

        if "android" in args.platforms:
            write_text(root, "android/res/values/ic_launcher_background.xml",
                       '<?xml version="1.0" encoding="utf-8"?>\n'
                       f'<resources><color name="ic_launcher_background">{args.background}</color></resources>\n')
            write_text(root, "android/res/mipmap-anydpi-v26/ic_launcher.xml", adaptive_xml())
            write_text(root, "android/res/mipmap-anydpi-v26/ic_launcher_round.xml", adaptive_xml())
            if monochrome is not None:
                for name in ("ic_launcher", "ic_launcher_round"):
                    write_text(root, f"android/res/mipmap-anydpi-v33/{name}.xml", adaptive_xml(True))
                warnings.append("Review the monochrome alpha silhouette for lost internal detail; compileSdk 33+ is required.")
            else:
                warnings.append("No authored monochrome layer supplied; themed-icon behavior needs review.")
            largest_layer = None
            for density, multiplier in ANDROID_DENSITIES.items():
                side = int(ANDROID_CANVAS_DP * multiplier)
                radius = ANDROID_SAFE_DIAMETER_DP * multiplier / 2
                foreground, factor = centered(logo, side, radius=radius, margin=4 * multiplier)
                note_scale(f"Android {density}", factor)
                save_png(root, f"android/res/drawable-{density}/ic_launcher_foreground.png",
                         foreground, files, radius=radius)
                if monochrome is not None:
                    mono_layer, mono_factor = centered(monochrome, side, radius=radius, margin=4 * multiplier)
                    note_scale(f"Android monochrome {density}", mono_factor)
                    save_png(root, f"android/res/drawable-{density}/ic_launcher_monochrome.png",
                             mono_layer, files, radius=radius)
                composite = flatten(foreground, color).convert("RGBA")
                inset = int(ANDROID_INSET_DP * multiplier)
                viewport = composite.crop((inset, inset, side - inset, side - inset))
                legacy_side = int(48 * multiplier)
                save_png(root, f"android/res/mipmap-{density}/ic_launcher.png",
                         resize(viewport, (legacy_side, legacy_side)).convert("RGB"), files, opaque=True)
                save_png(root, f"android/res/mipmap-{density}/ic_launcher_round.png",
                         masked_preview(viewport, "circle", legacy_side), files)
                largest_layer = foreground
            write_text(root, "android/integration.txt",
                       'Merge res/ into the app resources and use android:icon="@mipmap/ic_launcher".\n'
                       'Use android:roundIcon="@mipmap/ic_launcher_round" only when the project expects it.\n'
                       "Keep the API 26 XML when adding API 33 monochrome resources. Test in an actual launcher.\n")
            combined = flatten(largest_layer, color).convert("RGBA")
            inset = int(ANDROID_INSET_DP * 4)
            viewport = combined.crop((inset, inset, combined.width - inset, combined.height - inset))
            for shape in ("circle", "squircle", "rounded"):
                panels.append((f"Android {shape} (72dp)", masked_preview(viewport, shape)))
            safe = combined.copy()
            guide = ImageDraw.Draw(safe)
            center, radius = safe.width / 2, ANDROID_SAFE_DIAMETER_DP * 4 / 2
            guide.ellipse((center - radius, center - radius, center + radius, center + radius),
                          outline="#ff5577", width=3)
            panels.append(("Android 108dp / 66dp circle", resize(safe, (160, 160))))
            if monochrome is not None:
                mono_layer, _ = centered(monochrome, 432, radius=132, margin=16)
                for label, background, tint in (("light", (211, 223, 244), (32, 54, 82)),
                                                ("dark", (40, 48, 70), (214, 227, 248))):
                    tinted = Image.new("RGBA", mono_layer.size, (*tint, 255))
                    tinted.putalpha(mono_layer.getchannel("A"))
                    theme = flatten(tinted, background).convert("RGBA").crop((72, 72, 360, 360))
                    panels.append((f"Themed {label} (candidate)", masked_preview(theme, "circle")))
            if args.play_store:
                save_png(root, "android/play-store-icon.png", resize(master.convert("RGBA"), (512, 512)),
                         files, opaque=True, max_bytes=1024 * 1024)

        if "web" in args.platforms:
            use_flat = args.source_kind == "flat-icon" and not args.favicon_source
            for side in (16, 32, 48, 96):
                if use_flat:
                    favicon = resize(favicon_source, (side, side))
                    factor = side / favicon_source.width
                else:
                    favicon, factor = centered(favicon_source, side, args.favicon_scale)
                note_scale(f"Favicon {side}px", factor)
                favicons[side] = favicon
                save_png(root, f"web/favicon-{side}.png", favicon, files)
            ico_path = root / "web/favicon.ico"
            favicons[48].save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)],
                              append_images=[favicons[16], favicons[32]])
            with Image.open(ico_path) as ico:
                sizes = sorted(ico.ico.sizes())
                if sizes != [(16, 16), (32, 32), (48, 48)]:
                    raise ValueError("ICO is missing expected image sizes.")
                for size in sizes:
                    ico.ico.getimage(size).load()
            files.append({"path": "web/favicon.ico", "format": "ICO", "sizes": sizes,
                          "bytes": ico_path.stat().st_size})
            save_png(root, "web/apple-touch-icon.png", resize(master.convert("RGBA"), (180, 180)).convert("RGB"),
                     files, opaque=True)
            write_text(root, "web/head.html",
                       '<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48" type="image/x-icon">\n'
                       '<link rel="icon" href="/favicon-96.png" sizes="96x96" type="image/png">\n'
                       '<link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">\n')
            if args.pwa:
                icons = []
                for side in (192, 512):
                    regular = resize(master.convert("RGBA"), (side, side)).convert("RGB")
                    layer, factor = centered(logo, side, radius=side * 0.4)
                    note_scale(f"PWA maskable {side}px", factor)
                    if outside_circle(layer, side * 0.4):
                        raise ValueError("PWA mark exceeds circular safe zone.")
                    maskable = flatten(layer, color)
                    for purpose, image in (("any", regular), ("maskable", maskable)):
                        filename = f"pwa-{purpose}-{side}.png"
                        save_png(root, f"web/{filename}", image, files, opaque=True)
                        icons.append({"src": filename, "sizes": f"{side}x{side}",
                                      "type": "image/png", "purpose": purpose})
                    if side == 512:
                        panels.append(("PWA maskable (80% circle)", masked_preview(maskable, "circle")))
                write_json(root, "web/manifest-icons.json", {"icons": icons})
            write_text(root, "web/integration.txt",
                       "Copy icon files to the public asset directory and adapt head.html to the site's base path or framework metadata.\n"
                       "Keep the Search favicon URL stable. Merge manifest-icons.json into an existing manifest only when PWA assets are requested.\n"
                       "The icons fragment is not a complete installable application manifest.\n")
        create_preview(root, panels, favicons, files)
        if guideline_bytes is not None:
            (root / "guideline-check.json").write_bytes(guideline_bytes)
        if artwork_bytes is not None:
            (root / "artwork-edit.json").write_bytes(artwork_bytes)
        for role, info in inputs.items():
            original = Path(info["path"])
            relative = f"sources/{role}{original.suffix.lower()}"
            target = root / relative
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(original, target)
            info["bundle_copy"] = relative
        check_metadata(root)
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "guideline_snapshot": "2026-10-10",
            "guidelines": guidelines,
            "artwork_edit": artwork_edit,
            "inputs": inputs,
            "platforms": args.platforms,
            "composition": {"source_kind": args.source_kind, "background": args.background,
                            "apple_scale": args.apple_scale, "favicon_scale": args.favicon_scale,
                            "android_canvas_dp": ANDROID_CANVAS_DP,
                            "android_viewport_dp": ANDROID_VIEWPORT_DP,
                            "android_safe_circle_diameter_dp": ANDROID_SAFE_DIAMETER_DP},
            "files": files,
            "warnings": warnings,
            "checks": {"structural": "passed", "visual": "pending", "native_rendering": "pending"},
        }
        write_json(root, "asset-report.json", report)
        root.rename(out)
    return {"output": str(out.resolve()), "image_files": len(files), "warnings": warnings,
            "structural_checks": "passed", "visual_review": "pending"}


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="Inspect source dimensions, visible bounds, alpha and color profile.")
    inspect.add_argument("source")
    export = commands.add_parser("export", help="Prepare icons in a new directory without modifying source files.")
    export.add_argument("--source", required=True)
    export.add_argument("--source-kind", choices=("logo", "flat-icon"), required=True)
    export.add_argument("--out", required=True)
    export.add_argument("--platforms", nargs="+", choices=("apple", "android", "web"), default=["apple", "android", "web"])
    export.add_argument("--background", help="Opaque brand background as #RRGGBB.")
    export.add_argument("--foreground", help="Separate transparent mark for a flat icon, or an alternate foreground.")
    export.add_argument("--favicon-source", help="Existing compact brand mark for tiny browser icons.")
    export.add_argument("--apple-scale", type=float, default=0.78, help="Logo width/height fit on Apple canvas (default 0.78).")
    export.add_argument("--favicon-scale", type=float, default=0.9, help="Logo fit for browser favicons (default 0.9).")
    monochrome = export.add_mutually_exclusive_group()
    monochrome.add_argument("--monochrome-source", help="Separate transparent silhouette for themed Android icons.")
    monochrome.add_argument("--monochrome-from-alpha", action="store_true", help="Make a candidate silhouette from foreground alpha.")
    export.add_argument("--play-store", action="store_true", help="Also export the separate Play listing icon.")
    export.add_argument("--pwa", action="store_true", help="Also export separate any/maskable PWA icons.")
    export.add_argument("--guidelines", help="JSON evidence of current official guideline checks performed by the caller.")
    export.add_argument("--artwork-report", help="Provider edit report whose output hash matches a supplied image.")
    return parser


def main():
    args = build_parser().parse_args()
    try:
        result = load_image(args.source)[1] if args.command == "inspect" else export_bundle(args)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
