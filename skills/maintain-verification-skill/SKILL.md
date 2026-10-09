---
name: maintain-verification-skill
description: Audit and repair a project's verification skill and feature map against source and live behavior.
license: MIT
---

# Maintain a verification skill

This is Luke Mode's verification maintenance companion, adapted from
[PStack](https://github.com/backnotprop/pstack/blob/3a604672c46cd8187d2b19980eae0a34f9f91138/skills/maintain-verification-skill/SKILL.md)
under the included [MIT license](LICENSE). It retains explicit-only invocation.
Use `$maintain-verification-skill` in Codex or `/maintain-verification-skill` in
Cursor Cloud. `$luke-mode maintain-verification-skill` also explicitly names
this workflow. Maintenance is a requested stage, separate from running a
project's verification skill during ordinary engineering work.

Install beside `luke-mode`. Read applicable project guidance,
[harness selection](../luke-mode/references/harnesses.md), and the matching
adapter before discovery or delegation. Resolve shared references through the
active catalog's Luke installation if sibling links are unavailable. Keep the
working directory in the user's project.

## Target, scope, and outcomes

Locate the requested project verification skill by purpose, app, and scope,
using project instructions, the catalog, and the adapter's project-root lookup.
It normally has launch/drive instructions and a `features/README.md` map.
Check its resources, invocation policy, and compatibility before execution.
An explicit maintenance request does not bypass a target's user-only policy;
obtain its explicit invocation when needed. Ask which target only when multiple
applicable skills remain ambiguous. With no suitable target, report the missing
prerequisite and point to
[create-verification-skill](../create-verification-skill/SKILL.md).
If the requested verifier exists but lacks a feature map, reconstruct it from
concrete source using [the map example](../create-verification-skill/references/feature-map-example/README.md).
Include the reconstructed features in the complete source and live pass.

Keep edits within the target skill's own directory: instructions, feature map,
and owned helpers. Preserve unrelated work and invocation policies. Changes to
product code or shared harnesses require separate scope. Separate outdated
recipes from product regressions; keep regression evidence rather than
rewriting expected behavior to bless a defect.

Report one outcome:

- **clean:** every mapped feature has source and live coverage; no correction
  is needed.
- **changed:** corrections are made and proven; every mapped feature has source
  and live coverage. Workspace changes are the default deliverable.
- **blocked:** a required feature, prerequisite, or proof could not be completed.
  Disclose any partial edits and completed coverage.

An inaccessible feature is unverified, with its attempted route and concrete
missing prerequisite. Record it explicitly; it does not satisfy live coverage
for a `clean` or `changed` outcome.

## Audit the map against source

Read the index and all sibling feature files. Reconcile missing, duplicate,
stale, or dead index links. Account for every feature file, including an
unindexed one, before claiming source coverage.

For each feature, establish its current user-facing behavior from concrete
source paths. Return a concise summary, source entry points, likely drift or
none, and a live-verification recipe. When useful and supported, delegate
read-only feature investigations concurrently within the native runtime's
capacity. Read [Luke's model rules](../luke-mode/references/models.md) before
delegating; use the Worker role for suitable bounded reading. Give each reader
only its feature and relevant source pointers; readers perform no edits, tests,
app driving, or further delegation. If delegation is unavailable, perform the
same source pass directly and disclose the limitation.

Collect a source result for every feature. Spot-check cited drift, merge
overlapping recipes into practical shared app states, and inspect recent changes
for user surfaces missing from the map. Add a missing feature only with concrete
source evidence and include it in the live pass. Preserve all relevant mapped
entry points in the coverage plan.

## Drive and retain proof

The coordinator owns all live interaction. Follow the target's launch model:
one owned server/UI instance driven sequentially, or isolated sessions for a
short-lived CLI. Reuse an existing session only when the target's ownership and
isolation rules permit it. Source agreement alone does not complete maintenance.

Exercise every mapped feature and its listed entry points. Keep three invariants
throughout the run:

- Doctor before the first drive, on each fresh session, and after a failed or
  surprising drive. If the process is healthy but UI state is unusable, reset
  to a known state or relaunch before proceeding.
- Retain evidence of actions, results, and relevant side effects at the target's
  named location. Confirm earlier proof survives each cleanup.
- Clean up scratch state and owned processes from failed iterations. For an
  allowed shared instance, remove this run's residue while preserving the
  instance. Final teardown follows the last drive, including re-proofs.

If doctor fails because its recipe drifted, correct the recipe within edit
scope, restart only what the correction invalidates, and retry once. Report a
remaining prerequisite or failure as blocked. Capture the attempted route for
inaccessible features, name the actual prerequisite, and correct an omitted
prerequisite in the map when source supports it.

## Correct and re-prove

Classify observed gaps before editing:

- **Doc drift:** the app's intended behavior changed; correct the user-facing
  map, command, selector, or prerequisite from source and observed behavior.
- **Harness gap:** the app works but the skill cannot drive it; repair owned
  helpers or instructions, document executable helper invocations, and re-drive
  the affected path live.
- **Product regression:** intended app behavior fails; report the reproducer
  and evidence. Keep application fixes outside this maintenance pass.

Re-read every changed file and re-run affected recipes before reporting a
correction as proven. Keep concise scratch notes of source coverage, live
coverage by feature and entry point, artifact paths, regressions, and remaining
gaps. Report the outcome and any changed files after final cleanup; verify
evidence remains available. If the user requested a PR, deliver at most one
with the proven corrections using existing authorization. Otherwise leave
corrections in the workspace. Scheduling and recurring runs are separate work.
