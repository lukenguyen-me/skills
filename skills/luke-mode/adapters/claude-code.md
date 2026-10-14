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
result that turns out ambiguous to Reasoning or Coding instead of retrying
with Haiku.

The Agent tool's `effort` field accepts `low`, `medium`, `high`, `xhigh`, and
`max`. It may be set only when the user or a skill asks for it explicitly; a
saved profile value other than `inherit` is that explicit request. A role agent
carries the profile effort in its definition, so omit `effort` on role agent
calls. On a fallback call, pass a saved value other than `inherit`; with
`inherit`, omit the field so the delegate runs at its usual effort.

The parent model is selected with `/model` or `claude --model MODEL`. A skill
cannot switch it. With a configured profile the parent orchestrates, even when
its model matches a role's mapping.

## Role agents

Setup generates one agent definition per role from the profile, so the profile
model applies even when an Agent call omits `model`:

| Role | `subagent_type` | Tools |
| --- | --- | --- |
| Reasoning | `luke-reasoning` | Read-only list plus web lookup |
| Coding | `luke-coding` | All tools except `Agent` |
| Worker | `luke-worker` | Read-only list |
| Reviewer | `luke-reviewer` | Read-only list |

The read-only list includes Bash, so read-only scope there is a prompt
constraint, not a sandbox. Each body carries the delegate's standing rules,
since a delegate cannot load Luke Mode.

[`scripts/role_agents.py`](../scripts/role_agents.py) owns the files. It writes
them from the models file to `~/.claude/agents/` for the personal profile, or
`<repo>/.claude/agents/` for a repository profile:

```sh
python3 <skill-dir>/scripts/role_agents.py write --models <models-file> --dest <agents-dir>
python3 <skill-dir>/scripts/role_agents.py check --models <models-file> --dest <agents-dir>
```

`write` refuses to replace a same-named file it did not generate; show it to the
user and pass `--force` only with their approval. A project definition overrides
a personal one with the same name. The models file stays the source of truth;
edit it, then rewrite the agents.

## Delegation

Use the native Agent tool with the role agent as `subagent_type`, and omit
`model` so the definition applies it. A call's `model` overrides the
definition, so pass one only when it equals the profile. When the role agents
are not installed, fall back to `Explore` for Worker, `Plan` or `Explore` for
Reasoning, `general-purpose` for Coding, and a read-only type for Reviewer,
each with `model` from the profile. A fallback call without `model` inherits
the parent, which is the configured role only when the profile says `inherit`.
A composed skill's agent seats, such as `code-review`'s reviewers, spawn as the
role agent matching their work.

Spawn fresh agents, never `subagent_type: "fork"`: forks always run on the
parent model and ignore the `model` override. A new Agent call starts with no
conversation history, so pass a complete bounded brief.

### Routing hook

Luke's `SKILL.md` declares a `PreToolUse` hook on the Agent tool. Claude Code
registers it when the user invokes `/luke-mode`, and it stays active for the
rest of that session. The hook resolves the models file as
[model resolution](../references/models.md) does, minus an explicit path, and
does nothing without a `Claude Code` profile. With one, it denies:

- a fork;
- a type outside the four role agents while they are installed;
- a role agent call whose `model` or `effort` differs from the profile;
- a role agent whose definition disagrees with the profile's model or effort;
- a fallback call without a profile model while the role agents are missing.

Enforcement lasts for the rest of the session, beyond the Luke task. When later
work in that session needs another agent type, tell the user that a new session
lifts the hook.

Follow a denial's reason; it names the agent or setup step required. When it
asks for setup, stop delegating and report it. The hook is the Claude Code
backstop for strict routing. It enforces which agent and model a delegate gets;
the brief and the parent's own discipline still keep role work out of the parent.

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
