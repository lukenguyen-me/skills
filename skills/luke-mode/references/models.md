# Role models and delegation

## Profile and resolution

Use the models file explicitly supplied by the user, otherwise
`~/.config/luke-mode/models.md` if it exists. Read only the active harness's
profile. A profile for Codex is not a profile for Claude Code. Preserve user
instructions and harness/repository constraints above saved preferences.

An absent profile is an unconfigured state: continue ordinary work in the current
session and say so when model routing matters. Setup is optional. A supplied
profile without an entry for a required role needs that role configured; do not
guess a model. The four role mappings govern delegated work. Direct execution
uses the current session and is reported as direct execution, not as the mapped
role model having run.

For a delegated or explicitly required role:

1. Resolve its exact model and effort from the active profile. `inherit` is an
   intentional choice, not an unavailable-model fallback. Establish the effective
   inherited settings from runtime evidence; configured harness defaults can
   differ from the parent. Prefer explicit known parent values when the tool
   supports them and the user chose inheritance.
2. Validate the identifier and effort against the active tool's advertised
   capabilities or a current harness catalog. A cached catalog is a hint, not
   proof of live access. Do not rewrite model IDs to encode reasoning effort.
3. Confirm the tool supports the required override and context mode. A
   full-history fork may require inheritance; use a fresh bounded context for a
   different model when supported. Never claim an unsupported override took effect.
4. Announce the role and resolved settings before spawning. Inspect errors and
   returned model metadata when available. If the harness reports a substitution,
   stop accepting that run as the requested model and surface the mismatch.

If an exact choice is unavailable or cannot be applied, stop the affected
delegation and explain the cause. Use a fallback only if the user already
authorized it in the profile or current request, and announce it. Otherwise ask
for a model choice; continue unrelated work only. Never choose a closest model,
lower effort, or native default silently. If actual model metadata is unavailable,
distinguish a requested setting from an observed setting.

If delegation is absent and the request has no explicit model or independence
requirement, work sequentially in the parent and disclose the limitation. Do not
start a nested CLI, remote task, or new orchestration service as a substitute.

## Role use

Reasoning is for unresolved architecture, complex debugging, and consequential
trade-offs. Coding is for substantial feature work and refactoring. Worker is
for bounded tests, mechanical edits, or simple fact gathering. Reviewer is for
independent review or checking evidence in a separate context; independence does
not require a different model family.

Keep small steps with their current owner. Avoid creating a Worker just to run
one short command or a Coding agent just to make one obvious edit. A composed
skill's required reviewers use Reviewer settings; do not add another panel over
the same work. Respect actual harness concurrency limits. If a required review
process cannot run, disclose the limitation and use direct review only when the
user's process and independence requirements allow it.

Plan the allocation before spawning. Each brief contains the task, owning
directory, permitted writes, relevant absolute pointers, acceptance evidence,
selected primitive if any, and a request for findings plus gaps. Specify no
nested delegation. Use disjoint outputs for read-heavy tasks; serialize editing
and test execution. Wait for and inspect results before advancing a dependent
step. A failure or missing report remains a gap. Retry only when new information
or a recoverable failure justifies another attempt; do not repeat unsuccessful
delegation without addressing its cause.
