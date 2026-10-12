# Skill dependencies

Luke installs and updates the skills listed here, and only these. Other skills
from the same sources are the user's own choice; setup and sync leave them as
they are.

## Matt Pocock's skills

Source `mattpocock/skills`, tested at tag `v1.3.1`.

| Skill | Used by |
| --- | --- |
| `setup-matt-pocock-skills` | Setup's repository stage |
| `tdd` | Implement, Fix, Refactor, whole-spec |
| `code-review` | Implement, Fix, Refactor, Review, whole-spec |
| `diagnosing-bugs` | Fix |
| `codebase-design` | Design, Refactor |
| `domain-modeling` | Design, `grill-with-docs`, and `triage` |
| `grilling` | Design, `grill-with-docs`, and `triage` |
| `grill-with-docs` | Design (user-only) |
| `research` | Explore |
| `to-spec` | Design (user-only) |
| `to-tickets` | Design, Implement, whole-spec (user-only) |
| `implement` | Implement's sequencing (user-only) |
| `implement-spec` | The explicit `implement-spec` route (user-only) |
| `triage` | The Triage route (user-only); its presence makes Matt's setup write the triage-label mapping |

## PStack

Source `backnotprop/pstack`, which publishes no release tags:
`create-verification-skill` and `maintain-verification-skill`. Install only
these two; PStack's `tdd` conflicts with Matt's.

## Install with the Skills CLI

The Skills CLI (`npx skills@latest`) is the only installer. It writes the skill
files, the agent links, and the `skills-lock.json` entry together, so every
dependency has recorded provenance. When `add` fails, the dependency stays
pending with the CLI's error; hand links and hand copies are never a fallback.

Scope is the project: run from the repository root, without `--global`.
Global installations belong to the user; leave them untouched, and install the
project dependency even when a global copy exists.

1. **Agents.** Pass every agent the repository uses, plus the active harness:

   | Signal | Agent |
   | --- | --- |
   | `.agents/skills/` exists | `codex` (Cursor and the other universal agents share this root) |
   | `.claude/skills/` exists | `claude-code` |
   | Active harness | `codex`, `cursor`, or `claude-code` |

   With several agents the CLI keeps one copy in `.agents/skills/<name>` and
   links `.claude/skills/<name>` to it. A lone copy in `.claude/skills/` is
   right only when Claude Code is the only agent.
2. **Ref.** Pin Matt's source to a tag: `mattpocock/skills#<tag>`. Use the
   `ref` from the skill's lock entry when present, otherwise the tested tag
   above; sync chooses its own target tag. Pin PStack only when its lock entry
   has a `ref`.
3. **Command.** Run one `add` per source, naming every skill it installs:

   ```sh
   npx skills@latest add 'mattpocock/skills#v1.3.1' --skill tdd code-review --agent codex claude-code --yes
   ```

   Name skills literally. In zsh, `--skill $S` passes a space-separated
   variable as one word; use an array if the names come from a variable.
   `--skill '*'`, `--all`, and an unfiltered `skills update` reach beyond this
   list.

## Entries the CLI did not make

A dependency in a skill root without a lock entry, or a link pointing outside
the CLI's layout (for example into a Luke checkout), is a hand install. Report
its path and target. Re-running `add` replaces it, so do that only after the
user agrees. Before any `add` over an existing dependency, compare its files
with a temporary checkout of its locked ref; back up local edits and reconcile
them after the refresh, asking only about unresolved conflicts. Keep disabled
skills disabled.

## Verify

A dependency is complete when:

- `skills-lock.json` has its entry, with the expected source and, for Matt, the
  expected `ref`;
- each agent's root has it: a real directory in `.agents/skills/` when that
  root is in use, and `.claude/skills/<name>` as a link into it;
- `find -L <root> -maxdepth 1 -type l` prints nothing for each root in use, so
  no link is broken.

Re-running the same `add` leaves the files and the lock unchanged.
