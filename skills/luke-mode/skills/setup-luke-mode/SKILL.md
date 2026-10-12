---
name: setup-luke-mode
description: Bootstrap Luke Mode from one installation by registering bundled commands, installing missing Matt Pocock and PStack skills, configuring model roles, and setting up the current repository. Use for setup-luke-mode, first-project setup, or scoped model/toolkit configuration.
---

# Setup Luke Mode

This sub-skill ships inside `luke-mode`; install only the parent bundle.
Resolve shared references from this file's actual installation directory.
Keep the working directory in the user's project. Read applicable project
instructions before configuration.

Invoke with `$setup-luke-mode` in Codex or `/setup-luke-mode` in Cursor Cloud and
Claude Code. `$luke-mode setup`, `$luke-mode setup-luke-mode`, and their `/` equivalents
route here as well. When the separate command is not indexed yet, use the
parent route or a plain request to run `setup-luke-mode` from Luke Mode.
Full setup runs command registration, dependency installation, model
configuration, and repository setup in that order. It authorizes those setup
stages together; do not require another sync or Matt setup command from the user.
A model-only request, such as `configure models`, runs only the model stages.
A toolkit-only request runs dependency installation and repository setup.

Read [harness selection](../../references/harnesses.md),
[models](../../references/models.md), and the selected adapter before proposing
settings. Model configuration writes only the chosen Luke models file.
Matt's installed setup skill owns repository configuration. Preserve the
harness's global defaults and unrelated skills.

## Register bundled commands

Inspect native discovery first. If both bundled commands already resolve
to this Luke installation, reuse them. Otherwise run the bundled helper with
the active harness's writable skill root as an explicit argument:

```sh
python3 <luke-mode-directory>/scripts/register-subskills.py <active-skill-root>
```

Prefer the root containing the installed Luke entry, preserving its scope;
resolve the entry's symlink target separately from the discovery root. In
Cursor Cloud use files in the actual checkout or synced Cursor skill root.
The helper links each command to its bundled source, so Luke remains the source
of truth. It preserves existing matching links and refuses conflicting entries.
Inspect conflicts, including older standalone companions, before replacing
anything; keep using the bundled route while a conflict is unresolved. Obtain
filesystem permission only when the harness requires it. Refresh discovery if
supported; report any restart needed without stopping the remaining setup.

## Install missing dependencies

Resolve Matt's installation method, agent, and scope using the
[sync workflow](../sync-matt-pocock-skills/SKILL.md). Reuse a complete, compatible
installation. If required skills or resources are absent, use that workflow
to install the complete official toolkit, including `setup-matt-pocock-skills`.
For a new installation, default to the active agent and Luke's installation
scope; ask only when the target cannot be inferred or installations conflict.
A full setup request authorizes this installation. It does not authorize
overwriting unresolved customizations or enabling disabled skills.

