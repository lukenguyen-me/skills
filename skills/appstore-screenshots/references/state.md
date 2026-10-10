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
| `benefits` | Stable ID, order, verb, descriptor, reasoning, approval status |
| `capture_plan` | Benefit ID, source-backed commands/controls, target state, device/locale/appearance, readiness, output, blockers, cleanup |
| `captures` | ID/path, source revision, observed screen/state, dimensions, verdict, notes, automated/manual provenance |
| `pairings` | Benefit ID → capture ID, reason, approval status |
| `provider` | ID, model, transport/tool or custom-config path, verified capabilities, readiness, variant count |
| `design` | Brand name/hex, font path, fixed sizes, layout canvas, targets/dimensions/locales, safe area |
| `style_reference` | Approved exported path, target/locale, generation ID |
| `generations` | Benefit/capture IDs, provider/model, prompt/request paths, reference paths, variant paths, exported paths, chosen variant, final path, feedback, status |

Use `draft`, `approved`, `blocked`, or `stale` where appropriate. Generation status
may also be `generated` or `failed`. Record failures without pretending an output
exists. Inspect files on resume before accepting paths as valid evidence.

Invalidate by dependency: a pairing/capture/headline change affects that benefit;
a font/colour/layout change affects the set; replacing the style reference affects
the images derived from it. Preserve previously approved files under their earlier
run/target paths until replacements are approved. Switching provider marks the
style reference and dependent generation plan for review, without invalidating
real captures or benefits. Do not overwrite approved finals with working outputs.
