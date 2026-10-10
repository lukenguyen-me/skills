# Local code rendering

Use this reference for **code** and **hybrid** modes. Both render the final
typography and real UI locally. Code mode uses local drawings and existing assets;
hybrid also uses separately generated decorative assets. Neither requires sending
the complete composition to an image model.

## Design and revision loop

1. Choose a composition that communicates the benefit at thumbnail size. Save
   editable sources and a runnable command. Keep shared font sizes, palette,
   frame treatment, and spacing as reusable settings across the set.
2. Render at the exact store dimensions. Inspect the full image and thumbnail;
   revise hierarchy, spacing, frame quality, shadows, or relevant panel enlargements.
   A simple scaffold is a starting point, not evidence of a finished design.
3. Show distinct finished alternatives using the saved variant count. Local
   variants change deliberate design choices rather than rerendering identical
   inputs. After selection, reuse the approved design settings for the remaining
   set, changing only benefit-specific copy, captures, and relevant accents.
4. Save the inspected RGB PNG/JPEG, design sources, source assets, render command,
   and selection in state. Follow [design.md](design.md) for review and exports.

Use the bundled renderer or an existing composer. HTML/CSS/SVG with browser
capture, canvas, and 3D rendering are valid choices when their local tools are
available. Keep each design runnable without an agent-specific API. For browser
rendering, wait for fonts and images to load and map CSS pixels/device scale to
the exact export dimensions. Record runtime dependencies and commands.

If the agent cannot view rendered files, use available image inspection tools
or obtain a user review; report visual validation as pending until observed.
Preserve genuine captures as image inputs. Enlarge real panels by cropping their
source pixels; render exact copy separately. Existing brand illustrations or
photographs can be composed locally. New photographic/painted assets may benefit
from hybrid mode when the user selects it.

## Bundled editable layer renderer

Requires Python 3.10+, Pillow, and suitable installed/licensed fonts. Resolve
`SKILL_DIR` to this installed skill. Save a UTF-8 JSON recipe, then run:

```sh
python3 "$SKILL_DIR/scripts/layout.py" render \
  --recipe screenshots/aso/01-track/design-v1.json \
  --output screenshots/aso/01-track/v1.png
```

Input paths in the recipe resolve relative to the **recipe file**, including
fonts, captures, and decorative assets. The output path resolves from the command's
working directory. Successful stdout reports dimensions, RGB mode, renderer,
recipe, real input paths, fonts, and safe area. Outputs must be new PNG/JPEG paths;
approved files are never overwritten. This command performs no network calls or
credential discovery.

The example is one starting composition, not a required template. Change the
canvas and layers for tablets, landscape screenshots, or creative placements.
Use the placement's actual template safe area from [creative-assets.md](creative-assets.md)
for Header and Search Results. Resolve the font and capture paths before rendering.

```json
{
  "width": 1290,
  "height": 2796,
  "background": "#2563EB",
  "supersample": 2,
  "safe_area": [160, 120, 970, 2556],
  "layers": [
    {
      "type": "text",
      "text": "TRACK",
      "font": "../../../assets/fonts/Brand-Black.ttf",
      "size": 190,
      "align": "center",
      "box": [180, 160, 930, 230]
    },
    {
      "type": "text",
      "text": "YOUR PROGRESS",
      "font": "../../../assets/fonts/Brand-Black.ttf",
      "size": 88,
      "align": "center",
      "box": [180, 420, 930, 140]
    },
    {
      "type": "device",
      "source": "../raw/progress.png",
      "box": [155, 750, 980, 2140],
      "radius": 90,
      "bezel": 14,
      "outline": "#777777",
      "border_width": 3,
      "bleed": true,
      "shadow": {"offset": [0, 24], "blur": 28, "color": "#00000066"}
    }
  ]
}
```

Layer order is back to front. Coordinates are `[x, y, width, height]` in final
canvas pixels. The renderer draws at `supersample` resolution (1, 2, or 3; default
2), then downsamples for smooth edges. Use 1 for memory-constrained large canvases.
The canvas background must be opaque; output always has RGB mode.

| Layer | Fields and behavior |
| --- | --- |
| `text` | Exact `text`, `font`, positive pixel `size`; optional `font_index` for collections, `fill`, `align` (left/center/right), `valign` (top/center/bottom), and pixel `spacing`. Explicit newlines are preserved; overflow fails instead of shrinking or truncating copy. |
| `device` | Real `source`, `bezel`, `radius`, optional `fill`, `outline`, and `border_width`. A neutral frame contains the complete capture at its original proportions. Set the frame box to fit the capture; it does not invent device cutouts or UI. |
| `image` | Local `source`, optional source-pixel `crop` rectangle, `radius`, and `fit`. Default `contain` retains the complete image; `cover` crops proportionally and suits decorative backgrounds. Use contain for captures or already-selected panels. |
| `rect` / `ellipse` | `fill`, optional `outline` and `border_width`; rectangles also accept `radius`. Useful for restrained brand accents and panels. |

Every layer needs a `box` and can specify `opacity` (0–255) or `shadow` with
pixel `offset`, nonnegative `blur`, and an RGBA `color` such as `#00000066`.
For a breakout, add an `image` layer from the same real capture with a measured
`crop`, enlarged box, rounded corners, and shadow. The crop must stay within the
source. It changes scale, not UI or data.

Text is essential by default. Set `essential: true` on other layers whose entire
box must fit `safe_area`; text and marked artwork fail outside that rectangle.
Use `bleed: true` for intentional device/background cropping at canvas edges.
Safe-area checks establish geometry only: inspect important UI regions, glyph
coverage, shadows, and thumbnail readability separately. Use a font appropriate
to the locale; `direction` can request RTL/LTR shaping when Pillow has libraqm.
Choose a suitable existing renderer when the bundled text layout cannot support
the requested script or effect.

## Hybrid assets

Read [providers.md](providers.md) only after hybrid/provider mode is selected.
Generate decorative artwork separately (`images: []` for prompt-only assets),
save its provenance and provider/model, inspect it, and add it as a local image
layer. Keep real captures and headline text in the local composition. Share
approved artwork across locales where appropriate; rerender localized copy.
