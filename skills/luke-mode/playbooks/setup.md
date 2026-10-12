# Setup

Run as `$luke-mode setup` in Codex or `/luke-mode setup` in Cursor Cloud and
Claude Code. Keep the working directory in the user's project. Read applicable
project instructions before configuration.

Full setup runs dependency installation, model configuration, and repository
setup in that order. It authorizes those stages together; do not require another
sync or Matt setup command from the user. A model-only request, such as
`configure models`, runs only the model stages. A toolkit-only request runs
dependency installation and repository setup.

Read [harness selection](../references/harnesses.md),
[models](../references/models.md), and the selected adapter before proposing
settings. Model configuration writes only the chosen Luke models file.
Matt's installed setup skill owns repository configuration. Preserve the
harness's global defaults and unrelated skills.

## Install missing dependencies

Read [dependencies](../references/dependencies.md): it owns the skill list,
the agents, the ref, and the install checks. A dependency is missing when it
fails those checks at project scope, including when one agent's root lacks it.
Install all missing skills of a source in one `add`. A full setup request
authorizes this installation. It does not authorize replacing a hand install,
overwriting unresolved customizations, or enabling disabled skills.

Installation makes the PStack skills available; it does not create or maintain
this project's `verify-<app>` skill. Run either authoring workflow only when
explicitly named.

Check required tools from the installed instructions and selected project
workflow. Use existing tools; install missing local dependencies with the
project's package manager when permitted. Account login, credentials, unavailable
package managers, or external service provisioning remain explicit pending
steps. Run read-only version or availability checks afterward. Models can be
configured independently while a toolkit dependency is pending. Updating a
complete dependency installation belongs to [sync](sync.md), on request.

## Discover and propose

1. Establish the active harness and available delegation/model controls. Use
   exposed runtime model metadata first, then a current native catalog if one
   is available. Inspect only relevant existing model preferences and configuration.
   Do not spawn agents or make inference calls just to enumerate models.
2. Read the existing models file, if any. Preserve other harness profiles and
   unrelated user notes. Reuse confirmed choices unless the user wants changes.
   Apply the missing-heading warning from [models](../references/models.md).
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
[composition](../references/composition.md) before resolving the installed
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
   installed prerequisites. Report dependency availability, model
   configuration, and repository toolkit readiness separately. Full setup is
   complete when all three stages are verified or explicitly skipped by the
   user. A pending stage still permits independent work under the composition
   fallback rules. Re-running setup reuses completed stages.
