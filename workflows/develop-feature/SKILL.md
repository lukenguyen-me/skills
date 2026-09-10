---
name: develop-feature
description: Implement a parent spec through its ordered child tickets, one child at a time on one feature branch, and stop at human QA. Use for develop-feature or continuing an in-progress parent spec with child tickets.
---

# Develop feature (Codex)

Run the same Discover → Prepare → Child → Final sequence as the Grok workflow. Accept a parent issue number, URL, or local spec path, either as text or as `{"ticket":"172","mode":"develop"}`. `parent`, `query`, and `objective` are aliases for `ticket`. Default to `develop`; accept `plan` (also `dry-run`, `dry_run`, `dryrun`) and `smoke`.

## Agents and reasoning

Use **gpt-5.6-sol** for every agent: **xhigh** for the orchestrator, **high** for all workers, including implementation, verification, repair, and review. A skill cannot change the invoking session's model or effort; launch with these settings or select them in Codex before running. See [README.md](README.md#codex) for installation and launch instructions.

Delegate each stage below to a Codex subagent and wait for its result before proceeding. When `spawn_agent` exposes overrides, set `model: "gpt-5.6-sol"`, `reasoning_effort: "high"`, and `fork_turns: "none"`; supply the stage context explicitly. If the runtime uses configured agent roles instead, use a role with that model and effort. If neither mechanism can select the required worker settings, stop and report the missing runtime support rather than silently inheriting xhigh. Resume the implementation worker for repairs when available; otherwise give a fresh worker the implementation and verification evidence.

Use the same repository and workspace for all stages. Children run strictly sequentially: child N+1 starts only after child N is verified, committed, and integrated. Workers do their assigned stage themselves; only the implement/tdd/code-review skills may require nested agents, which must use the same worker model and high effort. Release completed workers when the runtime supports it so later stages have capacity.

Pass every worker the parent spec/ref, base and parent branches, current child/ref and position (when applicable), helper path, configuration, verification commands, and relevant previous results. Require `status` and `summary`, with command evidence, changed files, branch/SHA, and `stop_reason` or blocking issues as applicable. Missing/failed agent output is a failure, never a pass.

## Shared boundaries and resources

Stop on product ambiguity, missing dependencies/credentials, unexpected dirty state, unsafe merges, or required human intervention. Preserve work and report the blocker. Never merge to the base/protected branches, open a PR, deploy, or release. Push only if a test cannot run without it. These boundaries also apply to nested skills.

