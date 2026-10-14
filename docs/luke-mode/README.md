# Luke Mode

Luke Mode is an explicitly invoked engineering skill for Codex, Cursor Cloud, and
Claude Code.
Describe an outcome, and it selects a playbook, composes compatible installed
skills, and works toward evidence you can inspect.

Matt Pocock's skills remain the engineering toolkit. Luke adds routing, sequencing,
and optional model-aware delegation. It contains none of Matt's skill files and
requires no custom MCP server or orchestration service.

Luke Mode carries these bundle routes:

| Route | Purpose | Codex command |
| --- | --- | --- |
| [Setup](../../skills/luke-mode/playbooks/setup.md) | Install dependencies, configure model roles, and set up this repository | `$luke-mode setup` |
| [Sync](../../skills/luke-mode/playbooks/sync.md) | Update Luke's dependencies to a newer upstream tag | `$luke-mode sync` |
| [Autopilot](../../skills/luke-mode/playbooks/autopilot.md) | Carry a change to a draft PR with evidence, without check-ins | `$luke-mode autopilot <request>` |
| [Triage](../../skills/luke-mode/playbooks/triage.md) | Move issues through Matt's triage states, with codebase evidence | `$luke-mode triage` |

Matt's skills and PStack's `create-verification-skill` and
`maintain-verification-skill` are external
[dependencies](../../skills/luke-mode/references/dependencies.md) installed by
setup. Luke installs and updates only the listed skills and contains none of
their upstream files. The verification workflows retain explicit-only
invocation. In Cursor and Claude Code, use `/` instead of `$`.

## Install

