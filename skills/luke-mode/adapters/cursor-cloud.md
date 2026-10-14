# Cursor Cloud adapter

Use this adapter for a task running inside Cursor Cloud. Read the current native
tool schemas and runtime metadata; documentation describes supported features,
not this run's model access or enabled tools.

## Runtime identity

Prefer the session's platform identity. If available, Cursor Cloud MCP's
`run-info` provides current-run metadata. On managed VMs, the local metadata API
can also expose runtime and the model serving the current turn:

```sh
curl -fsS --max-time 5 --unix-socket "${CURSOR_AGENT_SOCKET:-/run/cursor/api.sock}" \
  http://cursor-agent/v1/meta-data/agent/runtime
curl -fsS --max-time 5 --unix-socket "${CURSOR_AGENT_SOCKET:-/run/cursor/api.sock}" \
  http://cursor-agent/v1/meta-data/turn/model
```

Inspect only relevant keys. This API is in preview and is absent on self-hosted
workers; missing metadata does not establish a different harness. Use other
session evidence or leave identity/model unresolved. A serving-model value is
parent-run evidence, not a subagent catalog or proof of a delegate's model.
[Metadata](https://cursor.com/docs/cloud-agent/metadata),
[Cloud MCP](https://cursor.com/docs/cloud-agent/capabilities#cursor-cloud-mcp)

## Skills and invocation

Invoke Luke explicitly with `/luke-mode`; setup and sync run as
`/luke-mode setup` and `/luke-mode sync`. The main `SKILL.md` sets
`disable-model-invocation: true`, which Cursor reads; Codex's `agents/openai.yaml`
alone does not configure Cursor invocation. Setup installs the external PStack verification skills
with their upstream invocation policy. Naming a verification companion in the user's
Luke request explicitly selects that workflow.

Start discovery with the live catalog and applicable project instructions.
For missing candidates, look in the owning repository's `.cursor/skills/` and
`.agents/skills/`, including nested directories scoped to the affected package.
Cursor can also load `.claude/skills/` and `.codex/skills/` compatibility locations.
Search actual user-level skill roots only when needed; a laptop installation is
not evidence that the Cloud run has that skill. Apply [composition](../references/composition.md)
to the selected files, native invocation policy, resources, and disabled state.

Deliver skills as actual files in the cloned repository: install them at project
scope with the Skills CLI and commit the result. With `--agent cursor` the CLI
writes `.agents/skills/`, which Cursor reads. A symlink to a laptop checkout is
insufficient for a remote clone. Confirm discovery in the Cloud run. Full/toolkit Luke setup includes Matt's repository setup stage explicitly;
ordinary engineering requests still respect its user-only policy.
[Skills and sync](https://cursor.com/docs/skills)

## Models

Use only the `Cursor Cloud` profile from the models file selected by
[model resolution](../references/models.md). Preserve `Codex` and any other
profiles. Without a Cloud profile, use the current session for ordinary work;
an explicit model or independent-review requirement still needs actual support.

Discover choices from live tool metadata or the Cloud model picker. An already
available authenticated model-list capability can supply a current catalog:
Cursor documents `GET /v1/models` for Cloud agents. This is not permission to
obtain credentials or start another run. Local Cursor CLI catalogs and Codex's
model cache are not Cloud capability evidence. When exact choices cannot be
established, use the user's picker choices or confirmed `inherit` preferences.
[Cloud model catalog](https://cursor.com/docs/cloud-agent/api/endpoints#list-models)

Keep the catalog model ID and reasoning effort in separate saved columns. At
invocation, use the native tool's separate effort field if supported. If its
schema instead accepts Cursor's documented model-parameter syntax, translate a
validated ID/effort into `MODEL[effort=VALUE]`. Use only parameters and values
supported by that model and tool; otherwise save effort as deliberate `inherit`
or leave an exact unsupported requirement pending. Preserve the saved base ID.
Existing custom subagents may also declare a model; inspect the effective
definition and launch override before relying on it.

The parent model is selected by Cursor's run settings or model picker. Setup
cannot switch it. `inherit` intentionally follows the native parent's model,
including the model Cursor resolves for Auto. Auto is not an exact model ID.

Cursor may substitute a model because of plan or team restrictions. Inspect
returned metadata or the subagent task card when available. A mismatch fails
Luke's exact-model requirement; stop dependent work and report it. If actual
model or effort cannot be observed, report the requested settings as unverified
and keep an explicitly required setting unresolved. A parent metadata read
does not verify a delegate.
[Subagent models](https://cursor.com/docs/subagents#model-configuration)

## Delegation, verification, and delivery

Use native Task/subagent tools when exposed, following their actual schemas.
Pass a complete bounded brief: Cursor subagents begin with separate context and
do not receive prior conversation history. Existing `.cursor/agents/` definitions
can be used when their model and scope match. Setup saves model preferences;
creating permanent custom agents is separate requested work.

Keep mutations and test runs sequential, except when the selected
[whole-spec contract](../references/implement-spec.md#scoped-concurrency)
establishes isolated worktrees and resources. Native background tasks may serve
independent tickets when exposed; dependent integration and review await
completed results. Verify each worker's owning checkout and resource isolation
inside this Cloud run. Explorers and Reviewers run read-only, and Verifiers write
only build outputs, logs, and evidence; use an available native read-only
definition or permission control, and otherwise describe the brief as a prompt
constraint. Inspect returned diffs, artifacts, and model evidence. Never substitute
a built-in fast worker for an exact configured role just because it is available.

If delegation or a required override is absent, apply the shared fallback rules.
Do not start a nested CLI, call the Cloud Agents API to create another agent, or
use `/in-cloud` as a substitute for missing in-session delegation.
[Native subagents](https://cursor.com/docs/subagents)

Verify inside the run's actual checkout and environment. Resolve project checks
and compatible verification skills there; laptop paths, services, and macOS-only
tools are not Cloud evidence. Use available browser/computer tools when the
acceptance criteria require them. Inspect existing `.cursor/environment.json`
or project Cloud instructions when needed for tests. Luke setup does not provision
an application environment or change its startup configuration.
[Cloud environment](https://cursor.com/docs/cloud-agent/setup)

Respect the run's authorized branch and delivery configuration. Cursor may manage
pushes and PR handoff at the harness level; Luke does not add extra commits,
pushes, or PR actions just by being invoked. Under
[autopilot](../playbooks/autopilot.md), Luke opens no second PR beside the
run's own: it publishes [PR evidence](../references/evidence.md) from the run's
environment and writes the body to the run's PR with `gh pr edit` when `gh` is
authenticated, otherwise returns the body in the handoff. Report the actual changed workspace,
checks, artifacts, and any unresolved model or capability requirement.
