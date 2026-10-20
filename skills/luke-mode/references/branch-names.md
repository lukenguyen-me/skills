# Branch names

Every branch Luke creates or renames follows this rule, on every route.

Follow the project's branch convention from its `AGENTS.md`, `CLAUDE.md`, or
contributing guide. Without one, name the branch `<type>/<issue-id>-<slug>`
when the task targets an issue, otherwise `<type>/<slug>`:

- `<type>` is the commit type of the change: `feat`, `fix`, `refactor`, `perf`,
  `test`, `docs`, or `chore`.
- `<issue-id>` is the tracker's identifier as the branch can hold it:
  `123` for GitHub issue #123, `str-45` for Linear's `STR-45`.
- `<slug>` is two to five lowercase words joined by hyphens that name the
  outcome, such as `streak-reminder`.

Examples: `feat/123-streak-reminder`, `fix/session-timer-reset`.

Keep any prefix the harness requires in front of the name; a
[Claude cloud session](../adapters/claude-code.md#cloud-sessions) pushes
`claude/feat/123-streak-reminder`.

A branch the harness generated for the session counts as unnamed until its
first push; rename it then. Once a branch is pushed or has a PR, keep its name.
