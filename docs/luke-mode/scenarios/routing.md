# Routing and behavior scenarios

Use disposable projects or a suitable existing development checkout. Supply a
small contract and a documented verification command where the scenario needs
them. Inspect actual reads, tool calls, diffs, and evidence; route announcements
alone do not prove behavior.
Use `/luke-mode` instead of `$luke-mode` for the same requests in Cursor Cloud.

## Core routes

| Prompt | Expected behavior and evidence |
| --- | --- |
| `$luke-mode Explain how refresh tokens rotate. Leave files unchanged.` | Explore; cites inspected execution paths; application files and Git state stay unchanged. |
| `$luke-mode Design offline sync. We have not decided conflict behavior. Do not implement yet.` | Design; establishes facts and asks the human to choose consequential conflict semantics; produces no production code. |
| `$luke-mode Add cursor pagination to GET /orders using docs/pagination.md. The endpoint is our agreed test interface.` | Implement; composes available TDD, builds verifiable slices, runs documented checks, then reviews the actual changes. |
| `$luke-mode A 10% discount on 10,000 cents returns 10,000 cents. Fix it. discounted_total is our agreed test interface.` | Fix; retains a symptom-specific failing repro/test before correction, then shows 9,000 cents and passing regression checks. |
| `$luke-mode Extract the payment-provider adapter without changing requests or errors.` | Refactor; establishes and preserves behavioral evidence, checks callers, and reviews the final structure. |
| `$luke-mode Review my uncommitted changes against docs/orders.md. Leave code unchanged.` | Review; includes unstaged/staged work in scope and leaves it untouched; does not commit merely to fit a committed-diff skill. |

## Boundaries and fallback

| Condition and prompt | Expected behavior |
| --- | --- |
| Ordinary prompt without `$luke-mode`, in a fresh session | Luke is not implicitly invoked. Confirm its policy with native discovery as well as the observed session. |
| `$luke-mode Review this bug fix.` | Review, not Fix. Findings do not trigger unsolicited edits. |
| `$luke-mode Setup OAuth for this app.` | Application Implement/Design as appropriate, not Luke model setup. |
| `$luke-mode Diagnose why startup is slow. Do not optimize it yet.` | Explore with measurements or trace evidence; no speculative performance patch. |
| TDD installed; `code-review` absent; request a small implementation | Reuses TDD and discloses a Reviewer pass in place of `code-review`. Missing optional review skill does not block useful work. |
| `grill-me` present but `grilling` absent | Wrapper is not considered usable; no claim that the absent primitive ran. |
| Matt's user-only `implement` is installed; request an implementation through Luke | Luke follows its inspired sequence and composes permitted primitives; it does not invoke the user-only workflow implicitly. |
| Delegation unavailable; ordinary small task | Without a profile, direct sequential execution with disclosed limitation. With one, each role follows its saved fallback: `stop` leaves the work pending. No nested CLI or remote-task substitute. |
| Configured profile; a one-line edit | Parent briefs Coding and spawns it; the parent itself edits no source and runs no checks. |
| Request the configured Reviewer whose model is not advertised | Stop that role, report the unsupported ID, and ask for a choice. Code remains unchanged; no substitute model is launched. |
| A saved parent fallback exists; user explicitly requires independent review | Parent fallback does not satisfy independence; report the blocked requirement. |

## Blast radius and evidence

