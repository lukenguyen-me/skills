# Setup Luke's model roles

This is a prompt-driven setup inside `$luke-mode`, not a CLI. Configure the four
portable roles for the active harness. Read [models](models.md) and the relevant
harness adapter before proposing settings. Setup changes Luke's personal models
file only; it does not configure an application, alter other skills, or change
the harness's global defaults.

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

Done when all four choices are accepted, persisted, and accurately described.
If writing is blocked, return the exact accepted draft and pending step without
claiming setup completed. Re-running setup updates the same profile.
