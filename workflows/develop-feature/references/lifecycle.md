# develop-feature lifecycle

This is the shared lifecycle. Grok executes `develop-feature.rhai`; Codex follows `SKILL.md` with native subagents.

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

`*` happens only on failure. Child N+1 does not start until child N is integrated.

## Ticket shapes (Matt Pocock)

Parent spec (`to-spec`): Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope.

Child ticket (`to-tickets`): Parent, What to build, Acceptance criteria, Blocked by.

Local files: `.scratch/<feature>/spec.md` and `.scratch/<feature>/issues/<NN>-<slug>.md`.

GitHub: `gh issue view`; children via `## Parent #N`, sub-issues, or the parent task list; blockers via `## Blocked by` or native dependencies.

## Git

Parent branch is the integration branch. Each child starts from the current parent tip, not from the original base.

Default names: `feat/{id}`. Children commit on the parent branch (`child_branches = false`). Override in `.grok/develop-feature.toml`, or `.codex/develop-feature.toml` for Codex (which takes precedence over the Grok file).

Worktrees are not used. Sequential children share the workspace so tests, servers, databases, and simulators do not collide. Grok’s `isolation_worktree` also does not merge edits back.

## Ongoing spec / continue

Re-run `/develop-feature` (Grok) or `$develop-feature` (Codex) on the same parent. Both share `.grok/develop-feature-state/`. Discovery keeps the full child list and marks finished children `integrated` (state file, closed/resolved ticket, or work already on the parent branch). The loop skips those and starts at the first unfinished child, on the existing parent branch.

If a child looks only partly done, discovery stops instead of guessing.

## Stop vs next child

Stop and keep state when implementation would guess, verification will not pass, merge is unsafe, or a human is required. Never continue on a broken parent.
