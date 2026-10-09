# Whole-spec execution

This is a mode of the Implement playbook, reached after resolving the requested
ticket or spec. Read-only and plan-only scope still takes precedence.

## Select the mode and owner

Read the target through the configured tracker or supplied files. Follow its
authoritative child relationships or implementation-ticket list to establish
whether it is a parent spec with buildable children. A title containing `spec`,
an incidental link, or a prose checklist alone does not establish that graph.
An individual ticket's link to its parent does not widen the requested scope
to that parent's siblings. The user's narrower scope takes precedence over
incidental parent references. Resolve an uncertain target before implementation.

- **Parent spec with implementation children:** select whole-spec mode
  automatically. Luke owns graph execution using the procedure below and
  compatible permitted primitives from [composition](composition.md). It
  borrows Matt's sequencing without invoking his user-only `implement-spec`.
  The upstream workflow's installation is not required for this Luke-owned mode.
- **Individual ticket or settled spec without implementation children:** use
  the ordinary Implement steps. A large spec needing decomposition can receive
  a recommendation for the user-only `to-tickets` workflow; it does not gain an
  invented task graph.
- **Explicit Matt workflow:** `$luke-mode implement-spec <spec-ref>` in Codex,
  `/luke-mode implement-spec <spec-ref>` in Cursor Cloud, or Matt's native skill
  selected alongside Luke, explicitly invokes his installed workflow. Resolve
  it and its requirements through composition. Matt owns execution under these
  constraints. Missing required dependencies leave that explicit request pending
  rather than silently redirecting it to Luke-owned execution.

Use one owner of the graph and each procedure. Luke-owned execution follows this
contract; the explicit Matt path follows its installed instructions and needed
resources under the same role, isolation, evidence, and delivery constraints.
Keep Matt's files outside Luke's bundle. Do not wrap ordinary Implement or
Matt's ordinary `implement` workflow around each ticket in either whole-spec mode.

## Preflight before mutations

- Resolve applicable `tdd` and `code-review` resources and conditional
  dependencies through composition. Luke-owned execution can use disclosed
  direct testing or review when optional primitives are unavailable and the
  user's requirements permit equivalent evidence. Explicitly required skills
  remain requirements. For the explicit Matt path, also resolve the installed
  `implement-spec`, provenance, enabled state, policy, and every required
  dependency; its missing prerequisites leave that request pending. A requested
  [Matt sync](../../sync-matt-pocock-skills/SKILL.md) can install missing files.
- Read the spec, all associated tickets, their blockers, and the configured
  tracker from project guidance. Validate ticket identities and detect missing
  blockers or cycles before dispatch. Establish acceptance evidence and retain
  the starting Git SHA as the fixed review point. Missing tracker setup points
  to the installed `setup-matt-pocock-skills` for explicit invocation.
  On resume, restore the original review baseline and verify recorded ticket
  integrations against Git history and current evidence; the resumed HEAD is
  not a new whole-spec baseline. An uncertain baseline remains pending.
- Reuse confirmed public test seams from the spec, tickets, or current session.
  Resolve missing seams and material product or architecture choices before
  the affected implementers write tests; follow the installed TDD policy.
- Read [models](models.md) and the active adapter. Establish native delegated
  execution, concurrent implementer capacity, separate Git worktrees, writable
  roots, shared context pointers, and reliable per-worktree command execution.
  A shared CWD or an exposed subagent tool alone does not establish isolation.
  Reserve capacity for integration and the chosen review process. In Luke-owned
  mode, if concurrency or delegation is unavailable, execute the same graph
  sequentially in one owned integration checkout when the user's model and
  independence requirements allow it; disclose that allocation. Preserve the
  whole parent scope. Missing a safe checkout or required review capability
  leaves execution pending. The explicit Matt path requires its native worktree
  and delegation capabilities and does not silently fall back to parent execution.
  Keep both paths within the current harness rather than launching a nested CLI,
  remote run, or new orchestration service.
- Inspect existing branches, worktrees, and user changes. Create fresh owned
  worktrees from the integration branch; reuse an existing run only with
  evidence of its ownership and integrated progress. An authorized whole-spec
  build entails the local branches, commits, and merges needed for integration.
  Preserve unrelated working-tree changes and existing history; correct a wrong base by
  normal merging or a fresh owned worktree, never by resetting user work.
- Establish delivery authority from the request and accepted project/harness
  settings. Tracker closure conventions alone do not authorize external writes.
  Respect existing PR or tracker authorization without asking again. If a PR
  is authorized and required or requested, follow Matt's timing after the first
  integration. Otherwise retain local delivery and report the pending external
  handoff. Avoid premature ticket closure or a false claim of tracker resolution.

## Roles and ownership

The current parent coordinates the run and owns its progress records. Apply
Luke's model rules to delegated work; this mode does not switch the parent model.

