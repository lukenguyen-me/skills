# Header and Search Results creative assets

Requirements checked **2026-10-10**. Recheck Apple's live specifications and
templates when planning a new set; save the check date and sources in state.

These optional creative placements accompany the screenshot carousel and appear
on iOS/iPadOS 27 and later. Keep the normal screenshot deliverables. This skill
includes one static image for each placement in a full iOS/iPadOS run; use a
shared universal asset only when requested. Videos are outside this default.
[Apple's asset management guide](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-your-app-store-assets)

## Image specifications

| Placement | Apple aspect ratio | Accepted pixel dimensions | Formats | Skill default |
| --- | --- | --- | --- | --- |
| Header | 21:9 | 3840 × 1646 | JPEG, JPG, PNG | 3840 × 1646 PNG |
| Search Results | 3:2 | Minimum 1920 × 1280; maximum 3840 × 2560 | JPEG, JPG, PNG | 3840 × 2560 PNG |
| Universal, usable in either placement | 16:9 | 5244 × 2950 | PNG | Only when requested |

Use the published exact Header and Universal dimensions rather than recalculating
them from the rounded aspect ratios. A smaller dedicated Search Results image
must retain 3:2 and remain within the published range. All images must omit alpha
channels and transparency. Export opaque RGB files as the workflow convention.
Apple's table does not specify a Header/Search Results file-size limit, color
profile, or bit depth; the adjacent 500 MB limit is for In-App Event images.
[Apple's creative asset specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/creative-assets-specifications)

## Creative direction

- **Header:** express the brand or a compelling offering through one clear idea
  for a first-time visitor. Choose a hero visual grounded in the app's purpose.
- **Search Results:** make the purpose obvious at a glance. Show interface,
  content, or gameplay that helps someone decide to download.
- Share palette, fonts, and tone. Text is optional; keep it short, legible, and
  localized. These placements do not require the screenshot verb/descriptor layout.
- Omit prices, discounts, URLs, copyright symbols, unsupported claims, other
  platform/marketplace marks, and Apple recognition badges.
- Use inclusive imagery suitable for 4+, even when the app has a higher rating.
  Avoid objectionable material, gore, and weapons aimed at people or the viewer.

Apple permits short text and imagery beyond app-in-use content when related to
the app. Its guidance does not impose a blanket ban on an app's own logo, UI,
or device frames. Choose these elements for the composition rather than copying
App Clip card or editorial artwork rules.
[Apple's asset best practices](https://developer.apple.com/app-store/asset-best-practices/)

## Template safe areas and placement previews

The following rectangles were measured from Apple's **Sketch templates**;
Header and Search Results also match the Photoshop `Art Safe Area` layers.
Coordinates start at the canvas's upper-left corner and use `(x, y, width, height)`.

| Canvas | Art safe area in pixels |
| --- | --- |
| Header, 3840 × 1646 | (1097, 493, 1646, 661) |
| Search Results, 3840 × 2560 | (836, 765, 2168, 1030) |
| Universal, 5244 × 2950 | (1921, 660, 1402, 962) |

Sources: [Sketch templates](https://devimages-cdn.apple.com/design/resources/download/app-store/creative_assets-templates.sketch),
[Header Photoshop template](https://devimages-cdn.apple.com/design/resources/download/app-store/creative_assets-product_page_header_template-static.psd),
[Search Results Photoshop template](https://devimages-cdn.apple.com/design/resources/download/app-store/creative_assets-search_results_template-static.psd).
In Sketch, inspect the canvas's nested
`Art Safe Area/Art Area/Art Safe Area/Rectangle`; use its bounds and ancestor
offsets, excluding the canvas's position on the page. Parent group sizes can
differ from the actual rectangle. Re-extract bounds if Apple changes a template.

These are composition guides, not exact crop boundaries or upload constraints.
Keep essential artwork, readable UI details, and any copy inside the appropriate
rectangle; extend decorative background to the edges. Scale all coordinates
proportionally for smaller Search Results exports. The Universal safe area sits
above the canvas's vertical center, so a generic centered composition is
insufficient. Remove all template labels, guides, and masks from final images.

Inspect local guide overlays on copies of the **normalized exports**, including
thumbnail views. Apple's App Store Connect Preview can show device, orientation,
and language variations. Use it when the assets are already available there;
otherwise record the local checks and mark the Connect preview pending until an
upload is requested. A local template check is not proof of Apple's rendered crop.
[Apple's Preview instructions](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-your-app-store-assets)

## Static-image recipe

1. Save a brief per placement/locale: concept, related benefit IDs, source asset
   paths or capture IDs, optional exact copy, export size, and template safe area.
   Reuse the strongest inspected capture for Search Results when suitable.
   Header art can express positioning without requiring another UI capture.
2. Compose a dedicated landscape scaffold with a project composer or a small
   local Pillow composition. Use approved brand assets and real captures, keep
   their proportions, and place essential content within the template guide.
   The bundled portrait `compose` command cannot make these layouts. Plan the
   provider's output ratio and final crop before enhancement; a resized portrait
   screenshot is not a creative scaffold.
3. Enhance through the selected provider using the prompt below. Include the
   scaffold first and an approved brand/style image second when supported.
   If no style exists for an asset-only request, establish it with the first
   approved creative. With limited reference support, use the fallbacks in
   [providers.md](providers.md); composite exact UI/copy locally when necessary.
4. Export each variant immediately at its placement size. Use `--anchor center`
   when the planned focal point is central; use the planned anchor for Universal.
   The helper removes alpha and preserves proportions, but cannot prove text or
   UI safety. Save its crop bounds, then inspect the resulting file.
5. Review valid candidates separately for Header and Search Results. Use the
   saved variant count and the bounded retry policy in [design.md](design.md).
   Check faithful UI, exact optional copy, brand consistency, safe areas, and
   local placement previews before user selection.
6. Save one selected export per requested placement/locale:
   `final/creative/<locale>/header.png` and
   `final/creative/<locale>/search-results.png`. Keep drafts and previews outside
   `final/`. Record separate design approval and Apple review/publication status.
   A requested universal file remains 5244 × 2950 PNG and maps to both placements;
   do not count it as a screenshot or quietly substitute it for two dedicated images.

Resolve `SKILL_DIR` as described in [design.md](design.md). Dedicated export examples:

```sh
python3 "$SKILL_DIR/scripts/layout.py" export \
  --source screenshots/aso/creative/en-US/header/v1.png \
  --width 3840 --height 1646 --anchor center --background '#2563EB' \
  --output screenshots/aso/creative/en-US/header/v1-export.png

python3 "$SKILL_DIR/scripts/layout.py" export \
  --source screenshots/aso/creative/en-US/search-results/v1.png \
  --width 3840 --height 2560 --anchor center --background '#2563EB' \
  --output screenshots/aso/creative/en-US/search-results/v1-export.png
```

### Enhancement prompt

```text
Create a polished static [HEADER / SEARCH RESULTS] creative for [APP / AUDIENCE].
Reference 1 is authoritative for composition, approved artwork, and real UI/data.
[Reference 2 supplies the approved brand style; match its palette, font family,
and finish while retaining this placement's landscape composition.]
Communicate this one idea: [SOURCE-BACKED CONCEPT].
[Preserve this approved short localized phrase exactly: COPY. / Add no text.]
Preserve genuine UI and content; do not invent controls, features, or claims.
Keep essential content within [SAFE RECTANGLE MAPPED TO THE FINAL CROP].
Extend the background to all edges. Use [VERIFIED PROVIDER OUTPUT RATIO], planned
for export to [EXACT WIDTH × HEIGHT]. Return one clean image with no guides,
template labels, watermark, store chrome, pricing, URLs, or recognition badges.
```

## Store handoff

The upload destination is **Apps → app → version → Product Page Information →
Header and Search Results → Header or Search Results**. These are separate from
the App Previews and Screenshots tab. Universal assets alone support **Use header
asset in search results**. Assets can receive standalone approval in Asset Library;
approved assets can update a live placement without a new app version. Prepare
the placement/locale mapping with the files; execute upload or publishing only
when separately requested.
[Apple's upload and update instructions](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-your-app-store-assets)
