# develop-feature strategy

Single source of truth for **what** to do. Grok (`develop-feature.rhai`) and Codex (`SKILL.md`) only differ in **how** they spawn workers. Read this file before Discover, Prepare, each Child, and Final.

## Sequence

```
discover
  → prepare parent branch from base
  → for each child in linearized order:
        /implement (tdd, tests, /code-review, commit on parent)
  → final integration verify
  → final review against the original parent spec
  → READY FOR HUMAN QA
```

Child N+1 starts only after child N is committed on the parent and marked integrated. Never implement two children at once.

There is no per-child verify agent and no per-child PR. `/implement` already typechecks, tests, and code-reviews. After all children, Final checks the original parent spec.

## Boundaries

Merge only onto the parent feature branch (or, if `child_branches` is true, merge a child branch into that parent). Stay off `main`, `master`, `develop`, `trunk`, `production`, and the detected base. Do not open a PR, deploy, or release. Push only when a test cannot run without it.

Stop when an acceptance criterion needs a product guess, a dependency or credential is missing, the tree is unexpectedly dirty, a merge is unsafe, or a required check needs a human. Preserve git state and report the blocker. Never continue on a broken parent.

## Config

Read `.codex/develop-feature.toml` first, then `.grok/develop-feature.toml`. Missing keys are inferred. `child_branches` defaults to false: `/implement` commits on the parent branch. Set it true only for a branch per child.

## Helper

`scripts/git_state.py` (installed next to this file or under `.grok/lib/develop-feature/`). Run it with the product repo as cwd. Shared progress: `.grok/develop-feature-state/<parent-id>.json`.

```text
python3 <helper> info
python3 <helper> state-read --parent <id>
python3 <helper> assert-not-base --branch <parent_branch> --base <base_branch>
python3 <helper> prepare-parent --parent <id> --branch <parent_branch> --base <base_branch>
python3 <helper> state-mark --parent <id> --child <id> --status integrated
# only if child_branches is true:
python3 <helper> start-child --branch <child_branch> --parent-branch <parent_branch> --parent <id> --child <id>
python3 <helper> integrate-child --branch <child_branch> --parent-branch <parent_branch> --parent <id> --child <id> --delete-child
```

## Tickets

Parent spec (`to-spec`): Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope.

Child (`to-tickets`): Parent, What to build, Acceptance criteria, Blocked by.

Tracker from `docs/agents/issue-tracker.md`: GitHub `gh`, GitLab `glab`, or local `.scratch/<feature>/spec.md` plus `.scratch/<feature>/issues/<NN>-<slug>.md`. Children may be native sub-issues, a parent task list, or tickets with `## Parent`. A path argument may be the parent spec file.

## /implement

Load the first implement `SKILL.md` that exists:

1. project `.agents/skills/implement/SKILL.md`
2. project `.codex/skills/implement/SKILL.md`
3. project `.grok/skills/implement/SKILL.md`
4. `~/.agents/skills/implement/SKILL.md`
5. `${CODEX_HOME:-~/.codex}/skills/implement/SKILL.md`
6. `~/.grok/bundled/skills/implement/SKILL.md`

Follow that file (tdd, typecheck/tests, code-review, commit). Spawn nested agents only as implement/tdd/code-review require. Do not implement other children.

## Discover

Done when the return includes parent id/title/ref, base branch, parent branch (not equal to base), `child_branches`, verify and integration commands, and the **complete** ordered child list.

Order by `Blocked by` (topological), then numeric/lexical id. If there are no children, the parent is the only child.

Keep every child in the list. Mark a child `integrated` if any of: state file says integrated; tracker issue closed / local Status is resolved, completed, done, or closed; parent branch git history clearly contains that child's work. Open / ready-for-agent / claimed / in-progress is not done. If overlapping commits make it unclear, stop rather than redo or skip.

Reuse an existing parent branch and its commits. Infer base from `origin/HEAD`, then `main`/`master`/`develop`. Branch template: toml, else `feat/{id}`. Infer verify commands from ticket criteria, toml, AGENTS.md/CLAUDE.md, repo scripts, CI — do not assume a package manager. Put full/e2e commands in integration commands.

Do not edit product files. Helper `info` and `state-read` are allowed.

## Prepare

Done when the parent feature branch is checked out, not reset to base, and the tree is ready for the first unfinished child. Run `assert-not-base` then `prepare-parent`.

## Child

Skip children already `integrated`. For each remaining child, from the current parent tip:

1. Run `/implement` for that child only.
2. Commit on the parent branch (`child_branches` false). If `child_branches` is true: `start-child`, `/implement` and commit on the child branch, then `integrate-child` into the parent.
3. `state-mark --status integrated` (already part of `integrate-child` when that path is used).

Done when the child's work is committed on the parent, the working tree is clean of that child's leftover edits, and the child is marked integrated. Then the next child.

## Final

Done when (1) integration/e2e commands against the full parent-vs-base diff have evidence of pass, or a documented deferral to human QA for a manual-only check, and (2) a fresh review of the original parent spec finds no blocking gaps.

On integration failure: one repair/commit on the parent, then reverify. On blocking spec gaps: one repair/commit, reverify, fresh review. Stop if blockers remain.

Return `READY FOR HUMAN QA`. The human runs the product and opens the PR.

## Resume

Re-invoke on the same parent. Discover again, skip integrated children, continue from the existing parent tip. Same-session pauses resume at the failed gate.
