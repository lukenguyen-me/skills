# Luke Mode

Luke Mode is an explicitly invoked engineering skill for Codex, Cursor Cloud, and
Claude Code.
Describe an outcome, and it selects a playbook, composes compatible installed
skills, and works toward evidence you can inspect.

Matt Pocock's skills remain the engineering toolkit. Luke adds routing, sequencing,
and optional model-aware delegation. It contains none of Matt's skill files and
requires no custom MCP server or orchestration service.

Luke Mode bundles two sub-skills:

| Sub-skill | Purpose | Codex command |
| --- | --- | --- |
| [setup-luke-mode](../../skills/luke-mode/skills/setup-luke-mode/SKILL.md) | Install dependencies, configure model roles, and set up this repository | `$setup-luke-mode` |
| [sync-matt-pocock-skills](../../skills/luke-mode/skills/sync-matt-pocock-skills/SKILL.md) | Refresh Matt's full upstream skill set, including new skills | `$sync-matt-pocock-skills` |

Matt's toolkit and PStack's `create-verification-skill` and
`maintain-verification-skill` are external dependencies installed by setup.
Luke contains none of their upstream files. The verification workflows retain
explicit-only invocation. In Cursor, use `/` instead of `$`.

## Install globally in Codex

With Node.js, npm, and Git installed, run:

```sh
npx skills add lukenguyen-me/skills --skill luke-mode --agent codex --global
```

