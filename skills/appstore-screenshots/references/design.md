# Layout, enhancement, and export

## Visual specification

This reference covers the screenshot carousel. Read
[creative-assets.md](creative-assets.md) for Header and Search Results layouts;
they use their own landscape compositions and template safe areas.

Use one bold, solid brand background, white uppercase headlines, and a heavy/black
sans-serif font. Put the action verb above the smaller benefit descriptor, centred
in the top quarter. Keep font, sizes, spacing, device position, and background
consistent across the set. Infer colour from source/assets and captures; explain
the selected hex value and allow the user to override it.

Use a device frame appropriate to the actual platform and capture. A portrait
phone sits high, centred, with its bottom intentionally bleeding past the canvas.
Do not stretch the UI into a different device aspect ratio. A breakout is optional:
only enlarge an entire existing, relevant panel, keeping its orientation/content,
with a soft shadow. Keep secondary decoration sparse and related to the benefit.

## Dimensions and crop planning

Check [Apple's screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)
for the requested targets before final export. Record exact dimensions and the
corresponding display slot. `1290 × 2796` portrait is a useful iPhone starting
target when compatible with the selected slot, not an exhaustive size rule. Check
iPad requirements when the app supports it. Use opaque RGB PNG/JPEG.

Choose generation settings from the selected model's supported sizes. When its
output ratio differs from the store target, plan the final top-centred crop. If
the source is wider, the retained width fraction is
`(target_width / target_height) / (source_width / source_height)`; if narrower,
height is removed from the bottom. For 9:16 → 1290:2796, about 82% of the width
survives. The common 70% text safe width fits, but verify the actual device and
breakout contents too. A square source needs a substantially narrower safe area.
Prefer an output ratio close to the target over aggressive cropping.

## Local helpers

Requirements: Python 3.10+, Pillow, and an actual installed/licensed heavy font.
Use existing project dependencies or a disposable environment. Discover a font
in app assets/system fonts and record its path; the helper has no mandatory
macOS-only font or bundled proprietary font. Resolve `SKILL_DIR` to the installed
skill's absolute path and run commands from the app repository.

The bundled composer supports **portrait phone captures**. For tablets,
landscape, desktop, or an existing branded device-frame system, adapt/reuse the
project's composer while retaining exact text, real UI, fixed layout, and safe
areas. The export and showcase helpers accept either orientation. Build a
scaffold for each target layout rather than recropping a phone design into a tablet
or a creative asset. Use `export --anchor center` for a planned central focal point;
the default `--anchor top` preserves screenshot headlines.

```sh
python3 "$SKILL_DIR/scripts/layout.py" compose \
  --screenshot screenshots/aso/raw/progress.png \
  --font /absolute/path/to/HeavyFont.ttf \
  --verb TRACK --desc 'YOUR PROGRESS' --background '#2563EB' \
  --width 1290 --height 2796 --safe-width 0.70 \
  --output screenshots/aso/01-track/scaffold.png
```

Set `--verb-size` and `--desc-size` to the same pixel sizes for every scaffold in
one layout. Defaults scale with canvas width. The helper fails for text overflow;
shorten wording with the user's agreement or reduce the **whole set's** sizes,
rather than making one headline inconsistent. Keep scaffolds as internal
intermediates. Inspect the real UI placement before enhancement.

## Provider-neutral enhancement prompts

Tailor these prompts to inspected image content. Resolve bracketed fields before
submitting them; do not invent a panel to satisfy a placeholder.

First screenshot, using its scaffold:

```text
Turn this App Store screenshot scaffold into a polished marketing image.
Preserve the headline exactly: [VERB] / [DESCRIPTOR]. Preserve its position and
relative sizes, the solid [HEX] background, and the real app capture's UI/data.
Keep all meaningful content inside [SAFE AREA FOR FINAL CROP].
Refine the [ACTUAL DEVICE TYPE] frame with realistic proportions and subtle
reflections/shadows at the same size and position. Keep the phone high and its
bottom cropped by the canvas. Keep the text crisp, heavy, white, and uppercase.
[Describe a relevant existing complete panel to enlarge at its original vertical
position and orientation with a soft shadow, or: Use no breakout.]
[Describe at most two relevant supporting elements, or: No secondary elements.]
Use a clean solid background. Return one complete image, without extra copy,
visible watermarks, store chrome, invented app controls, or changed app content.
```

Later screenshots, using scaffold then first approved style image:

```text
Create the next image in this App Store screenshot set.
Reference 1 is the scaffold: authoritative headline, layout, device placement,
and real app capture for this benefit.
Reference 2 is the approved style: match its device rendering, typography,
background treatment, proportions, shadows, and polish.
Preserve the exact headline [VERB] / [DESCRIPTOR], the solid [HEX] background,
and the real UI/data from reference 1. Use the same device frame as reference 2,
changing only its screen contents. Keep meaningful content inside [SAFE AREA].
[Relevant complete-panel breakout description, or: Use no breakout.]
[Zero to two supporting elements grounded in the benefit.]
Return one complete marketing image belonging to this series. Keep app content
faithful and add no extra copy, visible watermarks, or store chrome.
```

For revisions, identify reference 3 as the user's selected design direction and
append their exact requested changes. For the first image, omit a nonexistent
style reference. With fewer allowed inputs, use the provider capability fallback.
Retain prompt files and actual reference paths for reproducibility.

## Export before review

Normalize **every** generated candidate immediately. The helper preserves aspect
ratio, crops symmetrically at the sides or trims the bottom, flattens alpha, and
reports source dimensions/crop bounds. It never stretches the whole source:

```sh
python3 "$SKILL_DIR/scripts/layout.py" export \
  --source screenshots/aso/01-track/v1.png \
  --width 1290 --height 2796 --background '#2563EB' \
  --output screenshots/aso/01-track/v1-export.png
```

Inspect all exports at full size and thumbnail size. Check exact headline
spelling, real controls/data, crisp text, device proportions, crop safety,
background consistency, and variation from the style reference. Prompt adherence
is not proof of UI preservation; reject or restore faithful composition if
generation invents content. Show only valid export-sized variants for selection.
Regenerate after a specific correction, with at most two automatic retries per
pairing before reporting the repeated issue and asking for direction. User-requested
revisions begin a new bounded attempt.

Copy the chosen inspected export to its ordered final target/locale path and
save approval in state. Preserve earlier approved files when revising.

Once the set is approved:

```sh
python3 "$SKILL_DIR/scripts/layout.py" showcase \
  --sources screenshots/aso/final/iphone/en-US/01-track.png \
            screenshots/aso/final/iphone/en-US/02-create.png \
  --output screenshots/aso/showcase.png
```

Helpers refuse existing output paths. Use a new run/variant path for iterations.
The showcase is a preview; only individual approved files belong in store slots.
