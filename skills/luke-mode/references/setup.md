# Setup Luke Mode

`$luke-mode setup` configures four personal model roles and checks Matt Pocock's
toolkit setup for the current repository. A model-only request, such as
`$luke-mode configure models`, runs only the model stages below. A toolkit-only
request runs only [repository setup](#set-up-matts-toolkit-for-this-repository).

Read [models](models.md) and the relevant harness adapter before proposing model
settings. Model configuration writes only Luke's personal models file. Matt's
installed setup skill owns repository configuration; use the invocation rules
below. Preserve the harness's global defaults and installed skill files.

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
rankings. Same-model mappings are valid. Reviewer independence comes from its
separate context. `inherit` is also a valid explicit preference.

If the environment cannot expose available models, ask for the user's native
model-picker choices. If only cached metadata is available, label it and confirm
the choices against the picker or user-observed access. Never call a catalog an
entitlement guarantee. Keep an unknown role unresolved instead of inventing an ID.

## Confirm and save

Show one four-row table with exact model IDs, supported effort, and any unverified
access. Ask for confirmation or role-specific changes, unless the user already
accepted those exact settings. Default fallback is `stop`. An optional `parent`
fallback must be explicitly accepted, means direct execution in the current
session, and cannot satisfy an independent-review requirement.

Write the accepted active profile to `~/.config/luke-mode/models.md`, or the user's
explicit path. Obtain any filesystem permission the harness requires. Preserve
other profiles. Leave no unresolved placeholders in a saved profile. Use this
Markdown structure, shown here with valid intentional inheritance choices:

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
each configured harness; use `Codex` for this adapter.

Read back the saved profile and report its path. Say which values were validated
against a catalog and which were actually observed in a run. Choosing a Reasoning
model does not switch the parent session. If the user wants that model as the
parent, provide the harness's supported launch or model-picker instructions.

Model configuration is done when all four choices are accepted, persisted, and
accurately described.
If writing is blocked, return the exact accepted draft and pending step without
claiming model configuration completed. Re-running setup updates the same profile.

## Set up Matt's toolkit for this repository

Matt's setup is per repository; a saved personal model profile does not establish
toolkit readiness in another project. Read [composition](composition.md) before
resolving or invoking `setup-matt-pocock-skills`.

1. Inspect the current repository's `AGENTS.md` or `CLAUDE.md` and the setup files
   they reference, normally under `docs/agents/`. Check tracker configuration,
   domain layout, and any required triage-label mapping against the installed
   Matt skills' requirements. Reuse complete existing configuration; rerun setup
   only for missing configuration or a requested reconfiguration.
2. When setup is needed, resolve the installed `setup-matt-pocock-skills` skill,
   its resources, and invocation policy. If it is missing, disabled, or
   incompatible, report the prerequisite and leave repository setup pending.
   Installation or enabling a skill is separate authorized work.
3. Follow the resolved invocation policy. The upstream version is user-only:
   unless the user explicitly invokes it, show `$setup-matt-pocock-skills` as
   the next action and explain that it configures this repository. Keep
   repository setup pending. If the request already explicitly invokes both
   skills, proceed without asking the user to invoke it again. Reading its files
   does not bypass its policy.
4. When invocation is permitted, announce and follow the installed setup skill;
   let it own repository discovery, choices, drafts, and writes. Honor its
   confirmation steps and existing user decisions. Its possible changes include
   project instructions, `docs/agents/`, and tracker labels; model confirmation
   alone does not authorize those changes.
5. After an authorized run, read back the generated project guidance and its
   referenced configuration to verify the installed skills' prerequisites.
   Report personal model configuration and repository toolkit readiness
   separately. Full setup is complete when the personal profile is saved and
   verified, and repository prerequisites are verified or explicitly skipped by
   the user. A pending toolkit stage still permits ordinary work under the
   composition fallback rules.
