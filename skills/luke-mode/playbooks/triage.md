# Triage

Move issues, and external PRs when the tracker config includes them, through
Matt's triage states. Matt's installed `triage` owns the procedure: roles,
transitions, label mapping, the disclaimer, agent briefs, and `.out-of-scope/`.
Luke adds codebase evidence, delegation, the [lane label](#lane-label), the
[stop rules](#apply-the-outcome), and the hand-off to delivery.

`$luke-mode triage <request>` (`/luke-mode triage` in Cursor Cloud and Claude
Code), or the native `triage` selected alongside Luke, explicitly invokes it.
A question about an issue that does not name triage routes to Explore; offer
`$luke-mode triage <ref>` as the next action.

1. Resolve the installed `triage` through [composition](../references/composition.md),
   with its resources, the tracker config, and the triage-label mapping. A
   missing skill or mapping leaves triage pending; point to `$luke-mode setup`.
   Follow its instructions for the rest of the run, except where this playbook
   replaces its waits for direction.
2. When gathering context, assess blast radius in the code area the item names:
   affected modules, callers, interfaces. For several items, Explorers can gather
   each item's located facts read-only; tracker reads and writes stay with
   the parent.
3. Verify the claim to [Fix](fix.md)'s evidence standard: a repro that detects
   the reported symptom, or for a PR, the relevant checks run on its diff.
   Report the commands and output. A check that cannot run is a gap, and the
   claim stays unconfirmed. Triage changes no application code; a confirmed bug
   stays for Fix.
4. Apply the outcome as below. `.out-of-scope/`, glossary, and ADR edits are
   workspace changes and appear in the report.
5. For each item that reaches `ready-for-agent`, offer `$luke-mode fix <ref>`
   for a bug or `$luke-mode implement <ref>` for an enhancement as the next
   action, or `$luke-mode autopilot issue <ref>` when it also carries the lane
   label. The brief is that run's input; triage ends before it starts.

## Apply the outcome

Invoking triage is the request for its tracker writes. Luke applies the
outcome without waiting for direction: state and category labels, the lane
label, agent briefs, and `needs-info` triage notes. It waits for the maintainer
only before a `wontfix` closure: present the recommendation and the closing
comment, then close after their direction.

An open product or architecture decision that blocks the outcome does not wait
in the session. Move the item to `needs-info` and post the installed skill's
needs-info triage notes, with the decision as the question. Address the
question to the reporter or the maintainer, whoever owns the answer. Grill only
when the request asks for it; the questions grilling would ask go into the
triage notes instead.

A maintainer's explicit direction in the request, such as `Move #42 to
ready-for-agent`, overrides the recommendation, as the installed skill's quick
override describes.

## Re-triage

A `needs-info` item goes back through triage when its newest comment came after
its last triage notes, from anyone. An item whose newest comment is a triage
comment (it starts with the triage disclaimer) is still waiting; leave it. A
scheduled or bulk run finds the items to re-triage by this signal.

## Lane label

`ready-for-cloud` is a lane label, not a state: it says a cloud agent can do
the work, and an autopilot dispatcher picks up items that carry it. Add it only
next to `ready-for-agent`, when the work needs no local hardware, account, or
manual step that a cloud session lacks; a local check after the PR is fine, as
[local-verify](local-verify.md) runs it. Remove it when the item leaves
`ready-for-agent`. Exactly one state role still holds. The project's
triage-label mapping names the label; a mapping without a lane label means the
project has no cloud lane, so skip it.

Done when each triaged item carries the roles the installed skill requires, and
every closure followed the maintainer's direction. Report, per item, the role
changes, the verification evidence or gap, and the next action. A read-only
request, such as showing what needs attention, ends with the buckets.
