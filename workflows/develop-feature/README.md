# develop-feature

A Grok Build workflow that implements an ordered list of child tickets onto one parent feature branch, **one child at a time**, and stops at human QA.

It automates: parent branch, then per child the same `/implement` flow you use by hand (tdd, tests, `/code-review`, commit), a verify pass, and merge onto the parent. It does not open a per-child PR, merge to the base branch, or deploy.

## Install

Grok discovers workflows from:

| Scope | Path | Use |
| --- | --- | --- |
| User | `~/.grok/workflows/*.rhai` | Every repository on this machine |
| Project | `<repo>/.grok/workflows/*.rhai` | This repository only |

User scope is the portable install:

```bash
cd workflows/develop-feature
./install.sh --user
```

Project scope (commit with the repo):

```bash
cd /path/to/other-repo
/path/to/skills/workflows/develop-feature/install.sh --project
```

`--copy` (default) copies files. Grok loads only regular `.rhai` files from `~/.grok/workflows/`; a symlink there does not appear in `/workflows`. Re-run `./install.sh --user` after you change the source.

The installer overwrites the workflow script and git helper. It does not overwrite `.grok/develop-feature.toml`.

After install, open `/workflows` and press `r` to reload, or start a new Grok session. The command is `/develop-feature`.

## Invoke

From a Grok Build session in the **target product repository**:

```text
/develop-feature {"ticket":"172"}
/workflow develop-feature {"ticket":"172"}
/workflow develop-feature --effort high --agent-budget 64 {"ticket":"172"}
```

`ticket` may be an issue number, URL, or file path to the parent spec.

Plan only — discover tickets and print the sequence, no git writes:

```text
/workflow develop-feature {"ticket":"172","mode":"plan"}
```

Smoke the sequential engine (no git, no product edits):

```text
/workflow develop-feature {"ticket":"SMOKE-1","mode":"smoke"}
```

In this skills repository there are no product tickets. A fixture parent spec exists at `workflows/develop-feature/examples/parent-spec.md` for plan mode.

## Lifecycle

1. **Discover.** Read the parent spec, find child tickets, linearize them by `Blocked by`, detect the base branch, branch names, and verification commands.
2. **Prepare.** Create or check out the parent feature branch from the base branch.
3. **Each child, strictly in order:**
   1. Run the repo's `/implement` skill for that child (project `.agents/skills/implement` if present: tdd, typecheck/tests, `/code-review`, commit).
   2. Commit on the parent feature branch. No per-child PR.
   3. Verify using ticket criteria, then project instructions, then repo scripts/CI.
   4. Repair on failure with the same `/implement` flow, bounded retries.
   5. Record the child as integrated on the parent. Only then start the next child.
4. **Final.** Diff against base, run integration/e2e if the project defines them, review against the original parent spec, fix blocking gaps.
5. **Stop.** `READY FOR HUMAN QA`. You run the product, then open the PR.

Children never run concurrently. Shared ports, databases, simulators, and test processes stay uncontested.

## Configuration

Optional file: `<repo>/.grok/develop-feature.toml`. See `examples/develop-feature.toml.example`.

The workflow infers what it can:

- **Tickets** from `docs/agents/issue-tracker.md` (GitHub, GitLab, or local `.scratch/`), then from the parent body’s `## Parent` / `## Blocked by` children (Matt Pocock `to-spec` / `to-tickets` shape).
- **Base branch** from `origin/HEAD`, then `main` / `master` / `develop`.
- **Branch names** from the toml templates, else `feat/{id}` and `feat/{parent-id}-{child-id}`, else repo docs (`conventional-git`, `AGENTS.md`).
- **Verify commands** from the ticket, toml, `AGENTS.md` / `CLAUDE.md`, then package scripts / Makefile / CI. It does not assume npm, pnpm, bun, or any stack.

If the existing tracker already names parent and children, you do not need extra config.

## Reasoning levels

Orchestration is the workflow engine (deterministic). It does not consume the session’s `/effort`.

Child agents inherit the **workflow launch** effort:

```text
/effort xhigh
/workflow develop-feature --effort high {"ticket":"172"}
```

That keeps the invoking session at xhigh and sets child implement/review agents to high. Grok does not currently expose a per-`agent()` effort field in authored workflows; `--effort` on the launch is the portable knob. Bundled implementer/reviewer *roles* use high, but authored workflows cannot request `fork_context` and should not depend on those roles.

Mechanical git steps still run as full agents because the workflow language cannot run shell itself.

## Failure and resume

The run **stops** (it does not start the next child) when:

- the child is too ambiguous to implement without guessing product behavior
- verification keeps failing
- merge cannot be done safely
- repository state is unexpected
- credentials or environment are missing
- a required test needs a human

Re-invoking the same parent continues an in-progress spec. Discovery lists every child, marks finished ones `integrated`, and the loop starts at the first unfinished child. A child counts as finished if:

- this workflow already recorded it in `.grok/develop-feature-state/<parent-id>.json`, or
- the tracker issue is closed / local `Status` is resolved, completed, done, or closed, or
- the parent feature branch already contains that child's work

It reuses the existing parent branch. It does not rebuild from the original base.

If it cannot tell whether a child is done, it **stops** rather than re-implementing.

Same-process pause: `/workflow resume <display-name>` continues after `await_user` gates (for example a verify failure you then fixed). A process restart is **not** resumable by Grok; re-invoke `/develop-feature` on the same parent.

Budget-limited runs need a tool resume with a higher `agent_budget`. Default 128 is enough for typical features (roughly 6–10 agents per child plus discovery, prepare, and final).

## Human boundary

The workflow must not:

- merge the parent branch into the base branch
- merge to `main` / `develop`
- deploy or release
- open the final PR (`create_final_pr` exists in the example toml and stays false)

## Helper

`scripts/git_state.py` is a small deterministic git/state tool. Agents call it; the workflow script cannot. It refuses to merge into protected base names (`main`, `master`, `develop`, …).

```bash
python3 scripts/git_state.py info
python3 scripts/git_state.py self-check
```
