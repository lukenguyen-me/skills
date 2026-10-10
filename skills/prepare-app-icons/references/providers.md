# Optional artwork provider adapters

Read this when the user requests AI repair, enhancement, or foreground extraction.
Ordinary resizing, padding, background composition, and export use
[export-helper.md](export-helper.md) directly. Every edit starts with existing
artwork; a separately generated logo can be supplied as that artwork.

## Select a provider and transport

Honor the selected provider, model, and transport. Discover connected image tools
and local API key presence without printing keys. Use the available built-in
image-editing tool for a generic AI edit when appropriate; read its applicable
image skill. An explicit Gemini, Grok, or API request uses that integration.
Ask for a provider only when that choice matters and the session leaves it open.
Model IDs are explicit inputs, not permanent defaults.

Before a live edit, check the selected model's current edit/reference support,
input limits, size options, and alpha capability in its official documentation.
Provider options are not interchangeable. Snapshot checked **2026-10-10**:

| ID | API key environment variable | Bundled HTTP transport |
| --- | --- | --- |
| `gpt-image` | `OPENAI_API_KEY` | Images edits; multipart `image[]` references |
| `gemini` | `GEMINI_API_KEY` | Interactions; ordered image input blocks and final `model_output` image |
| `grok` | `XAI_API_KEY` | Images edits; JSON `image` or `images`, currently up to five references |

Current primary sources:

- [OpenAI image generation and editing](https://developers.openai.com/api/docs/guides/image-generation).
- [Gemini image generation and editing](https://ai.google.dev/gemini-api/docs/image-generation)
  and [Interactions](https://ai.google.dev/gemini-api/docs/interactions-overview).
- [Grok editing](https://docs.x.ai/developers/model-capabilities/images/editing)
  and [multiple references](https://docs.x.ai/developers/model-capabilities/images/multi-image-editing).

The Gemini adapter uses the current synchronous Interactions route. A model or
integration that requires `generateContent`, Vertex AI, async jobs, or another
transport can use a custom bridge. The helper does not prove account/model access.

## Shared edit request

The helper requires Python 3.10+ and Pillow. HTTP transport uses the standard
library and needs no provider SDK. Resolve the helper from this installed skill.

```sh
python3 scripts/edit_artwork.py --check
python3 scripts/edit_artwork.py --request /path/to/edit-request.json
```

`--check` reads key presence locally; it makes no API call. Example request:

```json
{
  "provider": "gpt-image",
  "model": "user-selected-image-edit-model",
  "prompt": "Extract the existing mark from image 1 onto a transparent background. Preserve its silhouette, proportions, colors, text, and internal details. Return unmasked foreground artwork without a rounded tile or outer shadow.",
  "images": ["assets/original-icon.png"],
  "output": "output/artwork/foreground-v1.png",
  "require_transparency": true,
  "options": {}
}
```

Paths resolve against the app working directory. Image 1 is the edit target;
subsequent images are labeled references in the prompt. The helper requires at
least one PNG/JPEG/WebP input, an explicit model, and a new PNG output path.
Keep the source artwork unchanged. State the intended edit and brand invariants
in the prompt; change only what the user requested.

`options` contains only settings supported by that provider/model. GPT Image
accepts scalar Images API options. For a model that supports transparent output,
use its documented `background`/`output_format` controls; the helper does not
silently change the chosen model. Gemini options are Interactions settings,
such as `response_format: {"type":"image","mime_type":"image/png",
"aspect_ratio":"1:1"}`. Grok accepts documented image options such as
`aspect_ratio`. Streaming and background job polling belong to a custom bridge.

One call returns one candidate and `<output>.edit.json`, recording the actual
provider, model, prompt, input hashes, output hash, alpha range, and pending visual
review. Preserve the report with the deliverables. Output is RGBA PNG: genuine
alpha and RGB color profiles are retained. Profiled non-RGB output is converted
to sRGB before saving; output is never flattened to white.
`require_transparency: true` rejects an opaque or empty result before publishing
it. It verifies actual alpha; it does not grant a model transparency capability.
Gemini/Grok documentation does not establish a universal alpha guarantee.

Inspect the candidate against the original before export. Reject altered text,
lost holes, changed proportions, invented detail, or a checkerboard drawn into
RGB pixels. When reliable extraction is unavailable, use editable originals or
an available cutout workflow and keep the foreground pending. A provider-rendered
square tile does not count as an adaptive foreground.

## Export the reviewed master

After visual inspection, pass the candidate through the existing exporter:

```sh
python3 scripts/export_icons.py export \
  --source output/artwork/foreground-v1.png --source-kind logo \
  --background '#183153' --platforms apple android web \
  --artwork-report output/artwork/foreground-v1.png.edit.json \
  --out output/app-icons-v1
```

The exporter fits safe areas and exact dimensions, converts to sRGB, and flattens
only assets that require opaque backgrounds. It copies the matched artwork report
into the bundle. Perform the platform guidance checks and supply `--guidelines`
as usual. AI output remains subject to brand and native rendering review.

## Custom command bridge

Use an existing CLI or SDK wrapper for another provider or transport. Inspect its
command and capability declaration before execution. Example config:

```json
{
  "id": "my-image-provider",
  "command": ["python3", "/absolute/path/to/provider_bridge.py"],
  "capabilities": {
    "reference_edit": true,
    "max_reference_images": 3,
    "transparent_output": true
  },
  "required_env": ["MY_IMAGE_API_KEY"]
}
```

Set the request's `provider` to the config ID and pass
`--adapter-config /path/to/adapter.json` to `--check` or `--request`.
The command receives the normalized JSON request on stdin with absolute input
paths and a temporary output path. It inherits environment credentials, writes
the candidate, and prints one JSON object: `{"output":"/local/candidate.png"}`.
The runner invokes an argument array without a shell and validates the actual
image and alpha before publishing the final variant and report. A declaration
of `transparent_output` is required for transparent requests and checked against
the returned pixels. Custom execution defaults to a 300-second timeout.

## Connected tool transport

Map the same prompt, ordered references, and alpha requirement to the selected
tool's real schema. Inspect local references before editing. Save its actual
result in the workspace and record provider/model information truthfully;
if the tool does not expose a model ID, record that limitation. Preserve alpha
and retain its provenance alongside the exports.

API transport needs the corresponding environment key; connected tools use
their existing authentication. API adapters perform no automatic billable retries
or vendor/model fallback. Diagnose a failed call and keep earlier successful
variants before retrying. Provider selection stays independent of platform export.
