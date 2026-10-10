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
| `provider` | ID, model, transport/tool or custom-config path, verified capabilities, readiness, variant count |
| `design` | Brand name/hex, font path, fixed sizes per layout, canvases, targets/dimensions/locales, safe areas, Apple specification/template sources and check date |
| `style_reference` | Approved exported path, target/locale, generation ID |
| `generations` | Asset type/placement/locale, benefit/capture IDs, provider/model, prompt/request paths, reference paths, variant paths, exported paths, crop bounds/anchor, chosen variant, final path, feedback, status |
| `creative_assets` | One record per requested placement/locale: concept, benefit IDs, source asset/capture IDs, optional approved copy, dedicated/universal layout, exact dimensions/format, template safe rectangle, generation IDs, selected final path, preview evidence, design approval, Apple review/publication status |

Use `draft`, `approved`, `blocked`, or `stale` where appropriate. Generation status
may also be `generated` or `failed`. Record failures without pretending an output
exists. Inspect files on resume before accepting paths as valid evidence.

The additional scope and creative records are backward-compatible with version 1.
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
run/target paths until replacements are approved. Switching provider marks the
style reference and dependent generation plan for review, without invalidating
real captures or benefits. Do not overwrite approved finals with working outputs.