Install PStack's two verification-authoring skills as external dependencies
from [backnotprop/pstack](https://github.com/backnotprop/pstack). Check its current
installation guide and fetch a current inventory before installing. Select only
`create-verification-skill` and `maintain-verification-skill`, with all their
supporting resources; Luke contains no copies of them. For global Codex:

```sh
npx skills@latest add backnotprop/pstack --skill create-verification-skill maintain-verification-skill --agent codex --global --yes
```

Use the same resolved agent and scope as the Matt installation; omit `--global`
for project scope and use `--agent cursor` for Cursor or `--agent claude-code` for
Claude Code. Reuse a complete existing
PStack installation, including a plugin route; preserve customizations and
resolve conflicting copies or unknown provenance before writes, following the
sync workflow's installation safeguards. Keep disabled skills disabled. Never
install all of PStack: its `tdd` would conflict with Matt's toolkit. Preserve
upstream invocation metadata, licenses, and linked resources. Verify both skills
and their resources from installed files, and record source/revision evidence.
Installation makes them available; it does not create or maintain this project's
`verify-<app>` skill. Run either authoring workflow only when explicitly named.

Check required tools from the installed instructions and selected project
workflow. Use existing tools; install missing local dependencies with the
project's package manager when permitted. Account login, credentials, unavailable
package managers, or external service provisioning remain explicit pending
steps. Run read-only version or availability checks afterward. Models can be
configured independently while a toolkit dependency is pending. Refresh an
otherwise complete dependency installation only when the user requests an update.

## Discover and propose

1. Establish the active harness and available delegation/model controls. Use
   exposed runtime model metadata first, then a current native catalog if one
   is available. Inspect only relevant existing model preferences and configuration.
   Do not spawn agents or make inference calls just to enumerate models.
2. Read the existing models file, if any. Preserve other harness profiles and
   unrelated user notes. Reuse confirmed choices unless the user wants changes.
3. Recommend one exact model and a supported reasoning effort for each role:

| Role | Selection target |
| --- | --- |
| Reasoning | Strongest available for architecture, complex debugging, design trade-offs |
| Coding | Balanced model suited to feature implementation and refactoring |
| Worker | Fast, lower-cost model suited to tests, mechanical edits, simple investigation |
| Reviewer | Capable model for independent code review and verification |

Use current capability descriptions to make recommendations, not invented name
rankings. When the selected adapter lists a recommended profile, propose it. Same-model mappings are valid. Reviewer independence comes from its
separate context. `inherit` is also a valid explicit preference.

If the environment cannot expose available models, ask for the user's native
model-picker choices. If only cached metadata is available, label it and confirm
the choices against the picker or user-observed access. Never call a catalog an
entitlement guarantee. Keep an unknown role unresolved instead of inventing an ID.

## Confirm and save

Show the active harness, save path, and one four-row table with exact model IDs,
supported effort, and any unverified access. Ask for confirmation or role-specific
changes, unless the user already accepted those exact settings. Default fallback
is `stop`. An optional `parent` fallback must be explicitly accepted, means direct
execution in the current session, and cannot satisfy an independent-review requirement.

Write to the user's explicit path, otherwise the existing selected repository
models file, otherwise `~/.config/luke-mode/models.md`. Creating
`.luke-mode/models.md` is an opt-in save choice for cloud portability. Obtain any
filesystem permission the harness requires. Preserve other profiles. Leave no
unresolved placeholders in a saved profile. Use this Markdown structure, shown
here with valid intentional inheritance choices:

```markdown
# Luke Mode models

## Codex

| Role | Model | Reasoning effort | Fallback |
| --- | --- | --- | --- |
| Reasoning | inherit | inherit | stop |
| Coding | inherit | inherit | stop |
| Worker | inherit | inherit | stop |
| Reviewer | inherit | inherit | stop |
```

For an exact mapping, replace `inherit` with the selected real identifier and
supported effort. For a harness without a per-agent effort control, record
`inherit` for effort and explain that limitation. Keep a separate heading for
each configured harness; use `Codex`, `Cursor Cloud`, or `Claude Code` as selected
by the adapter. Change the example heading for a Cloud or Claude Code profile;
retain existing sections for other harnesses unchanged.

Read back the saved profile and report its path. Say which values were validated
against a catalog and which were actually observed in a run. Choosing a Reasoning
model does not switch the parent session. If the user wants that model as the
parent, provide the harness's supported launch or model-picker instructions.

Model configuration is done when all four choices are accepted, persisted, and
accurately described. If writing is blocked, return the exact accepted draft and
pending step without claiming model configuration completed. Re-running setup
updates the same profile.

## Set up Matt's toolkit for this repository

Matt's setup is per repository; a saved personal model profile does not establish
toolkit readiness in another project. Read
[composition](../../references/composition.md) before resolving the installed
`setup-matt-pocock-skills` workflow.

1. Inspect the current repository's `AGENTS.md` or `CLAUDE.md` and the setup files
   they reference, normally under `docs/agents/`. Check tracker configuration,
   domain layout, and any required triage-label mapping against the installed
   Matt skills' requirements. Reuse complete existing configuration; rerun setup
   only for missing configuration or a requested reconfiguration.
2. When setup is needed, resolve the installed `setup-matt-pocock-skills` skill
   and its resources after the dependency stage. If installation failed, or
   the skill is disabled or incompatible, leave this stage pending with the
   concrete reason. Preserve disabled state.
3. Full or toolkit-only Luke setup explicitly includes Matt's repository setup
   stage. Announce that stage and follow the installed workflow without asking
   the user to type a second command. Preserve its user-only policy for ordinary
   engineering requests; model-only setup does not select it.
4. Let the installed workflow own repository discovery, choices, drafts, and
   writes. Honor its confirmation steps and existing user decisions. Show
   concrete drafts before any required approval. Its possible changes include
   project instructions, `docs/agents/`, and tracker labels; model confirmation
   alone does not authorize those changes.
5. Read back generated guidance and its referenced configuration to verify
   installed prerequisites. Report command registration, dependency availability,
   model configuration, and repository toolkit readiness separately. Full setup
   is complete when all four stages are verified or explicitly skipped by the
   user. A pending stage still permits independent work under the composition
   fallback rules. Re-running setup reuses completed stages.
