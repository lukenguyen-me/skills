# Grok Build workflows

Reusable Grok Build workflows. Install a workflow into `~/.grok/workflows/` (all projects) or `<repo>/.grok/workflows/` (one repo).

| Workflow | Command | What it does |
| --- | --- | --- |
| [develop-feature](./develop-feature/) | `/develop-feature` | Sequential child-ticket implementation onto a parent feature branch; stops at human QA |

```bash
./develop-feature/install.sh --user
```
