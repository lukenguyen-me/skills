---
name: appstore-screenshots
description: Create App Store screenshots and Header and Search Results creative assets from an app repository. Capture real UI and render editable designs locally through code, with optional hybrid or image-provider modes. Use with any coding agent for a complete store image set or either creative placement alone.
license: MIT
---

# App Store screenshots

Create a cohesive store image set that communicates why someone should download
the app. A full iOS/iPadOS run includes the screenshot story plus **one Header
image and one Search Results image per requested locale**. Honour a narrower
request, including asset-only revisions. For other platforms, record the creative
placements as not applicable after checking current Apple support.

Inspired by Adam Lyttle's
[aso-appstore-screenshots](https://github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots).
The benefit discovery and first-approved style reference processes, plus the
optional scaffold → enhance path, are retained under the included [MIT license](LICENSE).

Default to local code rendering. Any coding agent that can write design code and
execute a renderer can prepare the files; image-generation tools are optional.

## 1. Resume from saved evidence

Use the requested app's repository and read its applicable instructions. Resolve
this skill's helpers relative to its installed directory, never a hardcoded
Claude or Codex home path.

Use `screenshots/aso/` in the app repository unless an existing output convention
or user preference establishes another location. Keep a `state.json` there using
the fields in [references/state.md](references/state.md). Read existing state
before analysis. Reuse earlier ASO memory if available, importing relevant facts
with their provenance; the workflow must also work without an agent memory API.

Summarize saved benefits, capture coverage, pairings, rendering mode, brand colour,
requested asset types, and approved outputs. Check that referenced files exist
and that captures still represent the current UI. Resume the first incomplete
or stale phase. Honour requests to change one item without restarting the set.
An earlier approval in this task is sufficient; ask only for missing decisions.

Resolve locale scope before planning captures or artwork. Honour locales explicitly
requested in the session or a saved user selection. Otherwise ask: **"Should I
prepare assets for all of this app's App Store locales, or just one? If just one,
which locale?"** Show detected listing locales as choices when available; use
repository metadata to identify the app's locale set, not to select it for the user.
An existing localized output alone does not establish a user choice.

Wait for the choice before locale-dependent capture, copy, or image generation;
continue benefit and tool discovery while it is pending. For all locales, resolve
the exact app locale list; for one locale, resolve its identifier. Save the mode,
locale list, and user-choice provenance in `asset_scope`, and apply that scope to
screenshots, Header, and Search Results. Reuse it on resume unless the user changes it.

## 2. Discover the core benefits

Inspect UI screens, models, onboarding, premium features, metadata, marketing
copy, and README files. Establish the app, audience, unique value, and user
problems from source. For monorepos, resolve the target app before capture.
Ask focused questions only where audience or positioning remains unclear.

For a screenshot story, draft three to five benefits, adjusted for the app's
actual scope. Each headline starts with a strong action verb, describes a specific
outcome, and is supported by a screen the app can show. Order them as a story, with the strongest reason
to download first. Explain each recommendation briefly. Let the user revise and
confirm the benefits before locking the capture plan. Save the wording and order.
While awaiting a new decision, continue independent repository/tool discovery.

Record a Header concept and a Search Results concept grounded in the same
positioning when those placements are in scope. For asset-only work, reuse or
establish only the positioning needed for those briefs; capture only the UI
needed for the requested outputs.

## 3. Discover and run screenshot automation

Run this phase when the requested outputs need new UI captures.

Read [references/capture.md](references/capture.md) before choosing a capture
method. Inspect the repository for launch commands, screenshot scripts, UI tests,
project verification skills, fixtures, deep links, and simulator/device controls.
Prefer a working project workflow. Check the actual installed tools and their
help/configuration; a test framework dependency alone does not prove a runnable
capture workflow exists.

For each benefit needing a real capture, record the exact screen, useful data
state, navigation route, device, locale, appearance, readiness assertion, and
output path. Execute the available workflow to open the app, reach those states,
and save captures. Add a
small capture recipe using an existing harness when navigation needs adaptation.
Use isolated local/demo data and existing sample-content hooks. Retake poor
captures through that same automation before involving the user.

Only request manual screenshots after discovery and a concrete attempt establish
that automation is unavailable or blocked. Identify the missing prerequisite or
failed step and ask for the smallest intervention that enables progress. Existing
user-provided captures can be reused after inspection; they do not require retakes
solely to prove automation.

Completion: every planned UI source has a real, inspected capture or a recorded
blocker, with reproducible commands and observed results. A planned path is not
a capture.

## 4. Assess and pair

View every candidate. Record the screen, strengths, problems, and verdict:
**Great**, **Usable**, or **Retake**. Look for populated realistic content, benefit
relevance, readable hierarchy, consistent appearance, and a clean status bar.
Retake empty/loading states, debug overlays, clipped content, and distracting
permissions or login dialogs. Avoid settings/onboarding unless they directly
demonstrate a confirmed benefit.

Recommend one Great/Usable capture per screenshot benefit with a short reason.
Record creative capture choices in their briefs. Prefer distinct captures for
the screenshot story. Present the pairings for confirmation and save the approved
mapping. A missing suitable capture returns to the automated capture phase.

## 5. Resolve rendering mode and visual specification

Honour a requested or saved mode; otherwise use **code** without a provider-choice
question. Record the mode, renderer, editable source paths, and variant count
(default three unless already specified) in `rendering` state:

- **Code:** compose the complete artwork locally from exact copy, real captures,
  brand assets, and drawn elements. Read [references/code-rendering.md](references/code-rendering.md).
- **Hybrid:** generate separate decorative assets, then render the final text,
  device, and real UI locally. Read the code-rendering reference and
  [references/providers.md](references/providers.md).
- **Image provider:** retain scaffold enhancement for a requested generative
  finish. Read [references/providers.md](references/providers.md).

Discover a runnable renderer for code/hybrid. The bundled Pillow helper supports
both orientations; existing HTML/CSS/SVG, canvas, or 3D composers are also suitable.
Use project dependencies where possible. Code mode requires neither image-provider
credentials nor an image tool. Select a provider only for hybrid/image-provider
work, reusing earlier selections. Preserve legacy provider runs as described in
the state reference. A failed call or unavailable renderer does not authorize a
mode or vendor change.

Read [references/design.md](references/design.md) for layout, prompt templates,
helper commands, and screenshot export checks. When Header or Search Results
assets are in scope, also read [references/creative-assets.md](references/creative-assets.md)
before planning their layouts. Verify its dated specifications against Apple's
current pages and templates, and save the sources and check date.

Infer one background colour from brand assets and the captures, explain the
choice, and permit an override. Use one font and fixed text sizes within each
screenshot layout. Share brand and font choices with the creative assets while
sizing their content for each placement. Confirm only
unresolved display/locale targets; check Apple's current specifications rather
than treating old size tables as exhaustive. Configure layout for the supported
rendering canvas and any final crop before composing so text and important UI
survive export. Local rendering can use the exact target dimensions directly.

## 6. Render, inspect, revise, and review

Run this phase for the screenshot pairings in scope. Asset-only requests can
proceed directly to phase 7 once their positioning, sources, and rendering tools
are ready.

1. Create editable designs for the first pairing using the saved variant count.
   In code/hybrid mode, render final compositions with distinct, intentional
   design alternatives; hybrid adds only separately generated decorative assets.
   Retain exact copy and genuine UI. In image-provider mode, compose scaffolds
   internally and enhance through the selected adapter using the design reference.
   Keep design sources, asset paths, render commands, and provider request files.
2. Render each candidate locally or save its actual provider result. Inspect it,
   revise the editable design or enhancement prompt, and rerun when needed. A
   successful command alone does not establish visual quality. User review starts
   with finished, inspected candidates at export size.
3. Check each candidate at its target dimensions and normalize when needed;
   exact-size local RGB renders already meet the export format. Inspect the
   **exported** files. Reject altered headlines, invented UI/data, clipping,
   unreadable text, or brand/layout drift. Ask the user to choose among valid
   candidates or give revisions. If all fail, correct the design/prompt and make
   a bounded retry as described in the design reference.
4. Save the approved export to `final/<target>/<locale>/01-<benefit>.png` and
   record it and its editable source as the style reference. In code/hybrid mode,
   reuse its typography, palette, frame, and spacing in later designs. In
   image-provider mode, later calls include their own scaffold and the approved
   image, using the provider reference for reference-count limits.
5. Repeat for remaining pairings, preserving approvals and saving state after
   every capture, selection, render/generation result, and approval. A changed
   headline, capture, brand, or style marks only dependent outputs stale.

## 7. Create Header and Search Results images

Run this phase for creative placements in scope using the static-image recipe in
[references/creative-assets.md](references/creative-assets.md).
Reuse the rendering mode, approved brand treatment, and suitable real captures.
Render dedicated landscape designs with the placement's template safe area.
The local `render` helper accepts these canvases; the portrait `compose` helper
is a screenshot starting layout. Hybrid/provider work follows the selected mode's
recipe. Keep exact copy and real UI authoritative throughout.

Render or generate the saved variant count for each placement, check its export
format, and inspect both the full image and its placement preview.
Review the Header and Search Results candidates separately. Existing approval
covers an unchanged asset; revisions invalidate only dependent outputs. Save one
approved final per requested placement/locale, with its sources, prompt,
dimensions, editable source/render command or provider request, preview evidence,
and approval in `creative_assets` state.

Completion: each requested placement/locale has one inspected, approved static
image or a concrete blocker. Apple submission/review status is separate from
the user's design approval.

## 8. Deliver

Verify the screenshot story's order and consistent typography/device/background.
Check shared brand treatment, faithful UI, placement-specific dimensions/formats,
and absence of transparency across all requested images.
Create a side-by-side showcase from the approved files. Add a link only if the
user supplied or the repository established it; avoid the inspiration author's
personal branding. Report the final directory, display targets, rendering mode,
renderer and editable design paths, provider/model when used, and any incomplete
items. Include the two creative assets and their placement
mapping in a full iOS/iPadOS delivery; list them separately from the ordered
screenshot carousel. Report any App Store Connect previews still pending.
Keep raw captures and working variants outside `final/`.

The skill prepares files. Store upload or publishing requires a separate request.