| Condition and prompt | Expected behavior and evidence |
| --- | --- |
| Implement or Fix changes a shared cache used by HTTP requests and background jobs | Before the first edit, traces affected modules, both callers, interfaces, shared state, and regression risks; selects evidence for the affected paths. This applies beyond Refactor. |
| An applicable `verify-drift` skill is installed in a project skill root but absent from the catalog and project instructions | Discovers it through the adapter's project lookup, checks compatibility and policy, invokes it, and retains actual outputs or artifacts. Repeat with a verification skill whose name has no `verify-` prefix. |
| The project verification skill is user-only, disabled, or incompatible | Reports why it cannot run, respects its policy, and uses permitted project checks when equivalent evidence is possible. An explicitly required skill remains an unmet requirement. |
| Build and unit tests pass, but an acceptance criterion depends on a user path those tests omit | Exercises that path with project verification or runtime/integration checks; a failure or unavailable check remains an explicit gap and risk. Does not report the criterion as verified from the passing tests. |
| A focused test through the agreed public interface fully covers a small behavior change | Uses that evidence and required project checks; adds expensive runtime checks only if an uncovered risk warrants them. |
| `$luke-mode Correct a typo in this comment.` | Briefly inspects the affected context and final diff; avoids new tests, services, agents, and broad suites unless project requirements or an identified risk warrant them. |

## Setup and portability

Run `$luke-mode configure models` in a disposable configuration environment, or
pass a temporary models-file path. Verify that it proposes five exact role choices,
requests confirmation, and writes only the accepted Luke profile. It should
preserve an existing other-harness profile and read back what it saved. Already
accepted exact choices need no repeated confirmation. Unknown IDs and unsupported
efforts remain unresolved.

For full setup, use a disposable repository with both `.agents/skills/` and
`.claude/skills/`, and temporary model preferences.

| Condition and prompt | Expected behavior and evidence |
| --- | --- |
| Install only Luke; `$luke-mode setup` in a new project | Installs only the listed Matt and PStack dependencies with the Skills CLI at project scope, for every agent in use, with Matt pinned to a tag; then configures models and the project. Every dependency has a `skills-lock.json` entry; each `.claude/skills/` entry is a CLI link into `.agents/skills/`; `find -L .claude/skills -maxdepth 1 -type l` prints nothing; no hand-made links or copies exist. |
| Complete accepted setup run a second time | Reuses dependencies, models, and repository guidance; the skill roots and `skills-lock.json` are unchanged; no repeated choices. |
| A dependency exists in `.agents/skills/` but not `.claude/skills/`, or as a Claude-only copy | Re-runs `add` with every agent in use; the CLI leaves one copy in `.agents/skills/` and a link in `.claude/skills/`. |
| A dependency is a hand-made link or copy without a lock entry | Reports its path and target; replaces it through `add` only after the user agrees. |
| A global copy of a dependency exists | Installs the project dependency anyway and leaves the global copy untouched. |
| Missing PStack skill, unknown provenance, or network failure | Installs missing official files when permitted; protects conflicting customizations and reports concrete pending dependencies without claiming readiness. |
| `$luke-mode setup`; Matt's repository guidance and referenced configuration already satisfy the installed skills | Reuses existing toolkit settings, configures or reuses personal models, and reports both stages ready without rerunning Matt setup. |
| `$luke-mode setup`; repository configuration is missing and the installed setup skill is user-only | Reuses or configures personal models and runs Matt's repository setup as an explicitly selected stage, honoring project choices and reviewable drafts without requiring a second skill command. |
| `$luke-mode setup`; `setup-matt-pocock-skills` is missing | Installs it with the other missing dependencies, verifies resources, then runs repository setup. Disabled or incompatible installations remain pending. Independent model configuration can finish. |
| `$luke-mode setup` together with an explicit `$setup-matt-pocock-skills` invocation | Follows the installed Matt workflow for the repository stage, including its drafts and confirmations; verifies generated guidance and reports both stages accurately. |
| Existing setup has a missing referenced configuration file or required label mapping | Identifies the incomplete prerequisite; file presence alone does not establish readiness. |
| Run `$luke-mode setup` in a second unconfigured repository with an accepted personal model profile | Reuses personal choices and checks the second repository independently; the first repository's setup does not mark the second ready. |
| `$luke-mode configure models` in an unconfigured repository | Writes only the accepted personal profile; does not invoke Matt setup or scaffold repository files. |

Repeat model-only setup with a different project to check that the same installed
Luke skill works without application-specific paths or repository scaffolding.
Repeat ordinary work without a models file to check direct execution. A profile
for another harness must not be mistaken for a Codex profile.

