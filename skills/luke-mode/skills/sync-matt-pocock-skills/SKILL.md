---
name: sync-matt-pocock-skills
description: Sync Matt Pocock's skill set from mattpocock/skills, updating installed skills and adding new ones. Use when the user requests a Matt toolkit sync, refresh, installation, or update for Luke Mode.
---

# Sync Matt Pocock Skills

This is Luke Mode's toolkit sync sub-skill. It ships inside `luke-mode`;
install only the parent bundle.
Invoke with `$sync-matt-pocock-skills` in Codex or `/sync-matt-pocock-skills` in
Cursor Cloud and Claude Code. `$luke-mode sync Matt's skills` and its `/` equivalent route
here. Sync installs current upstream skill files; per-repository configuration
belongs to [setup-luke-mode](../setup-luke-mode/SKILL.md).

Use the official source, [mattpocock/skills](https://github.com/mattpocock/skills).
Check its current installation guide and the chosen installer's documentation
at execution time. Discover the full current skill inventory, including
`setup-matt-pocock-skills`; a fixed list of Luke's preferred primitives misses
new upstream skills. Preserve Matt's invocation policies and supporting files.

## Resolve the target

Read [harness selection](../../references/harnesses.md), the matching
adapter, and [composition](../../references/composition.md). Resolve links from
this file's actual installation directory. Read applicable project instructions.
Inspect the skill roots and installation metadata to establish the existing method, agent, scope,
source, and symlink targets. A similarly named local skill is not proof of Matt's provenance.

Reuse an established installation method and scope. When none exists, use the
user's requested agent and scope; ask only if those cannot be inferred from the
request and environment. If both project and global installations or both plugin
and file installations conflict, resolve which one owns this sync before writes.
Keep disabled skills disabled and preserve unrelated skills, Luke's model
profile, repository guidance, and tracker settings.

## Refresh the complete set

Obtain current upstream files in a temporary checkout or through the installer's
read-only listing. Record the upstream revision or tree metadata when exposed.
Compare the expected inventory and resources with the target before replacement.
For editable installations, use the recorded installed baseline when available
to identify local customizations. Back up affected files and reconcile clear
customizations with the refreshed version before publishing; ask only about
unresolved conflicts or a requested change of installation method.

Choose the existing installation route:

- **Skills CLI:** Re-run `add` for the official source with all skills selected
  and one specific agent. This refreshes existing skills and discovers new ones.
  For an established global Codex installation, the command is:

  ```sh
  npx skills@latest add mattpocock/skills --skill '*' --agent codex --global --yes
  ```

  For a project installation, omit `--global` and run in the owning repository.
  For Cursor, use `--agent cursor`; for Claude Code, use `--agent claude-code`. Use `--yes` only after resolving the target
  and local changes. Keep staged customization merges outside the target while
  `add` runs, then reapply them before verification. Avoid `--all`, which targets
  every agent, and an unfiltered `skills update`, which can update unrelated sources.
  If a current CLI provides source-scoped updates, still run `add` to include
  newly added upstream skills.
- **Plugin:** Refresh the existing Matt plugin with the host's supported update
  controls. The current upstream Codex plugin updates at startup; confirm the
  host's current behavior and refresh discovery when needed. Preserve this route
  instead of adding duplicate file installations or editing plugin caches. If
  the host cannot update in this session, report the exact pending host action.
- **Manual checkout or copy:** Fetch the official upstream into a temporary
  checkout, retain the original until the replacement is verified, and copy
  complete skill directories into the selected root. Follow current upstream
  layout and harness requirements. Preserve customizations and unrelated entries;
  report removed or renamed upstream skills and resolve conflicts before removal.

In Cursor Cloud, update files in the actual run's repository or use Cursor's
documented personal skill sync from `~/.cursor/skills/`. A laptop's Codex install
does not update a Cloud run. Verify native invocation metadata; preserve any
required Cursor policy conversion rather than assuming Codex metadata applies.

## Verify and report

Read back the installed files and compare every expected upstream skill and its
resources with the refreshed inventory. Check names, descriptions, invocation
policies, resolved links, and provenance through files or installer lock metadata.
Verify native discovery if the harness exposes it; distinguish installed files
from skills loaded into an already running session.

Report the source, revision evidence, agent, target scope/path, added and updated
skills, preserved customizations, and any pending conflict or discovery refresh.
Claim a complete latest sync only after the full current inventory is accounted
for. Network failures, unavailable host controls, and unverified entries remain
pending. Installation alone does not run Matt's user-only setup workflow or
establish repository readiness. When setup is requested too, sync first, then
run `setup-luke-mode` against the refreshed installed requirements.
