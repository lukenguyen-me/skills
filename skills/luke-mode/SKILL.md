---
name: luke-mode
description: Coordinate engineering work, bootstrap dependencies with setup-luke-mode, and sync Matt's toolkit. Use when the user explicitly invokes Luke Mode or requests its bundled setup-luke-mode or sync-matt-pocock-skills workflow.
disable-model-invocation: true
---

# Luke Mode

Coordinate the explicitly requested task and its follow-ups. Finish or hand back
that task before treating an unrelated request as a new Luke Mode invocation.
Resolve the links below from this skill's installation directory; keep the
working directory in the user's project.
Use the harness's native skill command: `$luke-mode` in Codex or `/luke-mode` in
Cursor Cloud and Claude Code. Read [harness selection](references/harnesses.md) before resolving
skills, configuring models, or delegating work.

## Start and route

Luke Mode bundles setup and sync under `skills/`. Matt's toolkit and PStack's
verification-authoring skills are external dependencies installed by setup.
Route requested setup, toolkit sync, and explicitly named verification-authoring
workflows before selecting an
engineering playbook:

| Requested stage | Companion skill |
| --- | --- |
| `setup`, `setup-luke-mode`, configure Luke's models, or check Luke's Matt toolkit setup | [setup-luke-mode](skills/setup-luke-mode/SKILL.md) |
| `sync-matt-pocock-skills`, sync or update Matt Pocock's skill set, including newly added skills | [sync-matt-pocock-skills](skills/sync-matt-pocock-skills/SKILL.md) |
| `create-verification-skill`: generate and prove a project-local app verification skill | `create-verification-skill` from the installed PStack source |
| `maintain-verification-skill`: audit and repair an existing verification skill and feature map | `maintain-verification-skill` from the installed PStack source |

The verification companions retain PStack's explicit-only invocation policy.
Dispatch them when the user names the skill explicitly, either as its native
command or an argument to Luke, such as `$luke-mode create-verification-skill`.
Otherwise offer the native command as the next action. A missing verification
recipe during engineering work uses the composition fallback; it does not
authorize authoring or maintenance.

Read the bundled file for setup or sync. Resolve explicitly named verification
workflows from the active harness catalog and skill roots, checking their
PStack provenance, supporting resources, and invocation policy. If missing,
report the dependency and route an authorized setup request to install it.
Read and follow the installed upstream workflow; keep one procedure owner.
The bundled setup and sync files are available before the harness indexes
their separate commands. A plain request to run `setup-luke-mode` explicitly selects this bundle's setup workflow;
`$luke-mode setup-luke-mode` (Cursor and Claude Code: `/luke-mode setup-luke-mode`) is the native
bootstrap route when the separate command is not listed. Setup registers the
bundled commands, installs missing Matt and PStack dependencies, configures
model roles, and sets up the current repository. A requested refresh runs sync before setup;
otherwise setup reuses a complete installation. `Setup OAuth for this app`
and `implement offline sync` remain engineering requests.

Route an explicitly named `implement-spec <spec-ref>` execution request to the
[whole-spec contract](references/implement-spec.md) and installed Matt workflow.
Naming it as Luke's argument or selecting its native skill alongside Luke
explicitly invokes that user-only workflow. Matt remains an upstream dependency
for this owner choice; missing requirements leave it pending. Ordinary
implementation routes through Implement, which resolves the target and
automatically selects Luke-owned whole-spec execution for a parent spec with
implementation children. Read-only and plan-only scope still takes precedence.

1. Read applicable project instructions and inspect only the state needed for
   the request. Preserve existing changes. Identify the requested outcome,
   acceptance evidence, and any unsettled product or architecture decisions.
2. Before edits, assess blast radius: affected modules, callers, interfaces,
   shared state, and regression risks. Use this to bound the change and choose
   evidence. Match depth to complexity, uncertainty, impact, and project
   requirements: an obvious isolated edit needs only a brief check; a change
   across modules needs dependency tracing. Revisit the assessment if scope grows.
   Work in small verified steps. Use additional expertise or independent review
   when it improves confidence in the outcome.
3. Select one primary playbook by the requested deliverable. Read
   its file before doing the work. Announce the route in one sentence, with
   any material fallback or planned delegation. Gather facts yourself; ask only
   for decisions or information the environment cannot establish.

| Requested deliverable | Playbook |
| --- | --- |
| An explanation or diagnosis, without an application change | [Explore](playbooks/explore.md) |
| Requirements, a plan, or architecture choices | [Design](playbooks/design.md) |
| Defined new or changed behavior | [Implement](playbooks/implement.md) |
| Correction of a defect or measured regression | [Fix](playbooks/fix.md) |
| Structural change with preserved behavior | [Refactor](playbooks/refactor.md) |
| Findings about specified code or changes | [Review](playbooks/review.md) |

Read-only and plan-only requests constrain the route. `Review this bug fix`
means Review; `explain why this fails` means Explore. A behavior change is
Implement or Fix, even if called a refactor. If that intent is genuinely
ambiguous, clarify before editing. Performance diagnosis belongs to Explore;
correcting a measured regression belongs to Fix. A bounded prototype can serve
Design when the user authorizes a runnable experiment.

For compound work, follow dependency order and re-route at a real phase boundary.
Proceed with implementation only within the user's authorization and settled
decisions. Design alone ends with a design, not code.

## Compose and delegate

Read [composition](references/composition.md) before edits, using another skill,
or choosing a fallback; it owns verification selection and skill compatibility.
Matt Pocock's installed skills remain the source of their engineering practices.
The playbooks borrow workflow sequencing from his user-invoked skills; they
compose permitted primitives without invoking a user-only workflow on the user's
behalf.

| Portable role | Responsibility and selection target |
| --- | --- |
| Reasoning | Architecture, complex debugging, design trade-offs; strongest available model |
| Coding | Feature implementation and refactoring; balanced coding model |
| Worker | Tests, mechanical edits, simple investigations; fast, lower-cost model |
| Reviewer | Independent code review and verification; capable review model |

A role does not require a new agent. Do bounded work directly when delegation
adds more coordination than useful isolation or speed. Before delegation, or
when the user requires a particular role/model, read [models](references/models.md)
and the selected harness adapter.

Delegate only a bounded task whose benefit you can name. Keep code modifications
and test runs sequential, with one owner of mutable project state at a time.
The [whole-spec mode](references/implement-spec.md#scoped-concurrency) selected
by Implement, or by an explicit Matt workflow request,
permits concurrency across isolated worktrees and resources, with one writer
per worktree and one integration writer. Its preflight must establish isolation
and native capacity before that exception applies.
Complete changes and checks before reviewers read a stable snapshot. Pass scope,
context pointers, permitted writes, verification, and a compact result contract.
Give delegates no authority to expand scope or start more agents. Coordinate a
composed skill's required reviewers within the harness's actual capabilities;
avoid duplicate investigations or review panels.

## Decisions and delivery

The human settles unresolved product requirements and consequential architecture
choices. Present the smallest useful decision with a recommendation; continue
independent fact gathering while waiting. Respect decisions already made.

Default delivery is workspace changes and verification. Commits, PRs, tracker
updates, and other external actions follow the user's request or existing
authorization; invoking Luke does not grant blanket permission for them.
Authorized whole-spec execution includes the local Git history needed for its
integration branch; external delivery still follows established authorization.

End with the outcome, what was verified and how, what was not verified, and
remaining risks or decisions. Name material fallbacks. Distinguish direct review
from independent review and model diversity. Failed, missing, or inconclusive
checks remain gaps; a delegate's success report is not proof. Never claim
completion beyond the observed evidence.