| Work | Luke role |
| --- | --- |
| Substantial graph planning or unresolved architectural choices | Reasoning |
| Optional bounded source investigation and shared research notes | Worker |
| Ticket implementation, TDD, conflict fixes, and review corrections | Coding |
| Straightforward integration, including Matt's merger delegation when selected | Worker |
| The chosen review's required independent review axes | Reviewer |

Keep shared research notes outside disposable worktrees and available through
absolute pointers. Briefs identify the spec, ticket, agreed seams, research,
integration baseline, owning worktree and branch, permitted resources, evidence,
and completion report. Require real command outcomes, commit SHAs, and gaps.
Keep implementation delegates within their ticket and worktree; they do not
launch more implementers or per-ticket full-spec reviews. The coordinator runs
the chosen review's required Reviewer briefs without an extra panel.

## Scoped concurrency

This mode permits concurrent coding and tests only across independently owned
worktrees and isolated mutable resources. Each worktree has one writer; edits
and tests within it are sequential. Each command uses its owning worktree's
working directory and paths. Schedule within actual native concurrency limits.

Assess resource overlap before dispatch. Serialize tickets that share files,
public contracts, generated outputs, migrations, or non-isolated services,
databases, fixtures, ports, and profiles. Worktrees isolate checkout files, not
those runtime resources. Record resource waits separately from declared blocker
edges. One integration writer handles the shared branch at a time; implementation
delegates update only their own branches. Reviewers inspect a frozen snapshot.

## Frontier and verified integration

After preflight, create or resume one owned integration branch from the accepted
baseline. In Luke-owned mode, dispatch eligible tickets into owned worktrees for
parallel work, or one integration checkout for disclosed sequential execution.
Each ticket gets its scoped acceptance evidence and applicable permitted TDD
practice. Keep edits/tests sequential within its checkout and verify its actual
result before advancing the graph. Follow the installed Matt procedure when it
is the explicitly selected owner.

Maintain a per-ticket record of blockers, owner, worktree, branch, candidate SHA,
evidence, and integrated SHA. Derive the ready frontier from blockers already
integrated and verified in this run, plus explicitly evidenced prerequisites in
the starting baseline. A worker's success report, a commit on its ticket branch,
or the remote tracker's current blocked-by count does not establish integration.
Resolve external blockers against concrete integration evidence; otherwise leave
their dependents pending. Keep failed or merged-but-unverified tickets outside
the satisfied-blocker set.

For worktree execution, inspect each completion's diff and evidence before
landing it. Have the owner merge the latest integration tip into its own branch
and recheck affected behavior. Under the single integration writer, verify that
the candidate contains
the current integration tip and land by fast-forward. If the tip advanced since
the owner's check, return the candidate for refresh and re-proof; resolve
conflicts in the owned ticket worktree with Coding. Preserve the failing
evidence rather than forcing an integration or silently rewriting history.

After landing, run the affected checks on the integration tip before recording
the ticket as integrated and verified or releasing its dependents. Freeze
integration advancement on a failing check, preserve the candidate and failure,
and repair in scope or report the blocked frontier. Skipped required tests are
unverified. For checks needing gitignored fixtures or credentials, use an
authorized isolated environment or checkout actually running the integration
tip; the original checkout at another revision is not equivalent proof. Sequential
execution applies the same verified checkpoint rule before releasing dependents.

## Final proof and delivery

Once every ticket is integrated and verified, run the project's required checks
and applicable permitted project verifier on the assembled integration tip.
Match acceptance criteria to real user paths and side effects. Keep missing
credentials, skipped checks, and unavailable verifier policies explicit;
verification authoring remains separate requested work.

Run one full-spec review using the pinned starting SHA and supplied spec. Invoke
compatible permitted `code-review` and let it own its axes and rubric. In
Luke-owned mode, when that optional primitive cannot be used, review the actual
integrated diff against the complete spec and standards under composition's
model and independence rules, and disclose the fallback. The explicit Matt path
still requires its installed review procedure.
Send in-scope findings to one Coding owner, then run focused checks and affected
integration verification on the corrected tip. Reconcile consequential decisions
with the user. A second broad review requires new risk or an explicit request;
do not loop back into repeated whole-spec review after every correction.

Finish only when integration evidence and review cover the requested scope.
Follow the authorized delivery: ready an authorized PR or resolve tickets when
permitted; otherwise report the local branch and pending tracker/PR actions.
Keep implementation, verification, review, and external delivery statuses
distinct. A blocked ticket or required proof leaves the spec incomplete.

Before final or blocked handoff, wait for or stop outstanding implementation and
integration delegates so retained worktrees are stable. Stop owned processes
and remove only clean worktrees created by this run after their commits and
evidence are retained. Preserve dirty or unrelated worktrees; report any retained
recovery paths. Keep progress records and proof artifacts
outside teardown targets so a resumed run can inspect them. Report the
integration branch and SHA, ticket coverage, actual concurrency or resource
waits, check outcomes, review findings, artifact paths, and remaining handoff.
