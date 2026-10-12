# Claude Code adapter

Use actual session tools and metadata as the capability boundary. A Claude Code
version number or this document does not grant tools, model access, or permissions.

## Skills

Use the available-skills listing first. For a named candidate missing from it,
look in project `.claude/skills/` directories from CWD to the repository root,
then `~/.claude/skills/`. Plugin skills appear with a `plugin:skill` prefix and
keep their own install paths; use those pointers rather than scanning every
plugin cache. Resolve symlinks and read the selected skill's invocation policy:
`disable-model-invocation: true` in `SKILL.md` frontmatter makes it user-only.
Do not treat Codex-only `.agents/skills` or Cursor-only installations as active
Claude Code skills.

Luke's `SKILL.md` sets `disable-model-invocation: true`, so it runs only when the
user invokes it. Invoke skills through the native Skill tool. Luke runs as
`/luke-mode`; setup and sync run as `/luke-mode setup` and `/luke-mode sync`.
Project instructions live in `CLAUDE.md`; Luke
does not install an always-on rule there.

## Models

Use only the `Claude Code` profile from the models file selected by
[model resolution](../references/models.md). Preserve `Codex`, `Cursor Cloud`,
and any other profiles.

The native Agent tool accepts a per-delegate `model` of `haiku`, `sonnet`, or
`opus`. These family aliases are the exact identifiers for this harness; each
resolves to the current release of that family. Save the alias, not a dated
model ID. Claude Code may expose other values such as `fable`; use one only when
the live Agent schema advertises it and the user chose it.

Recommended profile, used when the user accepts defaults:

| Role | Model | Reasoning effort | Use |
| --- | --- | --- | --- |
| Reasoning | opus | inherit | Architecture, complex debugging, consequential trade-offs |
| Coding | sonnet | inherit | Main implementation worker: features, refactors, tests, edits |
| Worker | haiku | inherit | Read-only exploration needing little judgment: locating files, symbols, call sites, config values |
| Reviewer | opus | inherit | Independent review and evidence checks |

Keep Haiku to read-only lookups whose answer is a location or fact. Route test
writing, mechanical edits, and any investigation that requires judgment to
Coding even when the general role table calls it Worker work. Escalate a Worker
result that turns out ambiguous to the parent or Coding instead of retrying
with Haiku.

The Agent tool's `effort` field accepts `low`, `medium`, `high`, `xhigh`, and
`max`. It may be set only when the user or a skill asks for it explicitly; a
saved profile value other than `inherit` is that explicit request. With
`inherit`, omit the field so the delegate runs at its usual effort.

The parent model is selected with `/model` or `claude --model MODEL`. A skill
cannot switch it. A configured role can run directly when the parent's model
satisfies it; otherwise delegate or report the unresolved requirement.

## Delegation

Use the native Agent tool. Pass `model` from the profile for every role-mapped
delegate; omitting it inherits the parent or the agent definition's model and is
not the configured role. Choose `subagent_type` by scope:

- Worker exploration: `Explore`, which is read-only by tool restriction.
- Reasoning analysis or plans without edits: `Plan` or `Explore`.
- Coding: `general-purpose` or a matching project agent from `.claude/agents/`.
- Reviewer: a read-only type when one fits; otherwise state that read-only scope
  is a prompt constraint, not a sandbox.

Do not use `subagent_type: "fork"`: forks always run on the parent model and
ignore the `model` override. A new Agent call starts with no conversation
history, so pass a complete bounded brief. Existing `.claude/agents/*.md`
definitions may declare their own model; the call's `model` override takes
precedence, so inspect the definition before relying on its default.

Agents run in the background and report on completion. Wait for the
notification before a dependent step; never predict a pending result. Launch
independent read-only agents in one message so they run concurrently. Keep
edits and test runs sequential unless the selected
[whole-spec contract](../references/implement-spec.md#scoped-concurrency)
establishes isolated worktrees; `isolation: "worktree"` gives a delegate its
own checkout. One writer owns integration.

Do not start the Workflow tool, a nested `claude` CLI, or a remote agent as a
substitute for missing in-session delegation. Workflows need the user's
explicit opt-in.

The Agent result does not echo the serving model. Report delegated settings as
requested rather than observed unless the harness returns model evidence.