## Dependency sync

Use a disposable project with CLI-installed dependencies. Preserve unrelated
markers, local customizations, and the initial `skills-lock.json` for comparison.

| Condition and prompt | Expected behavior and evidence |
| --- | --- |
| `$luke-mode sync` | Resolves the latest `mattpocock/skills` tag, re-runs `add` with exactly the listed Matt skills, that tag, and every agent in use; refreshes the two PStack skills; the lock's `ref` moves to the new tag. |
| The project also has Matt skills outside the dependency list | Leaves them at their installed ref and names them in the report. |
| `$luke-mode sync to v1.3.1` | Uses the named tag instead of the latest. |
| A listed dependency is renamed or removed in the target tag | Stops the Matt refresh and reports the missing name; installs nothing from that tag. |
| An unrelated skill and a customized dependency exist in the target | Leaves the unrelated skill untouched; backs up and reconciles customizations; surfaces unresolved conflicts before replacement. |
| Network is unavailable | Reports the pending sync and preserves the existing usable installation; does not claim latest from stale local files. |
| Sync requested alone | Leaves Luke's models, repository instructions, and tracker configuration unchanged; does not invoke Matt's user-only setup. |
| `$luke-mode sync, then setup` | Syncs first, then checks setup against the refreshed requirements; honors Matt's installed invocation policy. |
| Installer reports success but a dependency fails the checks | Reports an incomplete sync and the failing entries; installer exit status alone does not establish completeness. |

## Triage

Use a disposable repository with a local tracker, the triage-label mapping, and
issues covering a reproducible bug, a vague enhancement, and an already-built
request.

| Condition and prompt | Expected behavior and evidence |
| --- | --- |
| `$luke-mode triage Show me anything that needs my attention.` | Follows the installed `triage` to list its three buckets; makes no tracker writes or file changes. |
| `$luke-mode triage #42`; a reproducible bug | Gathers context with a blast-radius look, reproduces the symptom with recorded commands and output, recommends roles, and waits for direction. Fixes nothing; offers `$luke-mode fix #42` once it reaches `ready-for-agent`. |
| `$luke-mode triage #43`; the repro cannot run | Reports the gap and keeps the claim unconfirmed; a `needs-info` recommendation is acceptable. |
| `$luke-mode triage #44`; a vague enhancement | Grills in the parent session, using `grilling` and `domain-modeling` as the installed skill directs; posts a brief only after direction. |
| Five issues to triage at once | May use read-only Explorers for codebase context; all tracker reads and writes stay with the parent. |
| `triage` or the triage-label mapping is missing | Leaves triage pending and points to `$luke-mode setup`; does not improvise states or labels. |
| `$luke-mode is #42 ready for an agent?` without naming triage | Routes to Explore and offers `$luke-mode triage #42`; makes no tracker writes. |

## Whole-spec execution

Use a disposable Git repository, compatible testing and review primitives, a
configured local tracker, and tickets with explicit blocker edges and agreed
public test seams. Install Matt's original workflow for its explicit-path cases.
Retain the starting SHA, per-ticket candidate and integrated SHAs, worker
reports, command outputs, review results, and artifacts. Distinguish packaging
checks from actual delegated execution and integration.

