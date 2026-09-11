---
name: develop-feature
description: Implement a parent spec through its ordered child tickets, one child at a time on one feature branch, and stop at human QA. Use for develop-feature or continuing an in-progress parent spec with child tickets.
---

# Develop feature (Codex runtime)

Codex adapter. **Strategy is [references/lifecycle.md](references/lifecycle.md)** — read it before every stage. This file only covers how Codex runs that strategy.

## Runtime

Use **gpt-5.6-sol**: **xhigh** for this orchestrator, **high** for every worker. A skill cannot change the invoking session; launch Codex with those settings (see [README.md](README.md#codex)). When `spawn_agent` allows overrides, set `model: "gpt-5.6-sol"`, `reasoning_effort: "high"`, `fork_turns: "none"`. If the runtime cannot select worker high, stop and say so rather than silently inheriting xhigh.

Delegate each stage to a subagent and wait. Children are strictly sequential. Nested agents are allowed only as `/implement`, `/tdd`, or `/code-review` require, at the same worker model and high effort.

Pass workers the parent spec/ref, branches, current child, helper path, config, and prior results. Require `status` and `summary`. Failed or missing output is a failure.

Helper: [scripts/git_state.py](scripts/git_state.py) resolved from this skill directory (or `helper_path` if given). Cwd is the product repo.

Config: `.codex/develop-feature.toml`, else `.grok/develop-feature.toml`.

Args: ticket from text or `{"ticket":"172","mode":"develop"}`. Aliases: `parent`, `query`, `objective`. Modes: `develop` (default), `plan` (`dry-run` / `dry_run` / `dryrun`), `smoke`.

## Run

Follow lifecycle.md stages:

1. **Discover** (read-only except helper `info` / `state-read`).
2. If `plan`: return `PLAN` and stop.
3. **Prepare**.
4. **Each unfinished child**, in order: `/implement` as in lifecycle.md Child. Skip `integrated` children.
5. Return `READY FOR HUMAN QA` (no extra final verify or review).

## Smoke

Sequential workers only: prepare → SMOKE-1-1 implement → SMOKE-1-2 implement. Each replies OK with no tools or file edits. Label the result as smoke. No real discovery, git, or state.
