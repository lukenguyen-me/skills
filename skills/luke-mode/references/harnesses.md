# Select the active harness

Identify the execution harness from the current session's platform identity and
native tools. A model provider, repository config, or skill installation path
does not identify it: Cursor can use GPT models and discover Codex skill folders.
An external Cursor connector in a Codex session does not make that session Cursor.

| Active execution harness | Model profile heading | Adapter | Skill command |
| --- | --- | --- | --- |
| Codex | `Codex` | [Codex](../adapters/codex.md) | `$luke-mode` |
| Cursor Cloud Agent | `Cursor Cloud` | [Cursor Cloud](../adapters/cursor-cloud.md) | `/luke-mode` |

Read the matching adapter before harness-specific discovery or configuration.
Its capabilities remain subject to the tools actually exposed in this session.
Resolve the harness once per task and revisit it after a genuine handoff into
another runtime. A delegated task that stays in the same harness keeps that
harness's profile; a separate cloud run establishes its own capabilities.

When platform identity is unclear, keep ordinary work in the current session.
Ask which harness is active before saving a profile or launching a role whose
settings depend on it. Keep the profile unresolved until the harness is known.

Cursor's editor and CLI are distinct from Cursor Cloud. Their local model catalog
and tool availability do not prove Cloud access. This version implements Codex
and Cursor Cloud adapters; other harnesses can use the portable playbooks directly
with disclosed limits, without applying either adapter's models or native commands.
