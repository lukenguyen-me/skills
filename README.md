# Luke Mode

Luke Mode is an explicitly invoked personal engineering skill for Codex. Describe
an outcome, and it selects a playbook, composes compatible installed skills,
and works toward evidence you can inspect.

Matt Pocock's skills remain the engineering toolkit. Luke adds routing, sequencing,
and optional model-aware delegation. It contains none of Matt's skill files and
requires no CLI, MCP server, or orchestration service.

## Install globally in Codex

Keep this checkout wherever you maintain personal tools. From its root, create
one user-level symlink:

```sh
luke_mode_repo="$(pwd -P)"
mkdir -p "$HOME/.agents/skills"
if [ -e "$HOME/.agents/skills/luke-mode" ] || [ -L "$HOME/.agents/skills/luke-mode" ]; then
  printf '%s\n' 'Inspect the existing Luke Mode installation before updating it.'
else
  ln -s "$luke_mode_repo/skills/luke-mode" "$HOME/.agents/skills/luke-mode"
fi
```

Open Codex in any existing project and select `$luke-mode` or find it in `/skills`.
If discovery has not refreshed, restart Codex. Keep the checkout at the symlink's
target; edits here update the installed skill. Avoid installing a second copy
under another skill root. To remove this symlink, use
`unlink "$HOME/.agents/skills/luke-mode"`; the checkout remains.

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

## Set up portable model roles

```text
$luke-mode setup
```

Setup discovers the active harness's advertised models and recommends an exact
model and supported effort for each role. Confirm the four choices once.
Setup saves only Luke's personal model preferences, normally
at `~/.config/luke-mode/models.md`.

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
`diagnosing-bugs`, and `code-review`, alongside `tdd`. Install them through your
preferred Matt skill installation, separately from Luke. Choose one installation
method to avoid duplicates. Some Matt workflows require per-project setup, a
tracker, confirmed test seams, or a committed review baseline; Luke checks the
installed version's requirements before invoking it. [Matt's installation guide](https://github.com/mattpocock/skills#installation-30-second-setup)

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
