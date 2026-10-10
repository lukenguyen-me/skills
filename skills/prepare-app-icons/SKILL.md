---
name: prepare-app-icons
description: Adapt an existing app icon or logo into Apple app icons, Android adaptive launcher icons, and web favicons. Use when exporting platform icon assets or correcting their padding, layers, sizes, transparency, and packaging while preserving the supplied artwork.
---

# Prepare app icons

Turn supplied artwork into a usable platform icon set. Preserve its identity,
proportions, colors, and intentional details. This skill prepares existing artwork;
creating a new logo belongs to a separate design or image-generation workflow.
Artwork produced by that workflow can become this skill's input.

## Resolve the artwork and targets

Use the supplied file, or find the app's canonical icon in its repository. Prefer
the original vector or layered artwork over a screenshot or a compressed store
thumbnail. Inspect the image visually and inspect its dimensions, color profile,
alpha channel, and visible artwork bounds.

Distinguish a **logo/foreground** from a **finished flat icon** and from an
**already padded platform layer**. A flat tile includes its background; resizing
that tile into an Android foreground does not separate the logo. Recover layers
from editable artwork or use a supplied transparent foreground. Ask for missing
artwork only when reliable separation needs a design decision. Continue targets
that can use the available source.

Use platforms requested by the user or established by the app. For a generic
request for all three platforms, prepare iOS/iPadOS, Android, and web. Include
macOS, watchOS, tvOS, visionOS, PWA icons, or store listing assets when requested
or present in the target app. Inspect the existing Xcode catalog/`.icon` file,
Android resources, web manifest, and framework icon configuration before choosing
packaging. Reuse established names and integration conventions.

Derive backgrounds from the existing icon or brand. Keep essential artwork intact
when adding space, centering, or changing canvas size. Trim only redundant outer
transparency on a logo, and account for existing padding before adding more.
Use a supplied compact brand mark for tiny favicons when available. If a wordmark
needs simplification, resolve that brand choice with the user.

## Check current guidance

Before final export, open the official sources in each applicable reference:

- Apple targets: [references/apple.md](references/apple.md).
- Android launcher and optional Play listing: [references/android.md](references/android.md).
- Browser favicon, touch icon, and optional PWA: [references/web.md](references/web.md).

The reference snapshots are starting points. Recheck dimensions, safe areas,
layer structure, appearances, transparency, color space, and delivery format
against current documentation and the project's toolchain. Separate platform
requirements from this skill's composition defaults. In particular, Apple does
not prescribe one universal logo padding percentage.

Record the actual check date, source URLs, applicable requirements, and any
inaccessible sources in `guideline-check.json` beside the output. Reuse checks
already performed during the same task. If browsing is unavailable, continue
with the dated snapshot and label the result as awaiting current-guideline
verification; do not describe it as verified against the latest guidance.

## Compose and export

Use local asset tools for deterministic sizing, framing, alpha composition, and
format conversion. Keep source files and editable vectors. If the user explicitly
requests artwork repair or generation, use an available image-editing/design
workflow, inspect its result, then perform the platform exports here.

Create a separate composition for each platform. Android's adaptive foreground
needs more room than the typical Apple composition. Browser favicons need enough
visible artwork to read at 16–32 pixels; PWA maskable icons have their own circular
safe zone. Apply platform masks only to previews; export unmasked platform layers.

The bundled [export helper](references/export-helper.md) handles raster input,
iOS/iPadOS PNG catalogs, Apple foreground handoff layers, Android resources,
favicons, touch icons, and optional PWA/Play assets. It preserves aspect ratios,
uses sRGB, measures visible bounds, and writes an asset report and previews.
Use a native renderer to export vector artwork to a sufficiently large PNG for
the helper, retaining the original vector for editable deliverables. Other tools
can supply target-specific exports or existing native `.icon` files.

Resolve helpers relative to this installed skill, not the app's working directory
or a hardcoded agent home. Use a new output directory such as `output/app-icons/`
unless the project or user establishes another location. The helper refuses to
replace an existing directory; use a sibling directory for a revision.

For Apple, select the project's supported delivery path. Build and verify a native
Icon Composer file when the tool is available and the task calls for it. If only
foreground layers and setup instructions can be prepared, identify them as a
handoff. A PNG or a renamed directory is not a verified `.icon` file. A flat
catalog remains a valid delivery path when the project uses one.

## Verify and deliver

Check exported dimensions, actual file formats, alpha rules, color profiles,
file size limits, catalog metadata, and every resource/HTML/manifest reference.
Inspect the preview sheet, the original artwork, and actual 16/32-pixel favicons.
Android previews must crop the central launcher viewport before applying circle,
squircle, and rounded-square masks; masking the full 108 dp canvas hides errors.
Inspect themed silhouettes separately, especially multicolor marks whose meaning
depends on internal color boundaries. Treat the helper's monochrome conversion
as a candidate requiring visual review.

When integration is requested, place assets into the project's native locations,
merge metadata into existing catalogs/manifests, and run the relevant build or
icon check. When export alone is requested, provide exact integration instructions
without changing application configuration.

Deliver the platform files, editable sources/layers, preview sheet, and reports.
Report the source artwork, output location, guidance check date, and any pending
native-tool or visual verification. Geometry checks establish file compliance;
they do not establish brand quality or native system rendering.