The [Skills CLI](https://github.com/vercel-labs/skills) installs the complete
Luke directory, including setup and sync resources. Omit `--global` for a project
installation. You do not need to select other skills from this repository.

For a manual install, clone this repository and link only `skills/luke-mode`
into your active skill root. Keep the checkout at the link's target. Inspect
existing installations before replacing them.

Open your new project in Codex and run:

```text
$luke-mode setup-luke-mode
```

If `$setup-luke-mode` already appears in the harness catalog, it runs the same
workflow. You can also ask the harness to run `setup-luke-mode` from Luke Mode.
Setup registers links for the two bundled commands when native discovery needs
them. A harness may need a restart to index those links; the parent route works
immediately. Registration reuses matching links and preserves conflicting old
standalone installations for inspection.

Luke's `agents/openai.yaml` makes the main entry point explicit-only. Setup and
sync support matching scoped requests. No always-on project rule is installed
for Luke. [Codex skill documentation](https://developers.openai.com/codex/skills)

## Install in Claude Code

```sh
npx skills add lukenguyen-me/skills --skill luke-mode --agent claude-code --global
```

Then run `/luke-mode setup-luke-mode` in your project. Setup proposes the
`Claude Code` model profile from the [Claude Code adapter](../../skills/luke-mode/adapters/claude-code.md):
Opus for Reasoning and Reviewer, Sonnet as the main Coding worker, and Haiku
only for read-only exploration that needs little judgment.

## Install for Cursor Cloud

From the skills checkout, use Python 3.9 or later:

```sh
python3 scripts/package-luke-mode-cursor.py "/absolute/path/to/your-project/.cursor/skills/luke-mode"
```

The helper creates one complete `luke-mode` folder, with setup and sync inside.
The main entry point already carries the explicit-only flag that Cursor and
Claude Code read. The helper leaves sources unchanged, and refuses an existing destination. Include that one folder in the
repository version supplied to the Cloud Agent. Setup installs external
dependencies in the actual Cloud environment.

For a personal installation, package to `~/.cursor/skills/luke-mode`, then enable
**Sync Skills for Cloud Agents** in Cursor Settings → Agents → Context and Tools.
Personal Codex installs and model preferences do not travel with Cursor skill
sync. [Cursor skill discovery and sync](https://cursor.com/docs/skills)

In the Cloud chat, run `/luke-mode setup-luke-mode`, or `/setup-luke-mode` when
indexed. Confirm native discovery in the actual run; local package checks do
not exercise Cursor's live loader.

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
need only a brief check. Delegate when a separate context, expertise,
or independent review improves the work; keep routine steps with their owner.
Most small tasks need no agents. Code changes and test runs are sequential;
whole-spec execution has a scoped exception for isolated worktrees and runtime
resources, with one writer per worktree and one integration writer.

Unresolved product requirements and consequential architecture choices belong
to the human. Routine implementation choices proceed within the agreed scope.
Workspace changes and verification are the default deliverable. Commits, PRs,
and tracker updates follow the user's request or existing authorization,
including the delivery settings of an authorized Cloud run.

## Set up Luke Mode

```text
$setup-luke-mode
```

`$luke-mode setup` routes to the same sub-skill.

Full setup runs four stages:

1. Register the bundled setup and sync commands if native discovery needs them.
2. Install missing external dependencies: Matt's complete toolkit from
   [mattpocock/skills](https://github.com/mattpocock/skills), and only the two
   verification-authoring skills from [backnotprop/pstack](https://github.com/backnotprop/pstack).
3. Configure or reuse accepted model roles, normally saved at
   `~/.config/luke-mode/models.md`.
4. Run Matt's repository setup when guidance is missing, covering the tracker,
   domain docs, and triage labels.

The full setup request includes dependency installation and Matt's repository
setup; no second sync or setup command is required. Matt's installed workflow
owns its project choices and reviewable drafts. Re-running Luke setup reuses
complete installations, accepted models, and repository guidance. A complete
dependency installation is refreshed only on a requested update. Disabled skills,
conflicting installations, and local customizations remain protected.

Setup reports registration, dependencies, models, and repository readiness
separately. Installation does not execute the verification-authoring workflows;
explicitly name one when you want to create or maintain an app verifier.

Use `$setup-luke-mode configure models` to configure only the portable model
roles. `$luke-mode configure models` remains supported.

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
Luke can work directly in the current session. Four roles do not require four
agents, and a saved mapping does not imply its model ran during direct execution.

For settings that travel with the repository, explicitly choose this optional
save location in the Cloud chat:

```text
/setup-luke-mode configure models. Save the profile to .luke-mode/models.md.
```

Model lookup uses an explicit path first, then the repository's
`.luke-mode/models.md` if present, then the personal file. Each selected file
keeps harness profiles separate; missing roles are not merged from another file.
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
`to-spec`, and `to-tickets` for explicit invocation. It does not circumvent their
policy by reading their files as executable instructions.

Luke's own Implement playbook therefore works from a natural-language request.
It chooses single-ticket or whole-spec execution after resolving the target,
without automatically invoking Matt's separate `$implement` or `$implement-spec`
workflow. Installed primitives supply their detailed methods. [Matt's invocation rules](https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/productivity/writing-for-agents/SKILL-MECHANICS.md)

Useful optional additions are `grilling`, `codebase-design`, `domain-modeling`,
`diagnosing-bugs`, and `code-review`, alongside `tdd`. Include
`setup-matt-pocock-skills` through Luke setup when installing Matt's toolkit.
Choose one installation method to avoid duplicates. Some Matt workflows require
per-project setup, a tracker, confirmed test seams, or a committed review
baseline; Luke checks the installed version's requirements before invoking it.
[Matt's installation guide](https://github.com/mattpocock/skills#installation-30-second-setup)

Missing or incompatible optional skills produce a disclosed direct fallback.
Ordinary engineering leaves installed skill files alone; full setup installs
missing dependencies and a requested sync refreshes Matt's toolkit.
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
the local integration branch and pending handoff. Keep implementation, review,
verification, and external delivery statuses distinct. The run reports branch
and SHA, ticket coverage, actual concurrency, check outcomes, artifacts, and gaps.

To select Matt's original workflow as the execution owner instead, use
`$luke-mode implement-spec <spec-path-or-issue>` or the Cursor equivalent.
Selecting his native `$implement-spec` or `/implement-spec` alongside Luke is
equivalent. This explicit path requires his installed workflow, dependencies,
tracker setup, and native worktree/delegation capabilities. Missing requirements
leave that request pending rather than silently selecting Luke's own mode.
Use a requested `$sync-matt-pocock-skills` for missing upstream files, or explicitly
invoke `$setup-matt-pocock-skills` for missing repository setup. Matt's workflow
remains upstream rather than becoming another bundled companion.

See [Matt's workflow](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/implement-spec/SKILL.md)
and [usage notes](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/implement-spec.md)
for the inspected upstream version. His installed version owns the explicitly
selected Matt procedure.

## Sync Matt's latest skill set

```text
$sync-matt-pocock-skills
```

`$luke-mode sync Matt's skills` routes to the same sub-skill. Sync discovers the
full current inventory from `mattpocock/skills`, refreshes installed files, and
includes new upstream skills. It preserves the existing installation method,
agent, scope, local customizations, and unrelated skills. Conflicts that require
a user decision remain pending.

For Skills CLI installations, the sub-skill re-runs `add` for the official source
with all skills selected and one specific agent. This also picks up new skills.
For an existing plugin, it uses the host's update controls instead of adding a
second installation. The sub-skill checks current upstream instructions when it
runs and reports revision evidence and installed versus loaded state.

Sync and setup are separate. Sync does not configure model roles, repository
guidance, or tracker labels, and it does not invoke Matt's user-only setup skill.
When both operations are requested, sync runs first so setup checks the refreshed
requirements. In Cursor Cloud, verify the files and discovery inside the Cloud
environment. [Matt's installation guide](https://github.com/mattpocock/skills#installation-30-second-setup)

## Create and maintain project verification

Full Luke setup installs these two skills from
[backnotprop/pstack](https://github.com/backnotprop/pstack#install) into the active
harness's skill root. Their upstream instructions, resources, and invocation
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
[Cursor Cloud](../../skills/luke-mode/adapters/cursor-cloud.md). Cursor packaging and
local package checks are implemented; live Cloud discovery, delegation, and
model overrides still need validation in Cursor. Claude Code and Cursor's local
editor/CLI adapters are not implemented. Codex metadata alone does not enforce
another harness's invocation policy.

Try the [routing and behavior scenarios](scenarios/routing.md). See
[research and design choices](research.md) for provenance and limitations,
and [V1 validation](validation.md) for observed results and remaining coverage.
