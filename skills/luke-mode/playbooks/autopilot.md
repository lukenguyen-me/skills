# Autopilot

Carry a change from request to draft PR while the user is away. The PR is the
user's only view of the run: the diff, the evidence, and the decisions Luke
made on their behalf.

`$luke-mode autopilot <request>` (`/luke-mode autopilot` in Cursor Cloud and
Claude Code) selects this mode. Autopilot wraps the playbook the request routes
to; it does not replace it. A request that routes to Implement, Fix, or Refactor,
including whole-spec execution, runs on autopilot. A request for Explore,
Design, or Review runs its ordinary route; say that autopilot did not apply.

`$luke-mode autopilot issue #N` is a complete request: the ticket is the
input. Route by the ticket: `bug` to Fix, `enhancement` to Implement, and a
parent spec with implementation children to Implement's
[whole-spec mode](../references/implement-spec.md). A ticket without a category
routes by its brief, as any request does.

## Run

1. Route the request through Luke's ordinary steps and read the selected
   playbook. Plan the evidence with [PR evidence](../references/evidence.md),
   including the [shared device](../references/evidence.md#shared-devices)
   each mobile capture uses, and capture the before state before the first edit.
2. Do the playbook's work. Where the playbook would ask the user, decide and
   continue (see Decisions). Stop only at a hard stop.
3. Finish the playbook: checks, review, and its done criteria. Capture, inspect,
   and publish the after state through PR evidence.
4. Deliver:
   - On the default branch, create a branch named as in
     [branch names](../references/branch-names.md). On a branch the harness generated for the
     session that has no pushes yet, rename it the same way before the first
     push. Otherwise continue the current branch.
   - Commit only this task's changes, in the project's commit style. Changes
     that predate the run stay uncommitted; a file that holds both is a hard stop.
   - Push the branch. Write the body with the installed `pr` skill, filling its
     Evidence section from the published captures and adding a
     `## Decisions taken` section after it. Without `pr`, use its sections
     directly: Summary, Evidence, Decisions taken, Merge Danger. For a ticket,
     the body links it with the tracker's closing keyword, such as `Closes #N`.
   - Open the PR as a draft, or update the draft already open for this branch.
5. Hand off the PR and release the ticket, as below.

Done when the draft PR is open with every planned capture shown or named as a
gap, every decision listed, and every failed or unrun check stated, and the PR
and ticket carry the hand-off labels. Required checks that still fail after
in-scope attempts go at the top of the body; the draft still opens, because the
PR is where the user reviews the run. Give the PR link in the handoff.

## Hand off

Draft means the agents are not done. Ready for review means it is the human's
turn to review; it does not mean approved. Label names come from the project's
triage-label mapping, and the local-check paths from the
[project facts](local-verify.md#project-facts).

| State after the run | PR |
| --- | --- |
| Required checks pass; the diff touches a local-check path | Add `needs-local-verify`; keep the draft |
| Required checks pass; no local-check path changed | Mark ready for review |
| A required check still fails, or a hard stop blocked a step | Keep the draft; add no label |

A project with no local-check paths has none to touch. A label the tracker
lacks is a gap in the handoff; Luke does not create labels.

For a ticket, once the draft PR is open, remove `in-progress` from it. When the
run ends without a PR (a hard stop with nothing to push, or a failed push or PR
creation), keep `in-progress` and comment on the ticket with the reason and the
local branch, when the tracker is reachable. The human clears the label to
allow a retry.

Autopilot never merges a PR and never enables auto-merge. Its tracker writes
are the ones above; other tracker updates stay with the user.

## Decisions

Take the option Luke would recommend: the one most consistent with the request,
the project's existing patterns, and the easiest to reverse. Record each in the
PR body as one line: the question, the choice, and the main alternative.

```markdown
## Decisions taken

- Empty cart state: reused the existing `EmptyState` component over a new illustration.
- Price rounding: rounded per line item, matching invoices, not per order.
```

## Hard stops

Stop and ask before an action that cannot be undone by reverting the PR:

- destroying or migrating persisted data, including schema changes that drop
  or rewrite columns;
- deleting or rewriting files, branches, or history outside this task;
- touching production, secrets, billing, or shared infrastructure;
- committing a file that also holds changes made before the run.

At a hard stop, finish the independent work, push the branch, open the draft PR
with the blocked step named at the top, and ask the user there and in the
handoff. When push or PR creation fails, keep the local branch and report the
failing command and its error.
