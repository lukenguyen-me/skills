# Agent workflows

Reusable workflows for Grok Build and Codex. Grok runs Rhai workflows; Codex runs the equivalent skill with native subagents.

| Workflow | Command | What it does |
| --- | --- | --- |
| [develop-feature](./develop-feature/) | Grok: `/develop-feature`; Codex: `$develop-feature` | Sequential child-ticket implementation onto a parent feature branch; stops at human QA |

```bash
./develop-feature/install.sh --user
./develop-feature/install.sh --codex --user
```
