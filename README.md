# skills

A collection of LLM Coding-Agent skills for various tasks and workflows.

## Available Skills

### appstore-submission-content

A skill for generating complete, ready-to-paste App Store Connect text content. Covers all localizable fields (App Name, Subtitle, Description, Keywords, etc.), enforces Apple character rules, detects multi-language support, and outputs structured markdown.

Usage:
```bash
claude /skill:appstore-submission-content
```

### pastbuild-export

A skill for generating JSON exports compatible with [pastbuild.com](https://pastbuild.com) — a platform for preserving and showcasing past project of builders.

Usage:
```bash
claude /skill:pastbuild-export
```

### playstore-submission-content

Generate complete, ready-to-paste Google Play Store text content for Android app submissions. Covers App Title, Short Description, Full Description, and What's New with strict Play Store character and emoji rules enforced. Supports 51 languages and detects multi-language projects automatically.

Usage:
```bash
claude /skill:playstore-submission-content
```

## Adding New Skills

To add a new skill, create a new directory with:
- `SKILL.md` - Skill documentation
- `references/` - Additional documentation (schema, examples, etc.)
- `assets/` - Media files (optional)
- `scripts/` - Utility scripts (optional)

## Learn More

Visit the [Claude Code documentation](https://claude.com/claude-code) to learn about skills and how to use them.
