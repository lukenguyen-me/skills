---
name: appstore-screenshots
description: Create benefit-led App Store marketing screenshots from an app repository. Discover and run existing screenshot automation, pair real app captures with benefits, and enhance consistent layouts through Gemini, GPT Image, Grok, or a custom image provider.
license: MIT
---

# App Store screenshots

Create a cohesive screenshot set that communicates why someone should download
the app. Follow the workflow below: resume, discover benefits, capture the real
app, assess and pair captures, scaffold, enhance, review, and export.

Inspired by Adam Lyttle's
[aso-appstore-screenshots](https://github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots).
The benefit discovery, scaffold → enhance, and first-approved style reference
processes are retained under the included [MIT license](LICENSE).

## 1. Resume from saved evidence

Use the requested app's repository and read its applicable instructions. Resolve
this skill's helpers relative to its installed directory, never a hardcoded
Claude or Codex home path.

Use `screenshots/aso/` in the app repository unless an existing output convention
or user preference establishes another location. Keep a `state.json` there using
the fields in [references/state.md](references/state.md). Read existing state
before analysis. Reuse earlier ASO memory if available, importing relevant facts
with their provenance; the workflow must also work without an agent memory API.

Summarize saved benefits, capture coverage, pairings, provider, brand colour, and
approved outputs. Check that referenced files exist and that captures still
represent the current UI. Resume the first incomplete or stale phase. Honour
requests to change one item without restarting the set. An earlier approval in
this task is sufficient; ask only for missing decisions.

## 2. Discover the core benefits

Inspect UI screens, models, onboarding, premium features, metadata, marketing
copy, and README files. Establish the app, audience, unique value, and user
problems from source. For monorepos, resolve the target app before capture.
Ask focused questions only where audience or positioning remains unclear.

Draft three to five benefits, adjusted for the app's actual scope. Each headline
starts with a strong action verb, describes a specific outcome, and is supported
by a screen the app can show. Order them as a story, with the strongest reason
to download first. Explain each recommendation briefly. Let the user revise and
confirm the benefits before locking the capture plan. Save the wording and order.
While awaiting a new decision, continue independent repository/tool discovery.

## 3. Discover and run screenshot automation

Read [references/capture.md](references/capture.md) before choosing a capture
method. Inspect the repository for launch commands, screenshot scripts, UI tests,
project verification skills, fixtures, deep links, and simulator/device controls.
Prefer a working project workflow. Check the actual installed tools and their
help/configuration; a test framework dependency alone does not prove a runnable
capture workflow exists.

For each benefit, record the exact screen, useful data state, navigation route,
device, locale, appearance, readiness assertion, and output path. Execute the
available workflow to open the app, reach those states, and save captures. Add a
small capture recipe using an existing harness when navigation needs adaptation.
Use isolated local/demo data and existing sample-content hooks. Retake poor
captures through that same automation before involving the user.

Only request manual screenshots after discovery and a concrete attempt establish
that automation is unavailable or blocked. Identify the missing prerequisite or
failed step and ask for the smallest intervention that enables progress. Existing
user-provided captures can be reused after inspection; they do not require retakes
solely to prove automation.

Completion: every benefit has a real, inspected capture or a recorded blocker,
with reproducible commands and observed results. A planned path is not a capture.

## 4. Assess and pair

View every candidate. Record the screen, strengths, problems, and verdict:
**Great**, **Usable**, or **Retake**. Look for populated realistic content, benefit
relevance, readable hierarchy, consistent appearance, and a clean status bar.
Retake empty/loading states, debug overlays, clipped content, and distracting
permissions or login dialogs. Avoid settings/onboarding unless they directly
demonstrate a confirmed benefit.

Recommend one Great/Usable capture per benefit with a short reason. Prefer
distinct captures. Present the pairings for confirmation and save the approved
mapping. A missing suitable capture returns to the automated capture phase.

## 5. Choose the image provider and visual specification

Read [references/providers.md](references/providers.md). Discover connected
image tools and usable API adapters. If no selection already exists, ask the user
to choose **Gemini**, **GPT Image**, **Grok**, or another provider, showing which
are ready and which need setup. Record the chosen provider, model, transport,
capabilities, and variant count. Keep that selection on resume. Never silently
switch providers when a call fails. A prompt-only model is usable for separate
decorative assets; reference editing is required for full scaffold enhancement.

Read [references/design.md](references/design.md) for layout, prompt templates,
helper commands, and export checks. Infer one background colour from brand assets
and the captures, explain the choice, and permit an override. Use one font and
fixed text sizes across the set. Confirm only unresolved display/locale targets;
check Apple's current specifications rather than treating old size tables as
exhaustive. Configure layout for the supported generation aspect ratio and final
crop before scaffolding so text and important UI survive export.

## 6. Scaffold, enhance, and review

1. Compose deterministic scaffolds using the bundled helper or a compatible
   existing composer. They anchor the wording, brand colour, device placement,
   and real capture. Inspect them internally; user review starts with enhanced
   export-sized candidates.
2. Generate three variants for the first pairing unless the user set another
   count. Use parallel calls when the selected transport supports them within its
   limits. Save each output locally through the provider adapter. Keep request
   files and metadata free of credentials.
3. Immediately normalize each candidate to its target dimensions and inspect
   the **exported** files. Reject altered headlines, invented UI/data, clipping,
   unreadable text, or brand/layout drift. Ask the user to choose among valid
   candidates or give revisions. If all fail, correct the prompt/layout and make
   a bounded retry; stop repeated failed generation with the concrete issue.
4. Save the approved export to `final/<target>/<locale>/01-<benefit>.png` and
   record it as the style reference. Later calls include their own scaffold plus
   this first approved image. Revisions also include the selected candidate when
   the provider supports three references. Use the capability fallback in the
   provider reference if it accepts fewer inputs.
5. Repeat for remaining pairings, preserving approvals and saving state after
   every capture, selection, generation result, and approval. A changed headline,
   capture, brand, or style marks only dependent outputs stale.

## 7. Deliver

Verify the complete set's order, consistent typography/device/background,
faithful UI, exact dimensions, RGB PNG/JPEG format, and absence of transparency.
Create a side-by-side showcase from the approved files. Add a link only if the
user supplied or the repository established it; avoid the inspiration author's
personal branding. Report the final directory, display targets, provider/model,
and any incomplete items. Keep raw captures and working variants outside `final/`.

The skill prepares files. Store upload or publishing requires a separate request.