Use the bundled [scripts/git_state.py](scripts/git_state.py), resolving its absolute path from this skill directory, and run it with the target repository as the working directory. Honor an explicit `helper_path` argument. The helper deliberately shares `.grok/develop-feature-state/<parent-id>.json` with Grok so either agent can resume the same feature. Keep generated state out of commits and account for it when checking tree cleanliness (use the repository's ignore convention or a local `.git/info/exclude` entry in develop mode).

Read project configuration from `.codex/develop-feature.toml`, falling back to `.grok/develop-feature.toml`; use one file, with Codex taking precedence. See [examples/develop-feature.toml.example](examples/develop-feature.toml.example) for keys. Read [references/lifecycle.md](references/lifecycle.md) for ticket shapes and the shared lifecycle.

## 1. Discover

Delegate read-only discovery. Read the full parent, linked children, `docs/agents/issue-tracker.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `CONTEXT.md`, project config, build/test scripts, and CI when present. Use the configured tracker (GitHub `gh`, GitLab `glab`, or local Markdown); children may be native sub-issues, a task list, or tickets with a `Parent` section. Run helper `info` and `state-read --parent <id>`.

Return parent ID/title/ref, base branch, parent branch, `child_branches`, verification commands, integration commands, config notes, and the complete ordered children with IDs/titles/refs/status/blockers. Order topologically by `Blocked by`, then numeric/lexical ID. If there are no children, treat the parent as the single child. Stop on missing parent, unresolvable order, or ambiguous requirements.

Infer base from `origin/HEAD`, then `main`/`master`/`develop`, checking repo instructions. Use configured branch templates or `feat/{id}` for the parent and `feat/{parent-id}-{child-id}` for optional child branches. Parent must differ from base. Default `child_branches` to false. Prefer verification from ticket criteria, then project config, agent instructions, repo scripts, and CI. Separate cheap child checks from full integration/e2e checks; infer the stack rather than assuming a package manager.

Keep every child in the list. Mark finished children `integrated` if the saved state records integration, the tracker is closed/local status is resolved/completed/done/closed, or git history clearly shows their work on the parent. Open/ready-for-agent/claimed/in-progress alone is not completion. Stop if overlapping commits make completion uncertain. Reuse the existing parent branch and its commits.

For `plan`, return `PLAN` with parent/base/branch, ordered children and completion status, and inferred checks; stop without git or product writes.

## 2. Prepare

Delegate parent preparation. Run:

```text
python3 <helper> assert-not-base --branch <parent_branch> --base <base_branch>
python3 <helper> prepare-parent --parent <parent_id> --branch <parent_branch> --base <base_branch>
```

Proceed only when the intended parent is checked out, retaining any existing commits, and the workspace is ready for the first unfinished child.

## 3. Each child, in order

Skip children already integrated. For each remaining child:

1. **Implement.** Delegate exactly this child from the current parent tip. Load the first available implement skill from project `.agents/skills/implement/SKILL.md`, project `.codex/skills/implement/SKILL.md`, project `.grok/skills/implement/SKILL.md`, user `~/.agents/skills/implement/SKILL.md`, `${CODEX_HOME:-~/.codex}/skills/implement/SKILL.md`, then `~/.grok/bundled/skills/implement/SKILL.md`. Also accept an implement skill supplied by the session. If unavailable, stop and report the missing skill. Follow its tdd, tests/typecheck, code-review, and commit flow, within the shared boundaries. Load configured implementation/review skills when available. Normally commit on the parent. If `child_branches` is true, first run `start-child --branch <child_branch> --parent-branch <parent_branch> --parent <parent_id> --child <child_id>` with the helper and commit there. Require successful implementation with committed work.
2. **Verify.** A separate worker runs the child's acceptance checks and discovered commands. Require executed evidence, or a documented absence of automated checks plus diff inspection against criteria. Stop if a required child check needs human action.
3. **Repair if needed.** On verification failure, send the evidence to the implementer and repeat the same implement/tdd/tests/code-review/commit flow, then independently reverify. Allow at most **two repair attempts**. On exhaustion, ask for the code/environment fix and pause; after the user resolves it, reverify once. Stop if that still fails. Never advance on failure.
4. **Integrate.** Delegate integration. With child branches enabled, run `integrate-child --branch <child_branch> --parent-branch <parent_branch> --parent <parent_id> --child <child_id> --delete-child`. Otherwise run `state-mark --parent <parent_id> --child <child_id> --status integrated`. Prefix both with `python3 <helper>`. Require the child committed on the parent and a clean product working tree before advancing. Record its result in the report.

## 4. Final

Delegate integration verification against the full parent diff from base. Run the discovered integration/e2e commands and child verification commands if they did not already cover the full suite. On failure, allow **one integration repair/commit cycle**, then reverify. If still failing, pause for a human fix and reverify once on resumption; stop if still failing.

A manual-only final check may be deferred to human QA when the ticket did not demand it as an automated gate. Missing environment for a required automated gate remains a blocker. List every deferred check explicitly.

Delegate a **fresh final reviewer** to read the original parent spec and full diff, checking parent-level gaps, contradictory child implementations, missing feature tests, regressions, and unsafe extra scope. Style nits do not block. On blocking findings, allow **one spec repair/commit cycle**, rerun integration verification, and obtain a fresh review. Stop if blockers remain or a review cannot be completed.

Return `READY FOR HUMAN QA` only after these gates pass (apart from explicitly deferred manual QA). Include parent ID/title/ref, parent/base branches, each child's integrated/skipped status, verification evidence, final review result, and manual checks. Stop here; the human handles QA and the PR/base merge.

## Smoke mode

Exercise only sequential delegation: prepare → synthetic child SMOKE-1-1 implement/verify/review → synthetic child SMOKE-1-2 implement/verify/review → final review. Each worker replies OK without tools or file edits. Use the same model/effort settings. Stop on any failure; otherwise report `READY FOR HUMAN QA` clearly labeled as a smoke result with no product changes. Skip real discovery, git operations, and state writes.

## Resume

Re-invoking this skill on the same parent repeats discovery and skips completed children using the shared state, tracker, and git evidence. Continue from the existing parent tip. For a same-session verification pause, continue at its reverify gate once the blocker is resolved. Include the current stage and blocker in any `STOPPED` report.
