# Local verify

Check a cloud PR on the user's own machine, for what a cloud session cannot
run: the local build, app flows on real devices and simulators, and the
captures the PR names as `Not captured`. A pass hands the PR to human review;
a fail sends it back to the fixer. Local verify changes no code and never
merges.

`$luke-mode local-verify [#N]` (`/luke-mode local-verify` in Cursor Cloud and
Claude Code) selects this route. With `#N`, it checks that PR only. With no
argument, it works through every open PR labeled `needs-local-verify`, oldest
first, one at a time. Invoking it is the request for its PR comments, label
changes, and marking PRs ready.

## Project facts

The playbook names no project. Read these from the project instructions
(`AGENTS.md`, `CLAUDE.md`) and the docs they reference, such as `docs/agents/`:

- **Labels**: the triage-label mapping names `ready-for-cloud`, `in-progress`,
  `needs-local-verify`, and `verify-failed`. A missing mapping leaves the queue
  pending; point to `$luke-mode setup`.
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
2. Plan the checks. At minimum:
   - the local build;
   - each verification-skill flow the change affects, on each local surface
     the change touches (phone, tablet, desktop), on a
     [shared device](../references/evidence.md#shared-devices), physical first;
   - every `Not captured` line in the PR body.
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

**Fail.** Post one PR comment with the checked commit, the device and OS
version, the steps, what failed, and screenshots. Swap `needs-local-verify` for
`verify-failed` and keep the draft. End the comment with the hand-back: the
fixer adds `needs-local-verify` again after pushing the fix.

```markdown
## Local verification: failed at 3f2a91c

iPhone 15 (iOS 18.2), physical:

1. Open a note and draw with the pen tool.
2. Undo the last stroke.

Expected: the stroke disappears. Actual: the whole page clears.

![Page after undo](<url>)

After pushing a fix, add `needs-local-verify` again.
```

Local verify never edits code, pushes commits, merges, or enables auto-merge.

Done when each PR in scope has a pass or fail comment and its labels match, or
a reported gap with its labels unchanged. Report, per PR, the result, the
devices used, and any gap.
