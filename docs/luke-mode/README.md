# Luke Mode

Luke Mode is an explicitly invoked engineering skill for Codex and Cursor Cloud.
Describe an outcome, and it selects a playbook, composes compatible installed
skills, and works toward evidence you can inspect.

Matt Pocock's skills remain the engineering toolkit. Luke adds routing, sequencing,
and optional model-aware delegation. It contains none of Matt's skill files and
requires no custom MCP server or orchestration service.

## Install globally in Codex

Choose one of the following methods to make Luke Mode available in every project.

### Skills CLI

With Node.js, npm, and Git installed, run from any directory:

```sh
npx skills add lukenguyen-me/skills --skill luke-mode --agent codex --global
```

The [Skills CLI](https://github.com/vercel-labs/skills#install-a-skill) downloads
the skill and installs it for Codex. `--global` makes it available across projects.

### Git clone

With Git installed, run these commands in a macOS or Linux terminal. Clone into
a directory where you keep personal tools:

```sh
git clone https://github.com/lukenguyen-me/skills.git
cd skills
luke_mode_repo="$(pwd -P)"
mkdir -p "$HOME/.agents/skills"
if [ -e "$HOME/.agents/skills/luke-mode" ] || [ -L "$HOME/.agents/skills/luke-mode" ]; then
  printf '%s\n' 'Inspect the existing Luke Mode installation before updating it.'
else
  ln -s "$luke_mode_repo/skills/luke-mode" "$HOME/.agents/skills/luke-mode"
fi
```

Keep the checkout at the symlink's target; edits there update the installed
skill. To remove this manual installation, use
`unlink "$HOME/.agents/skills/luke-mode"`; the checkout remains.

### Activate

Open Codex in any existing project and select `$luke-mode` or find it in `/skills`.
If discovery has not refreshed, restart Codex.

Codex supports global `.agents/skills` discovery and symlinked skill folders.
Luke's `agents/openai.yaml` sets `allow_implicit_invocation: false`, so ordinary
engineering prompts do not activate it. [Codex skill documentation](https://developers.openai.com/codex/skills)

## Install for Cursor Cloud

From the root of the skills checkout, use Python 3.9 or later to prepare a complete Cursor
skill in the project you will give to the Cloud Agent:

```sh
python3 scripts/package-luke-mode-cursor.py "/absolute/path/to/your-project/.cursor/skills/luke-mode"
```

Replace the project path with your checkout. Include the generated directory in
the repository version supplied to Cursor Cloud. The helper copies all playbooks,
references, and adapters, and adds Cursor's `disable-model-invocation: true`
frontmatter. It leaves the source skill unchanged and refuses an existing
destination. Inspect any previous Luke installation before updating; use one
Luke copy in the Cloud run's discovery locations.

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
`/luke-mode setup` for full setup or `/luke-mode configure models` for just the
roles. Confirm native discovery in a Cloud run; package checks do not exercise
Cursor's live skill loader.

## Use

```text
$luke-mode Explain how refresh tokens rotate. Leave the code unchanged.
$luke-mode Design an offline sync strategy. Discuss the trade-offs before implementation.
$luke-mode Add cursor pagination to GET /orders using the attached contract.
$luke-mode Fix duplicate orders after a checkout retry. Reproduce it first.
$luke-mode Simplify the payment adapter while preserving its behavior.
$luke-mode Review my uncommitted changes against the requirements in docs/orders.md.
```

In Cursor Cloud, use `/luke-mode` for the same requests.

Luke works in small verified steps and adapts investigation and verification to
the task's complexity, uncertainty, and impact. Before edits, it assesses affected
modules, callers, interfaces, shared state, and regression risks; trivial changes
need only a brief check. Delegate when a separate context, expertise,
or independent review improves the work; keep routine steps with their owner.
Most small tasks need no agents. Code changes and test runs are sequential.

Unresolved product requirements and consequential architecture choices belong
to the human. Routine implementation choices proceed within the agreed scope.
Workspace changes and verification are the default deliverable. Commits, PRs,
and tracker updates follow the user's request or existing authorization,
including the delivery settings of an authorized Cloud run.

## Set up Luke Mode

```text
$luke-mode setup
```

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
Luke can work directly in the current session. Four roles do not require four
agents, and a saved mapping does not imply its model ran during direct execution.

For settings that travel with the repository, explicitly choose this optional
save location in the Cloud chat:

```text
/luke-mode configure models. Save the profile to .luke-mode/models.md.
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
It recommends **user-only workflows** such as `implement`, `grill-with-docs`,
`to-spec`, and `to-tickets` for explicit invocation. It does not circumvent their
policy by reading their files as executable instructions.

Luke's own Implement playbook therefore works from a natural-language request
without automatically invoking Matt's separate `$implement` workflow. The
installed primitives supply their detailed methods. [Matt's invocation rules](https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/productivity/writing-for-agents/SKILL-MECHANICS.md)

Useful optional additions are `grilling`, `codebase-design`, `domain-modeling`,
`diagnosing-bugs`, and `code-review`, alongside `tdd`. Include
`setup-matt-pocock-skills` when installing Matt's toolkit, separately from Luke.
Choose one installation method to avoid duplicates. Some Matt workflows require
per-project setup, a tracker, confirmed test seams, or a committed review
baseline; Luke checks the installed version's requirements before invoking it.
[Matt's installation guide](https://github.com/mattpocock/skills#installation-30-second-setup)

Missing or incompatible optional skills produce a disclosed direct fallback.
Luke neither installs nor edits them automatically. Explicitly required skills
and independent-review requirements cannot be satisfied by pretending a fallback
ran the same process.

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
