# skills

A collection of LLM coding-agent skills for various tasks and workflows.

Each skill lives under `skills/<name>/` in the [Agent Skills](https://agentskills.io/specification) format, so the npm `skills` CLI can list and install them from this repo.

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

### pastbuild-export

A skill for generating JSON exports compatible with [pastbuild.com](https://pastbuild.com) — a platform for preserving and showcasing past project of builders.

Usage:
```bash
claude /skill:pastbuild-export
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
