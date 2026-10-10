#!/usr/bin/env python3
"""Deterministic portrait scaffolds, aspect-preserving exports, and set previews."""

import argparse
import json
from pathlib import Path
import sys

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps


def save_rgb(image, output):
    output = Path(output)
    if output.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        raise ValueError("Output must be PNG or JPEG")
    output.parent.mkdir(parents=True, exist_ok=True)
    file_format = "PNG" if output.suffix.lower() == ".png" else "JPEG"
    with output.open("xb") as stream:
        image.convert("RGB").save(stream, format=file_format, **({"quality": 95} if file_format == "JPEG" else {}))
    return {"output": str(output.resolve()), "width": image.width, "height": image.height, "mode": "RGB"}


def open_rgb(path, background="white"):
    with Image.open(path) as image:
        rgba = ImageOps.exif_transpose(image).convert("RGBA")
    rgb = Image.new("RGB", rgba.size, background)
    rgb.paste(rgba, mask=rgba.getchannel("A"))
    return rgb


def wrap(draw, text, font, max_width):
    lines = []
    current = ""
    for word in text.split():
        if draw.textlength(word, font=font) > max_width:
            raise ValueError("Headline word exceeds safe area; revise wording or reduce the set's font sizes")
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def compose(screenshot, output, font, verb, desc, background, width=1290, height=2796,
            verb_size=None, desc_size=None, safe_width=0.70):
    if width <= 0 or height <= width:
        raise ValueError("Bundled scaffold composer requires a portrait canvas")
    if not 0 < safe_width <= 1 or not verb.strip() or not desc.strip():
        raise ValueError("Provide nonempty headlines and a safe_width between zero and one")
    rgb = ImageColor.getrgb(background)
    if len(rgb) != 3:
        raise ValueError("Background must be an opaque RGB colour")
    canvas = Image.new("RGB", (width, height), rgb)
    draw = ImageDraw.Draw(canvas)
    verb_font = ImageFont.truetype(font, verb_size or round(width * 0.16))
    desc_font = ImageFont.truetype(font, desc_size or round(width * 0.072))
    safe_pixels = round(width * safe_width)
    if draw.textlength(verb.upper(), font=verb_font) > safe_pixels:
        raise ValueError("Verb exceeds safe area; reduce the fixed verb size for the entire set")
    lines = wrap(draw, desc.upper(), desc_font, safe_pixels)
    device_y = round(height * 0.27)
    y = round(height * 0.065)
    for text, text_font in [(verb.upper(), verb_font)] + [(line, desc_font) for line in lines]:
        box = draw.textbbox((0, 0), text, font=text_font)
        text_height = box[3] - box[1]
        draw.text((width / 2, y), text, fill="white", font=text_font, anchor="mt")
        y += text_height + round(width * 0.025)
    if y + round(width * 0.04) > device_y:
        raise ValueError("Headline overlaps device; shorten it or reduce the set's fixed sizes")

    shot = open_rgb(screenshot)
    if shot.height <= shot.width:
        raise ValueError("Portrait scaffold requires a portrait app capture")
    device_width = round(width * 0.76)
    bezel = max(2, round(width * 0.012))
    screen_width = device_width - 2 * bezel
    screen_height = round(shot.height * screen_width / shot.width)
    x = (width - device_width) // 2
    device_height = screen_height + 2 * bezel
    radius = round(device_width * 0.06)
    draw.rounded_rectangle((x, device_y, x + device_width, device_y + device_height),
                           radius=radius + bezel, fill="#141414", outline="#666666", width=max(1, bezel // 3))
    shot = shot.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, screen_width - 1, screen_height - 1), radius=radius, fill=255)
    canvas.paste(shot, (x + bezel, device_y + bezel), mask)
    return save_rgb(canvas, output)


def export_image(source, output, width, height, background="white", anchor="top"):
    if width <= 0 or height <= 0:
        raise ValueError("Export dimensions must be positive")
    if anchor not in {"top", "center"}:
        raise ValueError("Crop anchor must be top or center")
    image = open_rgb(source, background)
    original = image.size
    target_ratio = width / height
    if image.width / image.height > target_ratio:
        crop_width = min(image.width, max(1, round(image.height * target_ratio)))
        left = (image.width - crop_width) // 2
        crop = (left, 0, left + crop_width, image.height)
    else:
        crop_height = min(image.height, max(1, round(image.width / target_ratio)))
        top = (image.height - crop_height) // 2 if anchor == "center" else 0
        crop = (0, top, image.width, top + crop_height)
    image = image.crop(crop).resize((width, height), Image.Resampling.LANCZOS)
    return {**save_rgb(image, output), "source_size": original, "crop_box": crop, "crop_anchor": anchor}


def showcase(sources, output):
    if not sources:
        raise ValueError("Provide at least one approved image")
    thumbs = []
    for path in sources:
        image = open_rgb(path)
        image.thumbnail((360, 720), Image.Resampling.LANCZOS)
        thumbs.append(image)
    gap = 24
    canvas = Image.new("RGB", (sum(image.width for image in thumbs) + gap * (len(thumbs) + 1),
                                max(image.height for image in thumbs) + gap * 2), "#eeeeee")
    x = gap
    for image in thumbs:
        canvas.paste(image, (x, gap))
        x += image.width + gap
    return save_rgb(canvas, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    compose_parser = commands.add_parser("compose", help="Make a portrait scaffold with exact text and real UI")
    compose_parser.add_argument("--screenshot", required=True)
    compose_parser.add_argument("--font", required=True, help="Path to the selected heavy/black font")
    compose_parser.add_argument("--verb", required=True)
    compose_parser.add_argument("--desc", required=True)
    compose_parser.add_argument("--background", required=True)
    compose_parser.add_argument("--width", type=int, default=1290)
    compose_parser.add_argument("--height", type=int, default=2796)
    compose_parser.add_argument("--verb-size", type=int)
    compose_parser.add_argument("--desc-size", type=int)
    compose_parser.add_argument("--safe-width", type=float, default=0.70)
    export_parser = commands.add_parser("export", help="Aspect-preserving crop, exact resize, opaque RGB output")
    export_parser.add_argument("--source", required=True)
    export_parser.add_argument("--width", type=int, required=True)
    export_parser.add_argument("--height", type=int, required=True)
    export_parser.add_argument("--background", default="white")
    export_parser.add_argument("--anchor", choices=("top", "center"), default="top",
                               help="Vertical crop anchor: top for screenshots, center for central creative artwork")
    showcase_parser = commands.add_parser("showcase", help="Side-by-side preview without added branding")
    showcase_parser.add_argument("--sources", nargs="+", required=True)
    for subparser in (compose_parser, export_parser, showcase_parser):
        subparser.add_argument("--output", required=True)
    args = vars(parser.parse_args())
    command = args.pop("command")
    try:
        result = {"compose": compose, "export": export_image, "showcase": showcase}[command](**args)
        print(json.dumps(result))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
