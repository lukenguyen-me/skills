# Resumable project state

Write `screenshots/aso/state.json` (or the chosen output directory) incrementally.
Use paths relative to the app repository for portable files; record absolute paths
only for external inputs. The state is an index of evidence, not proof by itself.
Preserve unrelated entries and explicit approvals. Store no keys, tokens, private
account data, signed download URLs, or full provider responses.

Required records:

| Field | Contents |
| --- | --- |
| `schema_version` | `1` |
| `app` | Repo/app path, name, identifier, source revision, audience, positioning |
| `asset_scope` | Requested asset types (`screenshot`, `header`, `search-results`), platforms, locale mode (`all`, `single`, or an explicitly requested list), exact locale identifiers, user-choice provenance, and reasons for excluded or unsupported placements |
| `benefits` | Stable ID, order, verb, descriptor, reasoning, approval status |
| `capture_plan` | Benefit ID, source-backed commands/controls, target state, device/locale/appearance, readiness, output, blockers, cleanup |
| `captures` | ID/path, source revision, observed screen/state, dimensions, verdict, notes, automated/manual provenance |
| `pairings` | Benefit ID → capture ID, reason, approval status |
| `rendering` | Mode (`code`, `hybrid`, or `image-provider`), renderer/runtime, editable source paths, reproducible render commands, dependency notes, variant count |
| `provider` | Null/unused in code mode; selected ID, model, transport/tool or custom-config path, verified capabilities, readiness for hybrid/image-provider |
| `design` | Brand name/hex, font path, fixed sizes per layout, canvases, targets/dimensions/locales, safe areas, Apple specification/template sources and check date |
| `style_reference` | Approved exported path, target/locale, generation ID, editable source paths and reusable design settings for local rendering |
| `generations` | Asset type/placement/locale, benefit/capture IDs, mode, renderer, editable source paths, render commands, source asset paths/provenance, provider/model when used, prompt/request paths, reference paths, variant paths, exported paths, crop bounds/anchor, chosen variant, final path, feedback, status |
| `creative_assets` | One record per requested placement/locale: concept, benefit IDs, source asset/capture IDs, optional approved copy, dedicated/universal layout, exact dimensions/format, template safe rectangle, generation IDs, selected final path, preview evidence, design approval, Apple review/publication status |

Use `draft`, `approved`, `blocked`, or `stale` where appropriate. Generation status
may also be `rendered`, `generated`, or `failed`. Record failures without pretending
an output exists. Inspect files on resume before accepting paths as valid evidence.

The additional rendering, scope, and creative records are backward-compatible
with version 1.
For older state without `rendering`, honour any saved user mode; infer
`image-provider` from a saved provider selection or enhanced outputs, otherwise
initialize `code`. Copy a legacy `provider.variant_count` into
`rendering.variant_count`, preserving its value. Keep approved outputs intact;
an absent editable source on a legacy provider image is not a reason to restart.
Code mode leaves provider details unused, while hybrid/provider modes retain them.
For older state, treat generations without an asset type as screenshots. Initialize
missing requested Header/Search Results records as `draft`; keep approved
screenshots intact and resume creative planning instead of restarting capture.
Record local safe-area checks separately from App Store Connect Preview evidence.
Use `pending` for a Connect preview that requires a future requested upload, and
`not_submitted` for Apple status when only local files exist. User design approval
does not imply Apple approval or publication. A universal record lists both
placements against one PNG rather than claiming two dedicated designs exist.

Invalidate by dependency: a pairing/capture/headline change affects that benefit;
a font/colour/layout change affects the set; replacing the style reference affects
the images derived from it. A creative concept/copy/source change affects only
that placement/locale and its dependents; a universal source affects both mapped
placements. A template/specification change marks only affected layouts for review.
Preserve previously approved files under their earlier
run/target paths until replacements are approved. Switching rendering mode or
renderer marks dependent designs for review while retaining captures, benefits,
and approved files. Switching provider marks the
style reference and dependent generation plan for review, without invalidating
real captures or benefits. Do not overwrite approved finals with working outputs.
