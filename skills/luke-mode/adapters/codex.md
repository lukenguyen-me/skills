# Codex adapter

Use actual session tools and metadata as the capability boundary. A Codex version
number or this document does not grant tools, model access, or permissions.

## Skills

Use the available-skills catalog first. For a named candidate missing from it,
look in project `.agents/skills` directories from CWD to the repository root,
then `~/.agents/skills`, and available legacy `$CODEX_HOME/skills` or
`~/.codex/skills`. Respect exposed disabled state. Plugin skills may have their
own catalog paths: use those pointers rather than scanning every plugin cache.
Resolve symlinks and read the selected skill's invocation policy. Do not treat
Claude-only installations as active Codex skills.

Luke's `agents/openai.yaml` disables implicit invocation. Install the skill in
one discovery location; two same-name installations can create ambiguous choices.
Project instructions remain project-owned; Luke does not install an always-on
`AGENTS.md` rule.

## Models

Prefer model names and supported effort levels exposed by the live subagent
tool. A native `model/list` capability can provide catalog metadata when present.
Without one, readable `$CODEX_HOME/models_cache.json` is only cached evidence;
`~/.codex/models_cache.json` is the default when `CODEX_HOME` is unset. During
setup, ask the user to confirm choices with `/model` if access is uncertain.
Inspect relevant `agents` defaults or custom-agent overrides only when needed to
resolve effective settings. User config is not proof of the active thread's model.

Codex selects the parent model at launch with `codex --model MODEL`, or through
`/model` in an interactive session. A Markdown skill cannot change it. A configured
role can run directly when the active settings satisfy the requirement; otherwise
use a compatible delegated context or report the unresolved requirement.

## Delegation

Use exposed native subagent tools, such as `spawn_agent`, plus their corresponding
message/wait controls. Inspect their actual schemas. Request model and reasoning
overrides only when supported. If the schema uses `fork_turns`, use `none` for a
fresh context with different settings; full-history forks inherit settings when
the schema requires that. Other schema versions can differ.

Do not assume Cursor's `Task`, `subagent_type: poteto-agent`, cloud workers,
`run_in_background`, or custom agent registration exists. Creating an unrelated
Codex task is not a substitute for a missing subagent tool.

For reading and review, constrain the brief to read-only work. If a matching
registered read-only agent is available, its sandbox can enforce this; a prompt
alone is a behavioral constraint, not a new sandbox. Keep inherited permission
controls and preserve tool restrictions.

When a composed skill needs reviewers, run its bounded reviewer briefs using
the available native tools and the Reviewer settings. Pass the required source
pointers and rubric. Let the leaf own its procedure rather than making each
reviewer reload Luke's orchestration. Coordinate their work within the actual
runtime limits and prevent unplanned further delegation.

Read-only commands can still create caches, start services, or touch remote
state. Choose commands consistent with the user's scope. Run tests and edits
sequentially; reviewers inspect a stable diff and current verification evidence.
