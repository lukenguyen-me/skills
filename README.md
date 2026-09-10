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

### appstore-release-notes

Generate compact App Store release notes from git history, tags, commits, and changed files. Outputs clear hyphen bullets labeled as Feature, Fix, or Improvement.

Usage:
```bash
claude /skill:appstore-release-notes
```

### appstore-submission-content

A skill for generating complete, ready-to-paste App Store Connect text content. Covers all localizable fields (App Name, Subtitle, Description, Keywords, etc.), enforces Apple character rules, detects multi-language support, and outputs structured markdown.

Usage:
```bash
claude /skill:appstore-submission-content
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

### playstore-submission-content

Generate complete, ready-to-paste Google Play Store text content for Android app submissions. Covers App Title, Short Description, Full Description, and What's New with strict Play Store character and emoji rules enforced. Supports 51 languages and detects multi-language projects automatically.

Usage:
```bash
claude /skill:playstore-submission-content
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
