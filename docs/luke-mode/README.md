# Luke Mode

Luke Mode is an explicitly invoked engineering skill for Codex and Cursor Cloud.
Describe an outcome, and it selects a playbook, composes compatible installed
skills, and works toward evidence you can inspect.

Matt Pocock's skills remain the engineering toolkit. Luke adds routing, sequencing,
and optional model-aware delegation. It contains none of Matt's skill files and
requires no custom MCP server or orchestration service.

Luke Mode has four companion skills:

| Sub-skill | Purpose | Codex command |
| --- | --- | --- |
| [setup-luke-mode](../../skills/setup-luke-mode/SKILL.md) | Configure Luke's model roles and check this repository's Matt toolkit setup | `$setup-luke-mode` |
| [sync-matt-pocock-skills](../../skills/sync-matt-pocock-skills/SKILL.md) | Refresh Matt's full upstream skill set, including new skills | `$sync-matt-pocock-skills` |
| [create-verification-skill](../../skills/create-verification-skill/SKILL.md) | Create and prove a project-local app verification skill and feature map | `$create-verification-skill` |
| [maintain-verification-skill](../../skills/maintain-verification-skill/SKILL.md) | Audit and repair a verification skill against source and live behavior | `$maintain-verification-skill` |

They live beside `luke-mode` so installers can discover them. Install all five
in the same skill root. Luke routes setup and sync requests to their companions.
The verification companions retain PStack's explicit-only policy: name them
directly or in a Luke request, such as `$luke-mode create-verification-skill`.
In Cursor, use `/` instead of `$`.

## Install globally in Codex

Choose one of the following methods to make Luke Mode available in every project.

### Skills CLI

With Node.js, npm, and Git installed, run from any directory:

```sh
npx skills add lukenguyen-me/skills \
  --skill luke-mode setup-luke-mode sync-matt-pocock-skills \
  create-verification-skill maintain-verification-skill --agent codex --global
```

