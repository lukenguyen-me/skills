# Role models and delegation

## Profile and resolution

Resolve the active harness through [harness selection](harnesses.md). Select one
models file in this order: the user's explicit path, the owning repository root's
`.luke-mode/models.md` if present, then `~/.config/luke-mode/models.md` if present.
Resolve explicit relative paths from the user's working directory. Report the
selected path when model routing matters. Keep one source for the whole profile;
do not fill missing roles from a second file.

Read only the heading matching the active harness: `Codex` or `Cursor Cloud`.
A file containing only another harness's settings has no active profile, even
when the model provider or identifier is available in both harnesses. Preserve
other headings during setup. User instructions and harness/repository constraints
take priority over saved preferences.

The repository file is optional and makes preferences available to Cloud runs
that clone it. Create it only when the user chooses that save path. A local
personal file does not travel with the repository or Cursor skill sync.

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
   proof of live access. Save model IDs and effort separately; the adapter may
   translate them into its documented native invocation syntax.
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
The [whole-spec mode](implement-spec.md) has its own capability preflight.
Luke-owned graph execution can use disclosed sequential parent work when the
requirements allow it. An explicitly requested Matt workflow still requires its
native implementation, integration, and review capabilities; parent execution
does not silently satisfy that different owner choice.

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
and test execution. For [whole-spec execution](implement-spec.md#scoped-concurrency)
selected by Implement or an explicit Matt workflow request, independent
worktrees and runtime resources permit concurrent Coding owners, with one
writer per worktree and a single integration writer. Reserve native capacity
for integration and the chosen review process; review roles run after
implementation owners stop mutating the reviewed snapshot.
Wait for and inspect results before advancing a dependent step. A failure or
missing report remains a gap. Retry only when new information
or a recoverable failure justifies another attempt; do not repeat unsuccessful
delegation without addressing its cause.
