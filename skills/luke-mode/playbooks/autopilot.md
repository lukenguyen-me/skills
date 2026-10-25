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

1. For a ticket, claim it as in Claim before anything else. A stop there ends
   the run.
2. Route the request through Luke's ordinary steps and read the selected
   playbook. Plan the evidence with [PR evidence](../references/evidence.md),
   including the [shared device](../references/evidence.md#shared-devices)
   each mobile capture uses, and capture the before state before the first edit.
3. Do the playbook's work. Where the playbook would ask the user, decide and
   continue (see Decisions). Stop only at a hard stop.
4. Finish the playbook: checks, review, and its done criteria. Capture and
   inspect the after state, then publish it with its before state through PR
   evidence, so each changed screen shows as a before and after pair.
5. Deliver:
   - On the default branch, create a branch named as in
     [branch names](../references/branch-names.md). On a branch the harness generated for the
     session that has no pushes yet, rename it the same way before the first
     push. Otherwise continue the current branch.
   - Commit only this task's changes, in the project's commit style. Changes
     that predate the run stay uncommitted; a file that holds both is a hard stop.
   - Push the branch. Write the body with the installed `pr` skill, filling its
     Evidence section from the published captures and adding a
     `## Decisions taken` section after it. Without `pr`, use its sections
     directly: Summary, Evidence, Decisions taken, Merge Danger. The body
     carries a closing line for every issue the PR resolves, as the PR rules
     in [Luke Mode](../SKILL.md) set out.
   - Open the PR as a draft, or update the draft already open for this branch.
6. Hand off the PR and release the ticket, as below.

Done when the draft PR is open with every planned capture shown or named as a
gap, every decision listed, and every failed or unrun check stated, and the PR
and ticket carry the hand-off labels. Required checks that still fail after
in-scope attempts go at the top of the body; the draft still opens, because the
PR is where the user reviews the run. Give the PR link in the handoff.

## Claim

A run claims its ticket before it works on it, so the tracker shows that the
ticket is taken and no second session starts on it. A dispatcher that adds
`in-progress` before it starts the session hands the claim to the run with
`--claimed`: `/luke-mode autopilot issue #N --claimed`.
Label names come from the triage-label mapping. A mapping without `in-progress`
has no claim; continue.

Read the ticket's labels and take the first row that applies:

| Ticket labels | Action |
| --- | --- |
| `in-review` | A PR for the ticket is open. On that PR's branch, continue it and update that PR. When that PR carries `in-progress`, the user's machine owns it ([fix locally](local-verify.md#fix-locally)): stop. Otherwise, or when no open PR closes the ticket, stop. |
| `in-progress`, and the request has `--claimed` | The dispatcher claimed the ticket for this run; continue. |
| `in-progress`, and the request has no `--claimed` | Another session may own the ticket; stop. |
| Neither | Add `in-progress`, then continue. |

A stop here is a hard stop before any work: edit nothing, open no PR, and write
nothing to the tracker. In the handoff, name the label that stopped the run and
the PR when there is one, and ask the user. The user clears the label, or runs
again with `--claimed` once no other session holds the ticket.

When the tracker cannot be read or the label write fails, continue without the
claim and name it as a gap in the handoff.

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

A ticket always shows its stage, so never remove `in-progress` without adding
the next label. Once the draft PR is open, swap `in-progress` for `in-review` on
the ticket in one edit, and add `in-review` to every other ticket the PR closes,
such as a parent spec's children. `in-review` says a PR for the ticket is open;
the PR's draft state and labels say whose turn it is: `needs-local-verify` as
above, `verify-failed` after a failed local check, `in-progress` on the PR
while the user's machine corrects it ([fix locally](local-verify.md#fix-locally)).
It stays until the merge
closes the ticket; when the PR is closed without merging, the human removes it.
A mapping without `in-review` leaves the project on the old hand-off: remove
`in-progress` and name the missing label as a gap in the handoff. A project may
automate this swap with a workflow that runs when a PR opens; the agent's own
edit is then redundant but harmless. The claim cannot be automated this way,
because a local run has no PR or push yet.

When a run that passed the claim ends without a PR (a hard stop with nothing to
push, or a failed push or PR creation), keep `in-progress` and comment on the
ticket with the reason and the local branch, when the tracker is reachable. The
human clears the label to allow a retry.

Autopilot never merges a PR and never enables auto-merge. Its tracker writes
are the claim and the hand-off writes above; other tracker updates stay with
the user.

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

A stop at the claim does no work and opens no PR; see Claim. At any other hard
stop, finish the independent work, push the branch, open the draft PR
with the blocked step named at the top, and ask the user there and in the
handoff. When push or PR creation fails, keep the local branch and report the
failing command and its error.
