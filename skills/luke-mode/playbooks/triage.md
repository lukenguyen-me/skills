# Triage

Move issues, and external PRs when the tracker config includes them, through
Matt's triage states. Matt's installed `triage` owns the procedure: roles,
transitions, label mapping, the disclaimer, agent briefs, and `.out-of-scope/`.
Luke adds codebase evidence, delegation, and the hand-off to delivery.

`$luke-mode triage <request>` (`/luke-mode triage` in Cursor Cloud and Claude
Code), or the native `triage` selected alongside Luke, explicitly invokes it.
A question about an issue that does not name triage routes to Explore; offer
`$luke-mode triage <ref>` as the next action.

1. Resolve the installed `triage` through [composition](../references/composition.md),
   with its resources, the tracker config, and the triage-label mapping. A
   missing skill or mapping leaves triage pending; point to `$luke-mode setup`.
   Follow its instructions for the rest of the run.
2. When gathering context, assess blast radius in the code area the item names:
   affected modules, callers, interfaces. For several items, Explorers can gather
   each item's located facts read-only; tracker reads and writes stay with
   the parent. Grilling is an interview with the maintainer, so it stays in the
   parent session.
3. Verify the claim to [Fix](fix.md)'s evidence standard: a repro that detects
   the reported symptom, or for a PR, the relevant checks run on its diff.
   Report the commands and output. A check that cannot run is a gap, and the
   claim stays unconfirmed. Triage changes no application code; a confirmed bug
   stays for Fix.
4. Invoking triage is the request for its tracker writes: labels, comments,
   closures. Make them at the installed skill's confirmation points, after the
   maintainer's direction. `.out-of-scope/`, glossary, and ADR edits are
   workspace changes and appear in the report.
5. For each item that reaches `ready-for-agent`, offer `$luke-mode fix <ref>`
   for a bug or `$luke-mode implement <ref>` for an enhancement as the next
   action. The brief is that run's input; triage ends before it starts.

Done when each triaged item carries the roles the installed skill requires and
every tracker write followed the maintainer's direction. Report, per item, the
role changes, the verification evidence or gap, and the next action. A
read-only request, such as showing what needs attention, ends with the buckets.
