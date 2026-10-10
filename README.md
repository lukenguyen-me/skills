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

### luke-mode

Coordinate engineering requests with playbooks, compatible installed skills, and
verified outcomes. Invoke explicitly with `$luke-mode` in Codex or `/luke-mode`
in Cursor Cloud. Luke Mode is maintained in this repository.

Luke Mode has four companion skills, installed beside the main skill:

- [setup-luke-mode](skills/setup-luke-mode/SKILL.md): configure Luke's model roles
  and check Matt's per-repository setup. Invoke `$setup-luke-mode` or `$luke-mode setup`.
- [sync-matt-pocock-skills](skills/sync-matt-pocock-skills/SKILL.md): refresh Matt's
  full upstream skill set, including new skills. Invoke `$sync-matt-pocock-skills`
  or `$luke-mode sync Matt's skills`.
- [create-verification-skill](skills/create-verification-skill/SKILL.md): create
  and prove a project-local app verification skill and feature map, adapted from
  PStack. Invoke `$create-verification-skill` or `$luke-mode create-verification-skill`.
- [maintain-verification-skill](skills/maintain-verification-skill/SKILL.md): check
  and repair an existing verification skill against source and live behavior,
  adapted from PStack. Invoke `$maintain-verification-skill` or
  `$luke-mode maintain-verification-skill`.

The verification companions retain explicit-only invocation. Installing them
makes the workflows available; creating a project's `verify-<app>` skill is a
separate requested action.

Ask Luke to implement a ticket or spec. The Implement playbook resolves the
target: a parent spec with implementation children automatically selects
[whole-spec mode](skills/luke-mode/references/implement-spec.md); an individual
ticket keeps its own scope. This mode belongs to Luke and uses permitted testing
and review primitives, so Matt's separate `implement-spec` installation is optional.
To select Matt's original workflow explicitly, use
`$luke-mode implement-spec <spec-path-or-issue>` (Cursor: `/luke-mode implement-spec`).
That choice requires his installed workflow and dependencies; use the sync
companion when their installation or refresh is requested.

Install all five globally for Codex:

```sh
npx skills add lukenguyen-me/skills \
  --skill luke-mode setup-luke-mode sync-matt-pocock-skills \
  create-verification-skill maintain-verification-skill --agent codex --global
```

See the [Luke Mode guide](docs/luke-mode/README.md) for Cursor Cloud packaging,
setup, model roles, and verification coverage.

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
