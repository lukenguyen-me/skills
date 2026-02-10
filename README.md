# skills

A collection of LLM Coding-Agent skills for various tasks and workflows.

## Available Skills

### pastbuild-export

A skill for generating JSON exports compatible with [pastbuild.com](https://pastbuild.com) — a platform for preserving and showcasing past project of builders.

Usage:
```bash
claude /skill:pastbuild-export
```

## Adding New Skills

To add a new skill, create a new directory with:
- `SKILL.md` - Skill documentation
- `references/` - Additional documentation (schema, examples, etc.)
- `assets/` - Media files (optional)
- `scripts/` - Utility scripts (optional)

## Learn More

Visit the [Claude Code documentation](https://claude.com/claude-code) to learn about skills and how to use them.
