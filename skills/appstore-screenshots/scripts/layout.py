#!/usr/bin/env python3
"""Local artwork from editable recipes, portrait scaffolds, exports, and previews."""

import argparse
import json
from pathlib import Path
import sys

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFilter, ImageFont, ImageOps


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


def checked_box(value, label):
    if (not isinstance(value, list) or len(value) != 4
            or any(type(item) is not int for item in value) or value[2] <= 0 or value[3] <= 0):
        raise ValueError(f"{label} must be [x, y, positive width, positive height] in integer pixels")
    return tuple(value)


def inside(box, area):
    x, y, width, height = box
    ax, ay, aw, ah = area
    return ax <= x and ay <= y and x + width <= ax + aw and y + height <= ay + ah


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def render_layer(layer, size, scale, base, sources, fonts):
    """Render one layer without changing source copy or stretching an image."""
    width, height = size
    tile = Image.new("RGBA", size)
    draw = ImageDraw.Draw(tile)
    kind = layer.get("type")
    radius = layer.get("radius", 0)
    if type(radius) not in {int, float} or not 0 <= radius < float("inf"):
        raise ValueError("Layer radius must be finite and nonnegative")
    radius *= scale
    if kind in {"rect", "ellipse", "device"}:
        border = layer.get("border_width", 0) * scale
        if type(border) is not int or border < 0:
            raise ValueError("border_width must be a nonnegative integer")
        fill = layer.get("fill", "#141414" if kind == "device" else "white")
        outline = layer.get("outline")
        shape = draw.ellipse if kind == "ellipse" else draw.rounded_rectangle
        options = {} if kind == "ellipse" else {"radius": radius}
        shape((0, 0, width - 1, height - 1), fill=fill, outline=outline, width=border, **options)
    if kind in {"image", "device"}:
        path = (base / layer["source"]).resolve()
        with Image.open(path) as opened:
            image = ImageOps.exif_transpose(opened).convert("RGBA")
        sources.add(str(path))
        if "crop" in layer:
            crop = checked_box(layer["crop"], "Source crop")
            if not inside(crop, (0, 0, image.width, image.height)):
                raise ValueError("Source crop exceeds the real image")
            cx, cy, cw, ch = crop
            image = image.crop((cx, cy, cx + cw, cy + ch))
        inset = layer.get("bezel", 12) * scale if kind == "device" else 0
        if type(inset) is not int or inset < 0 or 2 * inset >= min(size):
            raise ValueError("Device bezel leaves no screen area")
        target = (width - 2 * inset, height - 2 * inset)
        fit = layer.get("fit", "contain")
        if fit not in {"contain", "cover"} or (kind == "device" and fit != "contain"):
            raise ValueError("Images support contain or cover; devices require contain")
        if fit == "cover":
            image = ImageOps.fit(image, target, method=Image.Resampling.LANCZOS)
        else:
            image = ImageOps.contain(image, target, method=Image.Resampling.LANCZOS)
        if radius:
            mask = rounded_mask(image.size, max(0, radius - inset))
            image.putalpha(ImageChops.multiply(image.getchannel("A"), mask))
        tile.alpha_composite(image, ((width - image.width) // 2, (height - image.height) // 2))
    elif kind == "text":
        text = layer.get("text")
        font_size = layer.get("size")
        if not isinstance(text, str) or not text.strip() or type(font_size) is not int or font_size <= 0:
            raise ValueError("Text layers need exact nonempty text and a positive integer font size")
        path = (base / layer["font"]).resolve()
        font = ImageFont.truetype(str(path), font_size * scale, index=layer.get("font_index", 0))
        fonts.add(str(path))
        align = layer.get("align", "left")
        valign = layer.get("valign", "top")
        if align not in {"left", "center", "right"} or valign not in {"top", "center", "bottom"}:
            raise ValueError("Unsupported text alignment")
        spacing = layer.get("spacing", round(font_size * 0.2)) * scale
        if type(spacing) is not int or spacing < 0:
            raise ValueError("Text spacing must be a nonnegative integer")
        options = {"font": font, "align": align, "spacing": spacing}
        if "direction" in layer:
            options["direction"] = layer["direction"]
        bounds = draw.multiline_textbbox((0, 0), text, **options)
        tw, th = bounds[2] - bounds[0], bounds[3] - bounds[1]
        if tw > width or th > height:
            raise ValueError("Text overflows its box; revise line breaks or the set's fixed font sizes")
        tx = {"left": 0, "center": (width - tw) / 2, "right": width - tw}[align]
        ty = {"top": 0, "center": (height - th) / 2, "bottom": height - th}[valign]
        draw.multiline_text((tx - bounds[0], ty - bounds[1]), text,
                            fill=layer.get("fill", "white"), **options)
    elif kind not in {"rect", "ellipse"}:
        raise ValueError(f"Unknown layer type: {kind}")
    opacity = layer.get("opacity", 255)
    if type(opacity) is not int or not 0 <= opacity <= 255:
        raise ValueError("Layer opacity must be an integer from 0 to 255")
    if opacity != 255:
        tile.putalpha(tile.getchannel("A").point(lambda alpha: round(alpha * opacity / 255)))
    return tile


def composite_layer(canvas, tile, position, shadow, scale):
    if shadow is not None and not isinstance(shadow, dict):
        raise ValueError("Shadow must be an object")
    if shadow:
        blur = shadow.get("blur", 20) * scale
        offset = shadow.get("offset", [0, 12])
        if (not isinstance(blur, (int, float)) or not 0 <= blur < float("inf")
                or not isinstance(offset, list) or len(offset) != 2
                or any(type(item) is not int for item in offset)):
            raise ValueError("Shadow needs nonnegative blur and an integer [x, y] offset")
        colour = ImageColor.getcolor(shadow.get("color", "#00000066"), "RGBA")
        pad = round(blur * 3)
        alpha = Image.new("L", (tile.width + 2 * pad, tile.height + 2 * pad), 0)
        alpha.paste(tile.getchannel("A"), (pad, pad))
        alpha = alpha.filter(ImageFilter.GaussianBlur(blur))
        shade = Image.new("RGBA", alpha.size, colour)
        shade.putalpha(alpha.point(lambda value: round(value * colour[3] / 255)))
        canvas.alpha_composite(shade, (position[0] + offset[0] * scale - pad,
                                     position[1] + offset[1] * scale - pad))
    canvas.alpha_composite(tile, position)


def render_design(recipe, output):
    """Render a local JSON design; input paths resolve beside the recipe file."""
    output = Path(output)
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")
    if output.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        raise ValueError("Output must be PNG or JPEG")
    recipe = Path(recipe).resolve()
    spec = json.loads(recipe.read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        raise ValueError("Design recipe must be a JSON object")
    area = checked_box([0, 0, spec.get("width"), spec.get("height")], "Canvas")
    safe = checked_box(spec.get("safe_area", list(area)), "Safe area")
    if not inside(safe, area):
        raise ValueError("Safe area exceeds the canvas")
    scale = spec.get("supersample", 2)
    if type(scale) is not int or scale not in {1, 2, 3}:
        raise ValueError("supersample must be 1, 2, or 3")
    background = ImageColor.getcolor(spec.get("background", "white"), "RGBA")
    if background[3] != 255:
        raise ValueError("Canvas background must be opaque")
    layers = spec.get("layers")
    if not isinstance(layers, list) or not layers:
        raise ValueError("Design recipe needs a nonempty layers list")
    canvas = Image.new("RGBA", (area[2] * scale, area[3] * scale), background)
    sources, fonts = set(), set()
    for index, layer in enumerate(layers):
        if not isinstance(layer, dict):
            raise ValueError(f"Layer {index} must be an object")
        bounds = checked_box(layer.get("box"), f"Layer {index} box")
        essential = layer.get("essential", layer.get("type") == "text")
        if type(essential) is not bool:
            raise ValueError("Layer essential must be true or false")
        if essential and not inside(bounds, safe):
            raise ValueError(f"Essential layer {index} exceeds the safe area")
        bleed = layer.get("bleed", False)
        if type(bleed) is not bool:
            raise ValueError("Layer bleed must be true or false")
        if not inside(bounds, area) and not bleed:
            raise ValueError(f"Layer {index} exceeds the canvas; set bleed for intentional edge cropping")
        tile = render_layer(layer, (bounds[2] * scale, bounds[3] * scale), scale,
                            recipe.parent, sources, fonts)
        composite_layer(canvas, tile, (bounds[0] * scale, bounds[1] * scale), layer.get("shadow"), scale)
    canvas = canvas.convert("RGB").resize((area[2], area[3]), Image.Resampling.LANCZOS)
    return {**save_rgb(canvas, output), "renderer": "pillow", "recipe": str(recipe),
            "sources": sorted(sources), "fonts": sorted(fonts), "safe_area": safe, "supersample": scale}


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
    render_parser = commands.add_parser("render", help="Render final artwork locally from an editable JSON recipe")
    render_parser.add_argument("--recipe", required=True, help="Design JSON; its input paths are relative to this file")
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
    for subparser in (render_parser, compose_parser, export_parser, showcase_parser):
        subparser.add_argument("--output", required=True)
    args = vars(parser.parse_args())
    command = args.pop("command")
    try:
        result = {"render": render_design, "compose": compose, "export": export_image, "showcase": showcase}[command](**args)
        print(json.dumps(result))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
