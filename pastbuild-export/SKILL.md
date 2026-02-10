---
name: pastbuild-export
description: Generate Past Build project JSON for portfolio import. Use when users want to export their software projects from source code to pastbuild.com. Analyzes codebase to extract project name, description, tech stack, and structure for the Past Build import format.
---

# Past Build Export

Generate valid JSON for importing software projects into pastbuild.com - a platform for preserving and showcasing past builds.

## Quick Start

When a user asks to "export to Past Build", "create Past Build JSON", or similar:

1. **Analyze the codebase** - Look for package.json, README, source files to extract:
   - Project name
   - Description/summary
   - Tech stack (dependencies, frameworks)
   - Project structure and features

2. **Generate the JSON** using the schema below

3. **Present the output** for the user to paste into Past Build's JSON import

## JSON Schema

```json
{
  "version": 1,
  "name": "Project Name",
  "description": "Brief description of what the project does",
  "projectStatus": "ongoing" | "finished",
  "projectDate": "YYYY-MM-DD",
  "sections": [
    {
      "id": "uuid-v4",
      "title": "Section Title",
      "subtitle": "Optional subtitle",
      "order": 0,
      "media": []
    }
  ],
  "links": [
    {
      "id": "uuid-v4",
      "text": "GitHub",
      "url": "https://github.com/..."
    }
  ],
  "exportedAt": "2024-01-01T00:00:00.000Z"
}
```

## Field Requirements

| Field | Required | Description |
|-------|----------|-------------|
| `version` | Yes | Must be `1` |
| `name` | Yes | Project name |
| `description` | Yes | Project description (1-2 sentences) |
| `projectStatus` | No | `"ongoing"` or `"finished"` (default: `"finished"`) |
| `projectDate` | No | When the project was built (YYYY-MM-DD format) |
| `sections` | Yes | Array of sections describing the project |
| `links` | No | External links (GitHub, website, demo) |
| `exportedAt` | Yes | ISO timestamp of generation |

## Section Structure

Each section should cover a distinct aspect of the project:

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Tech Stack",
  "subtitle": "Libraries and frameworks used",
  "order": 0,
  "media": []
}
```

**Suggested section titles:**
- Overview / Introduction
- Tech Stack
- Features
- How It Works
- Challenges & Solutions
- Key Learnings
- Demo / Screenshots
- Future Improvements

## Extracting Project Info

### Common Sources

| Source | What to Extract |
|--------|-----------------|
| `package.json` / `pyproject.toml` | Name, version, dependencies (tech stack) |
| `README.md` | Description, features, setup instructions |
| `Cargo.toml`, `go.mod` | Name, dependencies |
| Source files | Architecture patterns, key features |

### Project Status Heuristics

- **`ongoing`**: Actively maintained, recent commits, planned features
- **`finished`**: Completed project, no active development, side project that reached its goals

### Project Date

Estimate from:
- Git history (`git log --reverse --format=%ai`)
- File creation dates
- README mentions ("built in 2023")

## Example Outputs

### Simple Web App

```json
{
  "version": 1,
  "name": "Task Tracker",
  "description": "A minimal task management app with drag-and-drop reordering and local storage sync",
  "projectStatus": "finished",
  "projectDate": "2024-06-15",
  "sections": [
    {
      "id": "overview-section",
      "title": "Overview",
      "subtitle": "What this project does",
      "order": 0,
      "media": []
    },
    {
      "id": "tech-section",
      "title": "Tech Stack",
      "subtitle": "Built with",
      "order": 1,
      "media": []
    },
    {
      "id": "features-section",
      "title": "Features",
      "subtitle": "Key capabilities",
      "order": 2,
      "media": []
    }
  ],
  "links": [
    {
      "id": "github-link",
      "text": "GitHub Repository",
      "url": "https://github.com/username/task-tracker"
    }
  ],
  "exportedAt": "2024-06-15T12:00:00.000Z"
}
```

### CLI Tool

```json
{
  "version": 1,
  "name": "Image Optimizer CLI",
  "description": "Batch image compression tool with WebP conversion and smart quality detection",
  "projectStatus": "finished",
  "projectDate": "2024-03-20",
  "sections": [
    {
      "id": "what-it-does",
      "title": "What It Does",
      "subtitle": "Problem solved",
      "order": 0,
      "media": []
    },
    {
      "id": "how-it-works",
      "title": "How It Works",
      "subtitle": "Technical approach",
      "order": 1,
      "media": []
    }
  ],
  "links": [
    {
      "id": "github",
      "text": "Source Code",
      "url": "https://github.com/username/img-opt"
    },
    {
      "id": "npm",
      "text": "NPM Package",
      "url": "https://npmjs.com/package/img-opt"
    }
  ],
  "exportedAt": "2024-03-20T09:30:00.000Z"
}
```

## UUID Generation

Generate UUIDs for `id` fields. Python example:

```python
import uuid
print(str(uuid.uuid4()))
# Output: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

## Tips for Quality Output

1. **Read multiple sources** - Check package.json, README, and source files for complete picture
2. **Keep descriptions concise** - 1-2 sentences that capture the essence
3. **Use consistent section ordering** - Overview → Tech Stack → Features → Details
4. **Include relevant links** - GitHub, live demo, documentation
5. **Match user's framing** - Use terminology from their project

## Resources

- **Schema Reference**: See [SCHEMA.md](SCHEMA.md) for complete type definitions
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for more output examples