The [Skills CLI](https://github.com/vercel-labs/skills) installs and updates
every skill, Luke and its dependencies alike. With Node.js, npm, and Git
installed, run from the project root and name every agent you use:

```sh
npx skills add lukenguyen-me/skills --skill luke-mode --agent codex claude-code
```

The CLI keeps one copy in `.agents/skills/`, which Codex and Cursor read, and
links `.claude/skills/` to it for Claude Code. You do not need to select other
skills from this repository. Then run setup in the project:

```text
$luke-mode setup
```

Setup installs the missing dependencies at project scope, for the same agents,
then configures models and the repository. Global installations are left
alone.

Luke's `agents/openai.yaml` makes it explicit-only in Codex, and the
`disable-model-invocation` flag does the same in Cursor and Claude Code. No
always-on project rule is installed for Luke.
[Codex skill documentation](https://developers.openai.com/codex/skills)

In Claude Code, setup proposes the `Claude Code` model profile from the
[Claude Code adapter](../../skills/luke-mode/adapters/claude-code.md): Opus for
Reasoning and Reviewer, Sonnet as the main Coding worker, and Haiku only for
read-only exploration that needs little judgment. Setup also generates one agent
per role (`luke-reasoning`, `luke-coding`, `luke-worker`, `luke-reviewer`) from
the saved profile, in `~/.claude/agents/` or the repository's `.claude/agents/`,
so each role keeps its model even when the parent omits one. Once `/luke-mode`
runs, a hook declared in the skill blocks forks, other agent types, and model
overrides that leave the profile for the rest of that session; start a new
session for unrelated work that needs other agent types. Rerun setup after
editing the models file; the hook blocks role agents that disagree with it.

### Cursor Cloud

Install with `--agent cursor` among the agents, and commit `.agents/skills/` and
`skills-lock.json` so the Cloud Agent's clone carries them. Run
`/luke-mode setup` in the Cloud chat; it installs dependencies in the actual
Cloud checkout. Confirm native discovery in the actual run.
[Cursor skill discovery](https://cursor.com/docs/skills)

## Use

```text
$luke-mode Explain how refresh tokens rotate. Leave the code unchanged.
$luke-mode Design an offline sync strategy. Discuss the trade-offs before implementation.
$luke-mode Add cursor pagination to GET /orders using the attached contract.
$luke-mode Fix duplicate orders after a checkout retry. Reproduce it first.
$luke-mode Simplify the payment adapter while preserving its behavior.
$luke-mode Review my uncommitted changes against the requirements in docs/orders.md.
$luke-mode Implement ticket #123.
```

In Cursor Cloud, use `/luke-mode` for the same requests.

Luke works in small verified steps and adapts investigation and verification to
the task's complexity, uncertainty, and impact. Before edits, it assesses affected
modules, callers, interfaces, shared state, and regression risks; trivial changes
need only a brief check. With a configured model profile, the parent session
orchestrates: it plans, briefs, integrates, and reports, and every Reasoning,
Coding, Worker, and Reviewer task runs in a delegate on that role's model, even
a one-line edit. Without a profile, Luke works directly in the current session.
Code changes and test runs are sequential;
whole-spec execution has a scoped exception for isolated worktrees and runtime
resources, with one writer per worktree and one integration writer.

Unresolved product requirements and consequential architecture choices belong
to the human. Routine implementation choices proceed within the agreed scope.
Workspace changes and verification are the default deliverable. Commits, PRs,
and tracker updates follow the user's request or existing authorization,
including the delivery settings of an authorized Cloud run.

### Autopilot

```text
$luke-mode autopilot Add a dark theme toggle to the settings screen.
```

Autopilot carries an Implement, Fix, or Refactor request to a draft PR without
check-ins. Where Luke would normally ask, it takes its recommended option and
lists each choice under `## Decisions taken` in the PR. It stops only before
actions a revert cannot undo: destroying or migrating data, deleting work
outside the task, or touching production, secrets, or billing. Even then it
pushes what it has and asks in the draft PR. Marking the PR ready, merging,
and tracker updates stay with you. Explore, Design, and Review requests run
their ordinary route.

### PR evidence

Every PR Luke opens, on autopilot or on request, has a body from Matt's `pr`
skill. For a change you can see, Luke captures the before state before its
first edit and the after state once the work is verified: screenshots for
visual changes, a GIF for flows, and command output for CLI changes. It uses
`agent-browser` for web, `simctl` for the iOS Simulator, and `adb` for Android.
Luke inspects each capture, publishes it, and shows it as a Before | After
table in the PR. Captures it could not take are listed as gaps.

GitHub has no API for PR image uploads, so the bundled
[`publish_evidence.py`](../../skills/luke-mode/scripts/publish_evidence.py)
commits the files to a hidden ref, `refs/evidence/<branch>`. Clones skip hidden
refs, so evidence adds nothing to a checkout. The images are visible only to
people who can read the repository, and they are kept forever. See
[PR evidence](../../skills/luke-mode/references/evidence.md).

## Set up Luke Mode

```text
$luke-mode setup
```

Full setup runs three stages:

1. Install missing [dependencies](../../skills/luke-mode/references/dependencies.md)
   with the Skills CLI at project scope: the listed Matt skills from
   [mattpocock/skills](https://github.com/mattpocock/skills), pinned to a tag,
   and only the two verification-authoring skills from
   [backnotprop/pstack](https://github.com/backnotprop/pstack). Every agent the
   repository already uses gets them.
2. Configure or reuse accepted model roles, normally saved at
   `~/.config/luke-mode/models.md`.
3. Run Matt's repository setup when guidance is missing, covering the tracker,
   domain docs, and triage labels.

The full setup request includes dependency installation and Matt's repository
setup; no second sync or setup command is required. Matt's installed workflow
owns its project choices and reviewable drafts. Re-running Luke setup reuses
complete installations, accepted models, and repository guidance. Disabled
skills, hand installs, and local customizations remain protected.

Setup reports dependencies, models, and repository readiness separately.
Installation does not execute the verification-authoring workflows; explicitly
name one when you want to create or maintain an app verifier.

Use `$luke-mode configure models` to configure only the portable model roles.

| Role | Work | Selection target |
| --- | --- | --- |
| Reasoning | Architecture, complex debugging, design trade-offs | Strongest available |
| Coding | Feature implementation and refactoring | Balanced coding model |
| Worker | Tests, mechanical edits, simple investigations | Fast, lower-cost model |
| Reviewer | Independent code review and verification | Capable review model |

The role names are portable; their model IDs are harness-specific. Setup preserves
separate `## Codex` and `## Cursor Cloud` profiles. It selects by execution harness,
even when Cursor uses a GPT model. Codex choices never serve as a missing Cloud
profile. `inherit` is a valid deliberate choice. Without setup,
Luke works directly in the current session, and a saved mapping does not imply
its model ran during direct execution. With setup, role work goes to delegates;
a direct run needs the role's accepted `parent` fallback.

For settings that travel with the repository, explicitly choose this optional
save location in the Cloud chat:

```text
/luke-mode configure models. Save the profile to .luke-mode/models.md.
```

Model lookup uses an explicit path first, then the repository's
`.luke-mode/models.md` if present, then the personal file. Each selected file
keeps harness profiles separate; missing roles are not merged from another file.
When the selected file lacks the active harness's section but a lower-priority
file has one, Luke warns that the harness runs without a profile.
Create or commit the repository file only when that shared configuration is
desired. Personal config files are not included in Cursor skill sync.

The Reasoning mapping also serves as the suggested parent model for difficult
tasks. Change the parent through Codex's `/model` picker or `codex --model MODEL`;
setup cannot switch an already running parent. Native subagent capabilities and
model defaults depend on the current session. [Codex subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)

In Cursor Cloud, choose the parent through Cursor's run settings or model picker.
Luke uses the native subagent model controls exposed in that run. Cursor can
substitute unavailable subagent models; Luke reports a mismatch or missing
execution evidence and keeps an explicit exact-model requirement unresolved.
[Cursor subagent models](https://cursor.com/docs/subagents#model-configuration)

Luke stops affected delegation when a selected model, effort, or capability is
unavailable. It reports the mismatch and asks for a choice. It uses a fallback
only if already authorized, and names it. Catalog presence is not a guarantee of
live access.

## Compose Matt's toolkit

The playbooks take workflow sequencing from Matt's user-invoked skills. Implement
follows `implement`'s order: defined scope, TDD at agreed public interfaces,
focused checks during work, final verification scaled to risk and project
requirements, then code review and delivery.

Luke automatically composes **permitted primitives** such as `tdd`,
`diagnosing-bugs`, `codebase-design`, and `code-review` when installed and compatible.
It recommends **user-only workflows** such as `implement`, `implement-spec`, `grill-with-docs`,
`to-spec`, `to-tickets`, and `triage` for explicit invocation. It does not circumvent their
policy by reading their files as executable instructions.

Luke's own Implement playbook therefore works from a natural-language request.
It chooses single-ticket or whole-spec execution after resolving the target,
without automatically invoking Matt's separate `$implement` or `$implement-spec`
workflow. Installed primitives supply their detailed methods. [Matt's invocation rules](https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/productivity/writing-for-agents/SKILL-MECHANICS.md)

Setup installs the Matt skills the playbooks use, listed in
[dependencies](../../skills/luke-mode/references/dependencies.md), including
`setup-matt-pocock-skills`. Add any other Matt skill yourself with the Skills
CLI; setup and sync leave it alone. Some Matt workflows require per-project
setup, a tracker, confirmed test seams, or a committed review baseline; Luke
checks the installed version's requirements before invoking it.

Missing or incompatible optional skills produce a disclosed direct fallback.
Ordinary engineering leaves installed skill files alone; full setup installs
missing dependencies and a requested sync updates them.
Explicitly required skills
and independent-review requirements cannot be satisfied by pretending a fallback
ran the same process.

## Execute a whole spec

```text
$luke-mode Implement ticket #123.
$luke-mode Implement docs/specs/offline-sync.md.
```

In Cursor Cloud, use `/luke-mode` for the same requests. Whole-spec execution is
a mode inside Implement. Luke reads the target and its authoritative child
relationships or implementation-ticket list. A parent spec with implementation
children selects this mode automatically. An individual child ticket keeps its
own scope even when it links to its parent and siblings. A title containing
`spec` or an incidental checklist does not establish a child-ticket graph.
Plan-only requests still stop at the plan.

Luke owns automatic graph execution under the
[whole-spec contract](../../skills/luke-mode/references/implement-spec.md).
It borrows Matt's sequencing and composes compatible permitted primitives;
Matt's separate user-only `implement-spec` skill is not required or invoked
implicitly. A settled spec without implementation children uses ordinary
Implement. A spec needing decomposition can receive a Design step or an explicit
`to-tickets` recommendation.

Preflight resolves the configured tracker, complete ticket graph, agreed public
test seams, review baseline, applicable `tdd` and `code-review`, and model rules.
Missing optional primitives allow a disclosed direct fallback when equivalent
evidence and the user's requirements permit it. Explicitly required skills and
independent review remain requirements. This mode does not install or configure
skills automatically.

Concurrent execution requires native capacity, isolated worktrees and runtime
resources, and reliable per-worktree command controls. Without concurrency or
delegation, Luke can execute the same parent graph sequentially in an owned
integration checkout when model and review requirements allow it. It discloses
the allocation and retains the requested parent scope.

The parent coordinates the graph. Reasoning supports substantial planning;
Worker handles bounded research or straightforward merger work; Coding owns
ticket implementation and corrections; Reviewer runs the chosen review's
required axes. The existing model profile rules apply, including exact overrides
and fallbacks. The parent model does not change when this route is selected.

Independent ready tickets may run concurrently, with one writer per worktree and
one writer for the integration branch. Tickets sharing files, contracts, or
mutable runtime resources wait for one another. The coordinator releases a
dependent ticket only after its blockers are merged and verified on the
integration tip. Remote blocked-by counts or worker success reports do not
substitute for that evidence. Stale candidates refresh from the current tip and
re-prove affected behavior before fast-forward integration. Skipped tests remain
gaps. A resumed run preserves the original whole-spec review baseline.

After all tickets are verified on the integration branch, run the required
checks and applicable permitted project verifier on the assembled app. Run one
full-spec review against the pinned baseline and complete spec, using compatible
permitted `code-review` or the disclosed review fallback. One Coding owner fixes
in-scope findings, followed by focused checks and affected
integration verification. Additional broad review requires a new risk or explicit
request. Clean up owned worktrees after preserving commits and proof; keep dirty
or unrelated worktrees and report their paths.

Local branches, commits, and merges are part of authorized whole-spec execution.
PRs and tracker writes follow existing authorization. An authorized draft PR follows
Matt's timing after the first integration; without external authorization, report
the local integration branch and pending handoff. Under autopilot, the integration
branch becomes the draft PR, with before captures from the pinned starting SHA. Keep implementation, review,
verification, and external delivery statuses distinct. The run reports branch
and SHA, ticket coverage, actual concurrency, check outcomes, artifacts, and gaps.

To select Matt's original workflow as the execution owner instead, use
`$luke-mode implement-spec <spec-path-or-issue>` or the Cursor equivalent.
Selecting his native `$implement-spec` or `/implement-spec` alongside Luke is
equivalent. This explicit path requires his installed workflow, dependencies,
tracker setup, and native worktree/delegation capabilities. Missing requirements
leave that request pending rather than silently selecting Luke's own mode.
Use a requested `$luke-mode sync` for missing upstream files, or explicitly
invoke `$setup-matt-pocock-skills` for missing repository setup. Matt's workflow
remains upstream rather than becoming another bundled companion.

See [Matt's workflow](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/implement-spec/SKILL.md)
and [usage notes](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/implement-spec.md)
for the inspected upstream version. His installed version owns the explicitly
selected Matt procedure.

## Sync Luke's dependencies

```text
$luke-mode sync
```

Sync moves the listed Matt skills to the latest `mattpocock/skills` release tag,
or to a tag you name, and refreshes the two PStack skills. It re-runs the Skills
CLI's `add` with exactly those skill names and the repository's agents, so the
lock file records the new tag. Other skills, including Matt skills you added
yourself, stay at their installed version; the report names them. A dependency
renamed or removed upstream stops the Matt refresh until the dependency list is
updated.

Sync and setup are separate. Sync does not configure model roles, repository
guidance, or tracker labels, and it does not invoke Matt's user-only setup skill.
When both operations are requested, sync runs first so setup checks the refreshed
requirements. In Cursor Cloud, verify the files and discovery inside the Cloud
environment.

## Triage issues

```text
$luke-mode triage Show me anything that needs my attention.
$luke-mode triage #42
$luke-mode triage Move #42 to ready-for-agent.
```

Naming `triage` invokes Matt's installed `triage`, which owns the roles, state
transitions, label mapping, agent briefs, and `.out-of-scope/` notes. Luke adds
a blast-radius look at the code the issue names, a repro held to the Fix
playbook's evidence standard, and read-only Workers when several issues need
codebase context. Triage changes no application code. Tracker writes happen at
Matt's confirmation points, after your direction. An item that reaches
`ready-for-agent` ends with `$luke-mode fix #42` or `$luke-mode implement #42`
as the offered next step.

Setup installs `triage` with the other dependencies, so Matt's repository setup
also writes the triage-label mapping. A question about an issue that does not
name triage goes to Explore.

## Create and maintain project verification

Full Luke setup installs these two skills from
[backnotprop/pstack](https://github.com/backnotprop/pstack#install) into the
project for every agent it uses. Their upstream instructions, resources, and invocation
policies are preserved. Neither workflow is bundled in Luke.

```text
$create-verification-skill
$luke-mode create-verification-skill for this app
$maintain-verification-skill
$luke-mode maintain-verification-skill for this app
```

In Cursor use `/` instead of `$`. Name either workflow explicitly to execute it;
setup only installs the authoring tools. Creation writes a project-local
`verify-<app>` skill and feature map, then proves a mapped feature while retaining
evidence after cleanup. Maintenance checks the existing feature map against
source and live behavior. Resolve the installed skill before execution: its
required controls, source-reader agents, and delivery steps remain requirements.
Report incompatible or missing capabilities instead of claiming the upstream
workflow ran with altered semantics.

See the current upstream
[creation instructions](https://github.com/backnotprop/pstack/blob/main/skills/create-verification-skill/SKILL.md)
and [maintenance instructions](https://github.com/backnotprop/pstack/blob/main/skills/maintain-verification-skill/SKILL.md).
Reuse one installation of each skill; resolve unknown provenance or duplicates
before updating files.

## Verification and portability

Luke discovers and invokes applicable, permitted project verification skills,
then uses the project's documented commands and existing tests or control
surfaces when a skill cannot be used. Its report names what was verified, what
was not, check outcomes, material fallbacks, and remaining risks. Passing builds,
unit tests, or reviewer agreement establish only what their evidence covers;
acceptance criteria need checks that exercise the affected behavior.

The core and playbooks are Markdown. [Harness selection](../../skills/luke-mode/references/harnesses.md)
routes to [Codex](../../skills/luke-mode/adapters/codex.md) or
[Cursor Cloud](../../skills/luke-mode/adapters/cursor-cloud.md), or
[Claude Code](../../skills/luke-mode/adapters/claude-code.md). Live Cloud
discovery, delegation, and model overrides still need validation in Cursor.
Cursor's local editor/CLI adapter is not implemented. Codex metadata alone does not enforce
another harness's invocation policy.

Try the [routing and behavior scenarios](scenarios/routing.md). See
[research and design choices](research.md) for provenance and limitations,
and [V1 validation](validation.md) for observed results and remaining coverage.
