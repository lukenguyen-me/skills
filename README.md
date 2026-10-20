# skills

A collection of LLM coding-agent skills for various tasks and workflows.

General skills live under `skills/<name>/` in the [Agent Skills](https://agentskills.io/specification) format, so the npm `skills` CLI can list and install them from this repo. The develop-feature skill lives alongside its Grok workflow under `workflows/develop-feature/`.

## Install

```bash
npx skills add lukenguyen-me/skills
```

That command lists every skill in this repo. Pick the ones you want, or install one by name:

```bash
npx skills add lukenguyen-me/skills --skill write-to-human
```

## Available Skills

### prepare-app-icons

Adapt an existing logo or app icon into Apple app icons, Android adaptive launcher
resources, and web favicons. Checks current official platform guidance, preserves
the artwork, and handles each platform's spacing, masks, transparency, and export
formats. Includes a local Python/Pillow exporter, previews, and optional PWA and
Google Play listing assets. Apple guidance covers Icon Composer and platform
catalogs; the bundled exporter supplies an iOS/iPadOS catalog and Composer layers.
Optional artwork editing supports GPT Image, Gemini, Grok, connected image tools,
and custom provider bridges. Provider output preserves transparency and passes
through the local exporter for exact platform geometry.

```sh
npx skills add lukenguyen-me/skills --skill prepare-app-icons
```

Invoke `$prepare-app-icons` in Codex or `/prepare-app-icons` in Claude Code with an
existing image and the target platforms. See [the skill](skills/prepare-app-icons/SKILL.md).

### appstore-screenshots

Create benefit-led App Store screenshots from an app repository, plus one Header
and one Search Results creative image per requested locale for iOS/iPadOS.
Asks whether to prepare all app locales or just one when locale scope is unspecified,
and keeps the user's choice on resume.
Discovers and runs existing screenshot automation, then renders editable artwork
locally through code by default. Works with any coding agent that can run a
renderer. Optional hybrid mode generates decoration and composes exact copy/UI
locally; image-provider mode enhances scaffolds through Gemini, GPT Image, Grok,
or a custom adapter. Supports
placement-specific dimensions and Apple template safe areas, separate asset
review, resuming saved progress, exact-size exports, and a showcase preview.

Inspired by [aso-appstore-screenshots](https://github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots).
See [the skill](skills/appstore-screenshots/SKILL.md) for the workflow and helpers.

```sh
npx skills add lukenguyen-me/skills --skill appstore-screenshots
```

From the app repository, invoke `$appstore-screenshots` in Codex or
`/appstore-screenshots` in Claude Code, or load the skill in another coding agent.
The bundled renderer supports editable layers, device frames, real panel crops,
shadows, and both portrait and landscape canvases. Helpers require Python 3.10+
and Pillow; code mode needs no image-provider key. Optional API adapters use
environment credentials, while connected image tools use existing authentication.

### app-preview-video

Produce a 15–30 second app preview video with motion, captions, music, and
sound effects from an app repository. One `plan.json` drives three cuts from
the same timeline: an App Store preview that meets Apple's specification
(886×1920, H.264 High 4.0, 11 Mbps, AAC 256k), a Google Play preview for
YouTube with captions, and a 1920×1080 landing-page hero with a 3D device
mockup. Real screen recordings are the footage for store cuts; code-drawn mock
screens cover storyboards and landing pages before a build exists. Bundled
music and effects are synthesized, so they carry no licensing risk.

See [the skill](skills/app-preview-video/SKILL.md) and the
[Ripple example](skills/app-preview-video/examples/ripple/plan.json).

```sh
npx skills add lukenguyen-me/skills --skill app-preview-video
```

The render engine is an HTML overlay page captured frame by frame through
Chrome, then encoded by ffmpeg. It needs Node 22+, ffmpeg, and
[agent-browser](https://github.com/vercel-labs/agent-browser) or any Chrome
with a remote debugging port. No npm install and no video framework license.

### luke-mode

Coordinate engineering requests with playbooks, compatible installed skills, and
verified outcomes. Invoke explicitly with `$luke-mode` in Codex or `/luke-mode`
in Cursor Cloud and Claude Code. Luke Mode is maintained in this repository.

Install only `luke-mode`. It carries two bundle routes:

- [setup](skills/luke-mode/playbooks/setup.md): install missing dependencies,
  configure model roles, and set up the current repository.
- [sync](skills/luke-mode/playbooks/sync.md): update Luke's dependencies to a
  newer upstream tag.

Full setup installs the Matt and PStack skills listed in
[dependencies](skills/luke-mode/references/dependencies.md), and only those.
Their upstream files remain the source of truth. Installing verification
workflows makes them available; creating a project's `verify-<app>` skill remains an explicitly
requested action.

Run `$luke-mode autopilot <request>` to carry a change to a draft PR without
check-ins. Luke records the decisions it made in the PR. For changes you can
see, the PR shows before and after screenshots or GIFs, stored on a hidden Git
ref that clones never download. `$luke-mode autopilot issue #N` takes a triaged
ticket as its only input, and `$luke-mode local-verify` checks cloud PRs on your
machine's devices before they go to review.

Ask Luke to implement a ticket or spec. The Implement playbook resolves the
target: a parent spec with implementation children automatically selects
[whole-spec mode](skills/luke-mode/references/implement-spec.md); an individual
ticket keeps its own scope. This mode belongs to Luke and uses permitted testing
and review primitives, so it does not need Matt's separate `implement-spec`.
To select Matt's original workflow explicitly, use
`$luke-mode implement-spec <spec-path-or-issue>` (Cursor: `/luke-mode implement-spec`).
That choice requires his installed workflow and dependencies; run
`$luke-mode sync` when their installation or refresh is requested.

Install in the project, for every agent you use:

```sh
npx skills add lukenguyen-me/skills --skill luke-mode --agent codex claude-code
```

Then run setup from the project:

```text
$luke-mode setup
```

Setup installs missing dependencies through the Skills CLI at project scope,
then configures models and the repository. Run `$luke-mode sync` to update
them later. In Cursor and Claude Code, use `/` instead of `$`.

See the [Luke Mode guide](docs/luke-mode/README.md) for Cursor Cloud,
setup, model roles, and verification coverage.

### mac-dev-storage-cleanup

Free disk space on a developer Mac without touching in-progress work. Scans
read-only, reports sizes by tier (Safe, Old-only, Ask first, Report only), and
deletes only what the user confirms. Covers Xcode (DerivedData, Archives,
DeviceSupport, simulators), Gradle, Android SDK and emulators, npm, pnpm,
Homebrew, and CocoaPods caches, Docker, agent git worktrees, and project build
artifacts. Uses official commands where they exist and otherwise the Trash, and
empties the Trash only on request; never `rm -rf` or `sudo`. Projects with recent, dirty, stashed, or unpushed work
stay untouched, and AI chat history is report-only. The projects root comes from
`PROJECTS_ROOT` (colon-separated), the user, or common folders. Scripts run on
macOS `/bin/bash` 3.2 and log to `~/Library/Logs/dev-cleanup.log`.

```sh
npx skills add lukenguyen-me/skills --skill mac-dev-storage-cleanup
```

Invoke `$mac-dev-storage-cleanup` in Codex or `/mac-dev-storage-cleanup` in Claude
Code. See [the skill](skills/mac-dev-storage-cleanup/SKILL.md).

### store-release

Prepare App Store and Play Store release content for a public version. Inspects the source-verified change since the last release, writes version notes, refreshes listing copy when the release makes it inaccurate, and syncs version configuration when those files exist.

Replaces `appstore-release-notes`, `appstore-submission-content`, and `playstore-submission-content`.

Usage:
```bash
claude /skill:store-release
```

### commit-message

Generate two conventional commit message options from staged changes and recent commit history: one multi-line format and one concise one-line version.

Usage:
```bash
claude /skill:commit-message
```

### pr-summary

Add a concise Before/After/Solution block at the top of every new or refreshed pull request description. Use alongside pr-writer when that skill is available.

Usage:
```bash
claude /skill:pr-summary
```

### write-to-human

Write every message to a human in Simplified Technical English (ASD-STE100). Lead with business impact and how the operation changes. Use a concrete example when a concept is complex. Applies to the whole conversation, not only reports or code.

Usage:
```bash
claude /skill:write-to-human
```

## Agent workflows

This repo also ships workflows under `workflows/`. Grok uses the Rhai entry point; Codex uses the Agent Skill entry point with native subagents.

### develop-feature

Implement ordered child tickets onto one parent feature branch, strictly one child at a time, and stop at human QA.

```bash
./workflows/develop-feature/install.sh --user
./workflows/develop-feature/install.sh --codex --user
```

Then, in the product repository:

```text
/develop-feature {"ticket":"<parent-spec>"}
```

For Codex, invoke `$develop-feature {"ticket":"<parent-spec>"}` with `gpt-5.6-sol`: **xhigh** for the orchestrator, **high** for workers.

See [workflows/develop-feature/README.md](workflows/develop-feature/README.md).

## Adding New Skills

Create a directory under `skills/`:

```
skills/<skill-name>/
├── SKILL.md          # Required: YAML name + description, then instructions
├── references/       # Optional: docs loaded on demand
├── scripts/          # Optional: helper scripts
└── assets/           # Optional: templates and media
```

`name` in the `SKILL.md` frontmatter must match the folder name.

## Learn More

- [Agent Skills specification](https://agentskills.io/specification)
- [skills CLI](https://github.com/vercel-labs/skills)
- [Claude Code skills](https://claude.com/claude-code)