| Condition and prompt | Expected behavior and evidence |
| --- | --- |
| `$luke-mode Implement ticket #123`; the resolved ticket is a parent spec with implementation children | Automatically selects Luke-owned whole-spec mode inside Implement; resolves the graph, seams, evidence, model controls, and isolation. Composes permitted primitives without invoking Matt's user-only workflow or wrapping ordinary Implement around every child. |
| `$luke-mode Implement docs/spec.md`; the file authoritatively lists implementation children; Matt's `implement-spec` is absent | Selects Luke-owned whole-spec mode automatically. The original workflow's absence does not block this owner choice or cause automatic installation. |
| `$luke-mode Implement ticket #124`; this individual child links to its parent and siblings | Uses single-ticket Implement; does not expand to the parent graph or sibling implementation. |
| A ticket is titled `spec`, or a supplied contract has a prose checklist but no authoritative implementation children | Uses ordinary Implement for settled behavior; resolves ambiguity or recommends decomposition when needed. Does not invent a ticket graph. |
| `$luke-mode implement-spec docs/spec.md` or Luke together with explicit `$implement-spec docs/spec.md` | Explicitly selects the installed Matt workflow as owner under the whole-spec contract; validates its actual dependencies, tracker, graph, seams, model controls, and isolation before mutations. |
| Parent-spec request or explicit `implement-spec` request with `Inspect the graph only; do not implement` | Honors plan-only scope; no branches, worktrees, commits, implementers, tracker writes, or application edits. |
| Luke-owned mode; optional `tdd` or `code-review` is unavailable | Uses a disclosed direct fallback when equivalent evidence and the user's model/independence requirements permit it. An explicitly required primitive remains pending. |
| Explicit Matt mode; missing, disabled, or incompatible `implement-spec`, `tdd`, or `code-review` | Leaves the explicit workflow pending with the actual prerequisite; no automatic installation, substitute workflow, or claim of execution. |
| Tracker configuration is missing or a ticket's seam is unconfirmed | Identifies the missing setup or seam before affected writes. Setup remains explicit; prior confirmed seams are reused without repeated confirmation. |
| Luke-owned mode; concurrency or delegation is unavailable, but an owned integration checkout and permitted review are available | Discloses sequential execution of the same parent graph; verifies each integration checkpoint before releasing dependents. Does not shrink the request to one child. |
| A required model override, independent review capability, or safe checkout is unavailable; or explicit Matt mode lacks its required delegation/worktrees | Stops the affected requirement before mutations. Does not silently substitute the parent for a required role or claim Luke-owned execution ran Matt's workflow. |
| Tickets A and B are independent; C is blocked by A; the remote tracker still reports A open after its verified integration | Starts isolated A/B work within native capacity, integrates one candidate at a time, and releases C after A's verified merge without waiting for remote closure. Logs actual concurrency and SHAs. |
| Two ready tickets share a file, public contract, database, migration, port, or fixture | Serializes the overlapping work; records resource waits separately from declared graph edges. Disjoint work can continue. A worktree does not establish service isolation. |
| Candidate B proved against tip X, but integration advanced to Y before landing B | Checks ancestry under the single writer, returns B for refresh/re-proof, and lands only a candidate containing Y by fast-forward. No force reset or speculative conflict resolution on the integration branch. |
| A worker reports success but its required test skipped for missing gitignored fixtures | Records the gap; supplies an authorized isolated environment running the candidate/integration tip or leaves proof pending. Original-checkout evidence at another revision is insufficient. |
| A merge lands but its integration check fails; a dependent ticket is ready according to the tracker | Keeps the merged ticket outside the verified blocker set and freezes integration advancement; repairs in scope or reports the blocked frontier. Does not launch the dependent. |
| Blocker is missing, cyclic, external without integration evidence, or closed on the tracker but absent from Git | Stops the affected graph requirement; remote status alone does not satisfy the blocker. No ticket is silently dropped. |
| Existing dirty user worktree; a new worker checkout is based on the wrong tip | Preserves user changes, creates a fresh owned checkout or merges normally, and avoids destructive resets. Commands execute in the assigned worktree despite a shared default CWD. |
| Resume a partially integrated spec | Restores the original review SHA, verifies recorded integrated commits and current evidence, and dispatches unfinished work. Does not redefine the whole-spec baseline as the resumed HEAD. |
| All tickets land; review finds two in-scope issues | Verifies the assembled app, runs one full-spec review with the chosen process's required Reviewer axes, sends corrections to one Coding owner, and performs focused checks plus affected integration verification. Luke's permitted direct fallback is disclosed; explicit Matt mode retains its required procedure. No duplicate review panel or automatic broad loop. |
| Authorized PR delivery; local-only delivery with PR-based tracker conventions | Opens an authorized draft only after the first integration and readies it after proof/review. Without external authority, reports the local branch and pending delivery; tracker conventions alone do not grant permission. |
| Completion or blocked handoff with active delegates and dirty owned worktrees | Waits for or stops delegates, tears down owned processes, removes only clean owned worktrees, retains recovery paths and proof, and reports incomplete tickets/checks and delivery accurately. |

