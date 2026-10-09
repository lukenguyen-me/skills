# Luke Mode

Luke Mode is an explicitly invoked personal engineering skill for Codex. Describe
an outcome, and it selects a playbook, composes compatible installed skills,
and works toward evidence you can inspect.

Matt Pocock's skills remain the engineering toolkit. Luke adds routing, sequencing,
and optional model-aware delegation. It contains none of Matt's skill files and
requires no CLI, MCP server, or orchestration service.

## Install globally in Codex

Choose one of the following methods to make Luke Mode available in every project.

### Skills CLI

With Node.js, npm, and Git installed, run from any directory:

```sh
npx skills add lukenguyen-me/luke-mode --skill luke-mode --agent codex --global
```

The [Skills CLI](https://github.com/vercel-labs/skills#install-a-skill) downloads
the skill and installs it for Codex. `--global` makes it available across projects.

### Git clone

With Git installed, run these commands in a macOS or Linux terminal. Clone into
a directory where you keep personal tools:

```sh
git clone https://github.com/lukenguyen-me/luke-mode.git
cd luke-mode
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

## Use

```text
$luke-mode Explain how refresh tokens rotate. Leave the code unchanged.
$luke-mode Design an offline sync strategy. Discuss the trade-offs before implementation.
$luke-mode Add cursor pagination to GET /orders using the attached contract.
$luke-mode Fix duplicate orders after a checkout retry. Reproduce it first.
$luke-mode Simplify the payment adapter while preserving its behavior.
$luke-mode Review my uncommitted changes against the requirements in docs/orders.md.
```

Luke works in small verified steps and adapts investigation and verification to
the task's complexity, uncertainty, and impact. Before edits, it assesses affected
modules, callers, interfaces, shared state, and regression risks; trivial changes
need only a brief check. Delegate when a separate context, expertise,
or independent review improves the work; keep routine steps with their owner.
Most small tasks need no agents. Code changes and test runs are sequential.

Unresolved product requirements and consequential architecture choices belong
to the human. Routine implementation choices proceed within the agreed scope.
Local changes and verification are the default deliverable. Commits, PRs, and
tracker updates follow the user's request or existing authorization.

## Set up Luke Mode

```text
$luke-mode setup
```

Setup configures personal model roles and checks Matt's toolkit configuration
for the current repository. The model stage discovers the active harness's
advertised models and recommends an exact model and supported effort for each
role. Confirm the four choices once. Luke saves the personal model preferences,
normally at `~/.config/luke-mode/models.md`.

Matt's `$setup-matt-pocock-skills` configures each repository's issue tracker,
domain docs, and triage labels when needed. Luke reuses complete existing setup.
When setup is missing, it checks that the installed skill is usable and provides
the next action. Matt's setup is user-only, so explicitly invoke
`$setup-matt-pocock-skills` to run it; naming both skills in the same request also
works. That skill owns the proposed repository changes and confirmation steps.
Luke reports model configuration and repository readiness separately.
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
separate harness profiles. `inherit` is a valid deliberate choice. Without setup,
Luke can work directly in the current session. Four roles do not require four
agents, and a saved mapping does not imply its model ran during direct execution.

The Reasoning mapping also serves as the suggested parent model for difficult
tasks. Change the parent through Codex's `/model` picker or `codex --model MODEL`;
setup cannot switch an already running parent. Native subagent capabilities and
model defaults depend on the current session. [Codex subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)

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

The core and playbooks are Markdown. Harness details live in
[the Codex adapter](skills/luke-mode/adapters/codex.md). V1 targets Codex; Claude Code
and Cursor adapters are not implemented or claimed as validated. In particular,
Codex's invocation policy does not enforce explicit-only behavior in Claude Code.
A future adapter must configure Claude's own invocation control and validate its
delegation behavior.

Try the [routing and behavior scenarios](scenarios/routing.md). See
[research and design choices](docs/research.md) for provenance and limitations,
and [V1 validation](docs/validation.md) for observed results and remaining coverage.
