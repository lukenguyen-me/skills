# Image provider adapters

Select the user's provider independently of the screenshot workflow. This skill
supports connected image tools, three bundled HTTP adapters, and a custom command
adapter. Provider identity and transport are separate: GPT Image can use an
available native image tool or the OpenAI API. API credentials are needed only for
API transport.

## Discover and select

Inspect the active tool catalog and local environment for usable integrations.
Check key **presence**, without printing values. Show Gemini, GPT Image, Grok, and
a custom choice with readiness and material limits. Honour a named provider even
if unavailable: resolve that integration or explain the blocker. Ask for a choice
only when the session/state has not already established one.

Verify the selected model's reference-edit support, maximum reference count,
output sizes/ratios, and concurrency from its tool schema/current official docs.
The HTTP helper routes requests; it does not prove model access or availability.
No model is hardcoded as a permanent default. Save the selected ID in state.

## Shared request and result contract

One request produces one variant. Save a UTF-8 JSON request with this shape:

```json
{
  "provider": "gemini",
  "model": "user-selected-current-image-model",
  "prompt": "Full enhancement prompt, including exact headline and reference roles",
  "images": ["screenshots/aso/01-track/scaffold.png"],
  "output": "screenshots/aso/01-track/v1.png",
  "options": {}
}
```

Use `images: []` only for separate decorative-asset generation. Input order is
scaffold, first approved style reference, then chosen revision direction. Paths
in request JSON resolve relative to the app repo working directory. `options` are
provider-specific supported generation settings, never credentials or replacement
prompts/references. Each request uses a new output path.

The bundled helper needs Python 3.10+ and Pillow. HTTP calls use the standard
library; no provider SDK installation is required:

```sh
python3 "$SKILL_DIR/scripts/generate_image.py" --check
python3 "$SKILL_DIR/scripts/generate_image.py" --request screenshots/aso/request-v1.json
```

`--check` performs local credential checks without API calls. Successful stdout
is JSON containing `provider`, `model`, `output`, `width`, and `height`. The helper
downloads/decodes results, validates the image, and saves an RGB PNG at `output`.
Raw results still require the design reference's export and visual review.
Errors leave no claimed output. There are no automatic billable retries; retain
successful variants and diagnose a failed call before deciding to retry.

## Bundled HTTP adapters

| Provider ID | Environment key | Reference-edit request | Settings |
| --- | --- | --- | --- |
| `gemini` | `GEMINI_API_KEY` | Gemini `generateContent`, ordered inline image parts | `options` becomes `generationConfig`; image/text modalities are requested |
| `gpt-image` | `OPENAI_API_KEY` | OpenAI Images edits, multipart ordered `image[]` files | Supported Images API options, such as model-compatible `size` and `quality` |
| `grok` | `XAI_API_KEY` | xAI Images edits, JSON `image` or `images` with data URIs | Supported xAI image options, such as `aspect_ratio` |

Grok uses JSON rather than OpenAI's multipart editing format. For Gemini, select
configuration fields appropriate to the model/API version. Send only settings
verified for the selected model; a generic quality/fidelity option is not portable.
The helper requests one variant per call and extracts the first final image.

Consult current primary sources for model and capability selection:

- [Gemini image generation / editing](https://ai.google.dev/gemini-api/docs/generate-content/image-generation)
- [OpenAI image generation / editing](https://developers.openai.com/api/docs/guides/image-generation)
- [xAI image editing](https://docs.x.ai/developers/model-capabilities/images/editing)
  and [multiple references](https://docs.x.ai/developers/model-capabilities/images/multi-image-editing)

## Connected tool adapter

Read the actual selected tool's schema and any applicable image skill. Translate
the shared request to its prompt, local references/attachments, model settings,
and output controls. Use one logical variant per request, tracking outputs when
the tool returns several. Save or download its actual result locally, then report
the shared result fields after inspecting it. Do not assume a chat tool, image
analysis tool, or a tool named `generate` can edit references.

If a tool saves into another directory or returns an attachment, materialize it
at the request's unique output path. If it cannot return a local artifact, record
that limitation and keep the result pending instead of claiming an export exists.

## Custom command adapter: another provider

Use an existing provider CLI, SDK wrapper, or project script without modifying the
main workflow. Read the command before execution. Create a local config:

```json
{
  "id": "my-provider",
  "command": ["python3", "/absolute/path/to/provider_bridge.py"],
  "capabilities": {"reference_edit": true, "max_reference_images": 3},
  "required_env": ["MY_PROVIDER_API_KEY"]
}
```

Set request `provider` to that config's ID, then run:

```sh
python3 "$SKILL_DIR/scripts/generate_image.py" --check --adapter-config /path/to/adapter.json
python3 "$SKILL_DIR/scripts/generate_image.py" --request screenshots/aso/request-v1.json \
  --adapter-config /path/to/adapter.json
```

The command receives the shared request as JSON on stdin, with absolute input and
output paths. It inherits environment credentials, completes/polls its job, saves
the image, and prints one JSON object with `output` pointing to that local file.
Diagnostics belong on stderr. A nonzero exit is a failure. The runner uses an
argument array without a shell and validates/materializes the resulting image.
Describe limits truthfully; unavailable reference editing fails before invocation.
The command timeout defaults to 300 seconds and is configurable with `--timeout`.

## Capability fallbacks

- **Two inputs:** scaffold + style reference. Describe the revision direction in
  the prompt and omit its third image explicitly.
- **One input:** first screenshot uses its scaffold. For later screenshots, make
  a labeled reference board containing the scaffold and style image, identifying
  the region to return. Inspect closely for layout/content drift. If the provider
  cannot isolate that region reliably, retain deterministic composition and use
  it only for separate assets, or ask the user to select a capable provider.
- **No reference editing:** generate only decorative assets, then composite real
  captures and exact text locally. Explain the reduced enhancement path before
  executing it; do not send a scaffold as an ignored parameter.

When a limit blocks the planned set, present the actual constraint and available
choices. Provider changes remain the user's decision. An authentication, rate,
service, or timeout error is not permission to route to a different vendor.