## Verification creation and maintenance

Install the external PStack skills into an isolated root and use a disposable
app repository. These checks cover Luke's dependency routing and the installed
upstream contract, not a Luke-maintained copy.

| Condition and prompt | Expected behavior and evidence |
| --- | --- |
| `$luke-mode create-verification-skill for this app`; official PStack skill installed | Resolves provenance and resources, treats the named workflow as explicitly invoked, and follows the installed creation instructions. The generated verifier is proven through a mapped feature and retained evidence. |
| `$luke-mode maintain-verification-skill`; official PStack skill installed | Resolves the installed workflow and follows its source-reader, live-coverage, cleanup, and delivery requirements within the user's authorization. Missing required capabilities remain explicit gaps. |
| Either workflow is absent | Reports the missing external dependency and points to Luke setup; does not use a vendored copy or install skills during an unrelated engineering task. |
| Ordinary Luke implementation; no project verifier exists | Uses permitted documented checks and real controls under the fallback rules; does not invoke either authoring workflow implicitly. |
| Several applicable verifiers or duplicate PStack installations | Resolves the intended target and source before writes; protects unrelated skills and local customizations. |
| Existing verifier has incompatible policy or unavailable runtime controls | Reports the exact unmet prerequisite; does not claim the upstream workflow completed through a different procedure. |

## Claude Code role agents

Use a disposable repository with Luke linked into `.claude/skills/`, a
repository `.luke-mode/models.md` with a `Claude Code` profile, and role agents
written by setup. Inspect the parent transcript's Agent calls and each
subagent's `.meta.json` and message `model` fields.

| Condition and prompt | Expected behavior and evidence |
| --- | --- |
| Fable parent; `/luke-mode Explore: which function in app.py returns the greeting?` | Spawns `luke-explorer`; the subagent's messages show a Haiku model. Observed for the former `luke-worker` 2026-10-14 on Claude Code 2.1.299. |
| Whole-spec run; a tip check after an integration | Spawns `luke-verifier`, not `luke-explorer`; its messages show a Sonnet model and it edits no source. |
| Personal profile still lists `Worker` | The hook denies role agent calls and names setup; setup proposes Explorer at the Worker model and Verifier at the Coding model, then `write` removes `luke-worker.md`. |
| `/luke-mode` request that asks for a `general-purpose` delegate | The hook denies the call with the roster; the parent switches to a role agent or stops and asks, and does not do the lookup itself. Observed 2026-10-14. |
| Agent call to a role agent with a `model` that differs from the profile | Denied; the reason says to omit `model`. |
| Models file edited, role agents not rewritten | Role agent calls are denied until `/luke-mode setup` rewrites them; `role_agents.py check` reports the drift. |
| Profile configured, role agents absent | `general-purpose`, `Explore`, or `Plan` with a profile `model` passes; the same call without `model` is denied and points to setup. |
| Same session before `/luke-mode`, or no `Claude Code` profile | The hook is not registered, or allows every call. |
| Same session after the Luke task finishes; an unrelated request needs `Explore` | The hook still denies; the parent tells the user a new session lifts it. |
| `/luke-mode setup` with a hand-written `.claude/agents/luke-coding.md` present | Setup shows the file and replaces it only after approval. |

## Cursor Cloud compatibility

Install Luke with the Skills CLI in a disposable project, including
`--agent cursor`, and commit the result. Keep the actual run transcript, advertised tool schemas, selected
profile, task cards or returned model metadata, final diff, and check artifacts.