The [Skills CLI](https://github.com/vercel-labs/skills#install-a-skill) downloads
the five skills and installs them for Codex. `--global` makes them available
across projects.

### Git clone

With Git installed, run these commands in a macOS or Linux terminal. Clone into
a directory where you keep personal tools:

```sh
git clone https://github.com/lukenguyen-me/skills.git
cd skills
luke_mode_repo="$(pwd -P)"
mkdir -p "$HOME/.agents/skills"
for luke_mode_skill in \
  luke-mode setup-luke-mode sync-matt-pocock-skills \
  create-verification-skill maintain-verification-skill; do
  if [ -e "$HOME/.agents/skills/$luke_mode_skill" ] || [ -L "$HOME/.agents/skills/$luke_mode_skill" ]; then
    printf '%s\n' "Inspect the existing $luke_mode_skill installation before updating it."
  else
    ln -s "$luke_mode_repo/skills/$luke_mode_skill" "$HOME/.agents/skills/$luke_mode_skill"
  fi
done
```

Keep the checkout at the symlink's target; edits there update the installed
skill. To remove this manual installation, use
`unlink` on each of the five installed symlinks; the checkout remains.

### Activate

Open Codex in any existing project and select `$luke-mode`, `$setup-luke-mode`,
`$sync-matt-pocock-skills`, `$create-verification-skill`, or
`$maintain-verification-skill`, or find them in `/skills`.
If discovery has not refreshed, restart Codex.

Codex supports global `.agents/skills` discovery and symlinked skill folders.
Luke's `agents/openai.yaml` sets `allow_implicit_invocation: false`, so ordinary
engineering prompts do not activate it. Setup and sync allow discovery for
requests that specifically match Luke setup or Matt toolkit sync. Both
verification companions set `allow_implicit_invocation: false`; explicit
invocation selects their authoring or maintenance stage.
[Codex skill documentation](https://developers.openai.com/codex/skills)

## Install for Cursor Cloud

From the root of the skills checkout, use Python 3.9 or later to prepare a complete Cursor
bundle in the project you will give to the Cloud Agent:

```sh
python3 scripts/package-luke-mode-cursor.py "/absolute/path/to/your-project/.cursor/skills/luke-mode"
```

Replace the project path with your checkout. The helper creates `luke-mode`,
`setup-luke-mode`, `sync-matt-pocock-skills`, `create-verification-skill`, and
`maintain-verification-skill` beside one another in that skill root.
Include all five generated directories in the repository version supplied
to Cursor Cloud. It copies all resources and adds Cursor's
`disable-model-invocation: true` to the main skill and verification companions;
setup and sync retain normal discovery. It leaves the sources unchanged and refuses
to write if any of the five destinations exists. Inspect previous installations
before updating; use one copy of each skill in the Cloud discovery locations.

For a personal installation, prepare the package in Cursor's own user skill root:

```sh
python3 scripts/package-luke-mode-cursor.py "$HOME/.cursor/skills/luke-mode"
```

Then turn on **Sync Skills for Cloud Agents** in Cursor Settings → Agents →
Context and Tools. Only `~/.cursor/skills/` participates in that sync; a Codex
installation in `~/.agents/skills/` and your personal Luke models file stay local.
Project skill files are available through the cloned repository. Prepare any
required Matt skills for the same Cloud environment as well.
[Cursor skill discovery and sync](https://cursor.com/docs/skills)

In the Cloud Agent chat, select `/luke-mode` and submit your request. Use
`/setup-luke-mode` for full setup, `/setup-luke-mode configure models` for just
the roles, or `/sync-matt-pocock-skills` to refresh Matt's toolkit. Use
`/create-verification-skill` and `/maintain-verification-skill` for verification
authoring. The main skill's named companion routes work as well. Confirm native discovery in a Cloud
run; package checks do not exercise Cursor's live skill loader.

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

Setup configures model roles and checks Matt's toolkit configuration
for the current repository. The model stage discovers the active harness's
advertised models and recommends an exact model and supported effort for each
role. Confirm the four choices once. Luke normally saves model preferences at
`~/.config/luke-mode/models.md`.

Matt's `$setup-matt-pocock-skills` configures each repository's issue tracker,
domain docs, and triage labels when needed. Luke reuses complete existing setup.
When setup is missing, it checks that the installed skill is usable and provides
the next action. Matt's setup is user-only, so explicitly invoke
`$setup-matt-pocock-skills` to run it; naming both skills in the same request also
works. That skill owns the proposed repository changes and confirmation steps.
In Cursor Cloud, the Matt command is `/setup-matt-pocock-skills`. Luke reports
model configuration and repository readiness separately.
[Matt's setup skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md),
[Codex invocation policy](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/agents/openai.yaml)

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
`setup-matt-pocock-skills` when installing Matt's toolkit, separately from Luke.
Choose one installation method to avoid duplicates. Some Matt workflows require
per-project setup, a tracker, confirmed test seams, or a committed review
baseline; Luke checks the installed version's requirements before invoking it.
[Matt's installation guide](https://github.com/mattpocock/skills#installation-30-second-setup)

Missing or incompatible optional skills produce a disclosed direct fallback.
Ordinary engineering and setup routes leave installed skill files alone.
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

The PStack-derived companions are included in Luke's package, independently of
Matt's toolkit sync. Installing them makes their workflows available across
projects. Running creation writes a verification skill for the current app;
setup and ordinary engineering work leave this authoring step to an explicit
request.

```text
$create-verification-skill
$luke-mode create-verification-skill for this app
```

Either command starts creation. It discovers the app's real launch and control
paths, writes a project-local `verify-<app>` skill with a linked feature map,
and drives one mapped feature end to end. The generated skill specifies launch,
doctor, drive, evidence, and cleanup. Evidence must survive teardown. Default
output roots are `.agents/skills/` in Codex and `.cursor/skills/` in Cursor Cloud;
existing compatible project conventions take precedence. Missing runtime
prerequisites leave an explicitly reported draft. The generated verifier can
permit normal discovery even though its creation workflow is explicit-only.

```text
$maintain-verification-skill
$luke-mode maintain-verification-skill for this app
```

Either command starts maintenance. It checks every mapped feature against
source, then one coordinator drives all features and mapped entry points
sequentially. Source reading can use native Worker delegation when useful and
supported, or a disclosed direct pass. Corrections stay inside the verification
skill's directory and are re-proven live; product regressions are reported with
evidence. Outcomes are `clean`, `changed`, or `blocked`, with partial coverage
and inaccessible prerequisites disclosed. Workspace changes are the default;
commits, PRs, and recurring maintenance follow the user's requested delivery.
Target verifier invocation policies still apply.

Both companions adapt
[PStack creation](https://github.com/backnotprop/pstack/blob/3a604672c46cd8187d2b19980eae0a34f9f91138/skills/create-verification-skill/SKILL.md)
and [maintenance](https://github.com/backnotprop/pstack/blob/3a604672c46cd8187d2b19980eae0a34f9f91138/skills/maintain-verification-skill/SKILL.md),
with the upstream MIT notice included in each skill. Choose one installation
of each name if PStack's originals are also available; resolve duplicate
ownership before updating either version.

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
