# Local verify

Check a cloud PR on the user's own machine, for what a cloud session cannot
run: the local build, app flows on real devices and simulators, and the
captures the PR names as `Not captured`. A pass hands the PR to human review;
a fail sends it back to the fixer, or, with `--fix`, is fixed on this machine.
Local verify never merges.

`$luke-mode local-verify [#N] [--fix]` (`/luke-mode local-verify` in Cursor
Cloud and Claude Code) selects this route. With `#N`, it checks that PR only.
With no argument, it works through every open PR labeled `needs-local-verify`,
oldest first, one at a time. With `--fix`, a failed check is corrected here,
as in [Fix locally](#fix-locally); without it, the run changes no code and
pushes nothing. Invoking it is the request for its PR comments, label changes,
and marking PRs ready; `--fix` adds the commits and pushes to the PR's branch.

## Project facts

The playbook names no project. Read these from the project instructions
(`AGENTS.md`, `CLAUDE.md`) and the docs they reference, such as `docs/agents/`:

- **Labels**: the triage-label mapping names `ready-for-cloud`, `in-progress`,
  `needs-local-verify`, and `verify-failed`. A missing mapping leaves the queue
  pending; point to `$luke-mode setup`. `--fix` claims the PR with
  `in-progress`; a mapping without it leaves the claim to the comment, as a gap.
- **Local-check paths**: the changed paths that need a local check, such as an
  app directory. A project that names none has no PR for this route.
- **Local build**: the build or test command the cloud cannot run.
- **Verification skill**: the project's app verification skill and its feature
  map. Resolve it through [composition](../references/composition.md); without
  one, use the project's documented checks under its fallback rules.

## Check one PR

1. Record the PR's head commit, its changed files, and its body. Check out the
   head in a temporary worktree, so the user's checkout stays as it is:
   `git fetch origin pull/<N>/head` then `git worktree add --detach <tmp> FETCH_HEAD`.
   With `--fix`, check out the PR's head branch instead, so a fix pushes to
   the PR: `git fetch origin <head-branch>` then
   `git worktree add --track -b <head-branch> <tmp> origin/<head-branch>`
   (`git worktree add <tmp> <head-branch>` when the branch already exists
   locally). A head branch in a fork cannot be pushed from here; check that PR
   as if `--fix` were absent and say so.
2. Plan the checks. At minimum:
   - the local build;
   - each verification-skill flow the change affects, on each local surface
     the change touches (phone, tablet, desktop), on a
     [shared device](../references/evidence.md#shared-devices), in the pool's
     order;
   - every `Not captured` line in the PR body. A line for a surface that
     exists on the base is a pair: capture its before state from the PR's
     merge base, in a second temporary worktree, on the same device.
3. Verifier runs the checks and captures evidence as in
   [PR evidence](../references/evidence.md): inspect and shrink each capture.
   Record each device's name and OS version.
4. A step that needs real hardware handling, such as stylus ink or a camera
   pointed at an object, goes to the human. Name the device, the exact steps,
   and what to look for, then record their answer as that step's result.
5. Publish the captures with
   `python3 <luke-mode>/scripts/publish_evidence.py <files> --ref <head-branch>`
   (`<luke-mode>` is this skill's directory).
6. Before any label write, check that the PR head is still the recorded commit.
   When it moved, report the result for the checked commit and check the new
   head instead.
7. Write the result to the PR, as below. Then remove the worktree, release
   every claimed device, and restore the settings the run changed.

A check that cannot run, such as a missing toolchain, no device for a surface,
or a hardware step the human skips, is a gap, not a pass. Leave the PR's labels
and draft state unchanged, report the gap, and move to the next PR.

## Result

**Pass.** Post one PR comment that names the checked commit, each device or
simulator with its OS version, what was checked on it, and the published
evidence. Then remove `needs-local-verify` and mark the PR ready for review.

**Fail.** With `--fix`, go to [Fix locally](#fix-locally). Otherwise post one
PR comment with the checked commit, the device and OS version, the steps, what
failed, and screenshots. Swap `needs-local-verify` for `verify-failed` and keep
the draft. End the comment with the hand-back: the fixer adds
`needs-local-verify` again after pushing the fix. When the failure fits the
[fix bound](#fix-locally), offer `$luke-mode local-verify #N --fix` as the next
action in the handoff; the user decides, so the queue keeps moving.

```markdown
## Local verification: failed at 3f2a91c

iPhone 15 (iOS 18.2), physical:

1. Open a note and draw with the pen tool.
2. Undo the last stroke.

Expected: the stroke disappears. Actual: the whole page clears.

![Page after undo](<url>)

After pushing a fix, add `needs-local-verify` again.
```

## Fix locally

With `--fix`, a failed check is this run's defect to correct on the PR's
branch, when it fits the bound:

- it corrects this PR's change against this PR's acceptance criteria, in the
  files the PR touches or their direct callers;
- it adds no behavior the PR did not set out to add, and settles no product or
  architecture question;
- none of autopilot's [hard stops](autopilot.md#hard-stops) applies.

A failure outside the bound takes the Fail result above, with the diagnosis so
far in the comment: the cloud fixer starts from it.

1. Claim the PR before the first edit: swap `needs-local-verify` (or
   `verify-failed`) for `in-progress` on the PR, and post one comment naming
   the checked commit and the failure. The label tells a dispatcher and any
   cloud session watching the PR that an agent owns it again; a PR that
   already carries it belongs to another session, so stop and report. The
   ticket keeps `in-review`: a PR for it is still open.
2. Run [Fix](fix.md) in the worktree. The failed step is the repro; Coding
   edits, Verifier reruns the project's required checks. Commit on the PR's
   branch in the project's commit style; the branch keeps its name.
3. Replay the whole plan from Check one PR, not only the failed step, on the
   devices the first pass used. A step that fails again goes back to step 2.
   A fix that outgrows the bound stops here: reset the worktree to the PR
   head, swap `in-progress` for `verify-failed`, and post the Fail result
   with the diagnosis.
4. Push the branch. Publish the new captures with `publish_evidence.py --ref
   <head-branch>` and edit the PR body: replace each `Not captured` line the
   run captured with its before and after pair (the after image alone for a
   surface the PR introduces), and add a `## Local fixes` section, after
   `## Decisions taken` when present, with one line per fix: what failed, on
   which device, and the fix commit.
5. Check that the head is still the pushed commit, then post the comment
   below, remove `in-progress`, and mark the PR ready for review. The
   local run already ran the local build, the required checks, and the flows,
   so ready does not wait for CI on the new head; name CI's state at the time
   in the comment.

```markdown
## Local verification: fixed at 8d41c2e

Failed at 3f2a91c: undo cleared the whole page (iPhone 15, iOS 18.2).
Fix: 8d41c2e scopes the undo stack to the current stroke.

iPhone 15 (iOS 18.2), physical: pen tool, undo, redo. The other strokes stay.

![Page after undo](<url>)

CI on 8d41c2e: running when this was posted.
```

Without `--fix`, local verify never edits code or pushes commits. On any run,
it never merges or enables auto-merge.

Done when each PR in scope has a pass, fixed, or fail comment and its labels
match, or a reported gap with its labels unchanged. Report, per PR, the result,
the devices used, the fix commits, and any gap.