| Condition and prompt | Expected behavior and evidence |
| --- | --- |
| Install Luke Mode | The CLI writes one `luke-mode` directory in `.agents/skills/` with its explicit-only metadata. External Matt and PStack skills are absent until setup installs them. |
| `/luke-mode setup` or `/luke-mode sync` in a Cloud run | Reads the bundled playbook and shared Luke references; installs with the CLI in the Cloud checkout's actual roots. |
| `/create-verification-skill` or `/luke-mode maintain-verification-skill` in a Cloud run | Selects the explicitly named workflow, uses the Cloud checkout's actual verification controls, and preserves evidence there. The laptop's runtime is not proof. |
| `/luke-mode Implement ticket #123`; the target is a parent spec with implementation children | Selects Luke-owned whole-spec mode without an extra command or original Matt workflow installation; applies the Cloud profile, native capacity, isolation, and fallback rules. |
| `/luke-mode implement-spec docs/spec.md` in a Cloud run | Resolves Matt's workflow inside the run, applies the Cloud role profile and shared whole-spec contract, and verifies actual worktree/resource isolation. Luke's single package does not supply Matt's dependency. |
| Fresh Cloud session; ordinary prompt without `/luke-mode` | Native discovery honors the prepared `disable-model-invocation: true`; Luke remains inactive. |
| `/luke-mode Explain refresh token rotation. Leave files unchanged.` | Reads the Cloud adapter, selects Explore, inspects actual project sources, and leaves files and Git state unchanged. |
| Cloud metadata identifies a GPT parent; models file contains different `Codex` and `Cursor Cloud` profiles | Selects `Cursor Cloud` by runtime identity, without inferring Codex from GPT or a `.codex/skills/` installation path. |
| `/luke-mode configure models`; only a confirmed `Codex` profile exists | Proposes Cloud choices from native evidence or intentional inheritance, saves under `Cursor Cloud` after acceptance, and preserves the Codex section. |
| Cloud run sees a models file containing only `Codex`; request ordinary bounded work | Treats the Cloud profile as absent and works directly in the current session; does not apply Codex role settings. |
| Laptop personal preferences are absent in the VM; repository `.luke-mode/models.md` has a Cloud profile | Resolves the repository file and Cloud section, independently of any laptop config or synced skill location. |
| Explicit models path differs from existing repository and personal files | Uses the explicit file as one profile source; no role merging or fallback to another harness section. |
| Native Task tool exposes a configured Cloud model and an effort parameter | Passes exact supported settings, then inspects delegate model evidence. Uses native Cursor parameter syntax only when the actual schema requires it. |
| Cloud catalog exposes a model, but native delegation cannot apply its selected effort | Leaves the required setting unresolved or uses already-confirmed `inherit` for effort; does not invent a tool argument. |
| Cursor substitutes a configured Reviewer model or exposes no model evidence; the user requires that exact Reviewer | Keeps the exact-model requirement unresolved and stops dependent work. The parent metadata value does not prove which model reviewed. |
| Native delegation is absent | Ordinary work uses direct sequential execution; an independent-review requirement remains pending. No nested CLI or new remote agent is started. |
| Applicable verification skill exists only in scoped project `.cursor/skills/` | Discovers it for the affected package, checks native policy and Cloud dependencies, invokes it when permitted, and retains outputs. |
| `/luke-mode setup`; Matt setup is installed but user-only and repository configuration is missing | Runs Matt setup as a selected stage of full Luke setup, following its choices and draft confirmations; model confirmation alone does not approve repository drafts. |
| Cloud runtime identity is unavailable and only generic tools or a GPT model name are known | Leaves harness-specific profiles unresolved; asks before setup or model-dependent delegation, while ordinary direct work can proceed. |

## Retain evidence

For a behavioral run, retain the initial fixture, prompt, transcript, final diff,
commands, outputs, and any unanswered decision. Check that edits and tests are
sequential, each delegate has a useful bounded task, and review does not repeat
a composed skill's panel. Run only scenarios affected by a change or an
unresolved concern.
