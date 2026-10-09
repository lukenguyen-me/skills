# Skill composition and evidence

## Resolve a candidate

Start with the active harness's available-skills metadata and project
instructions. Search known skill roots by the candidate's name only when needed;
catalogs can omit entries. Treat readable installed instructions as authoritative,
not an upstream summary or a remembered version. Resolve supporting links from
the selected skill's actual directory.

Before invoking a candidate, check:

- Its name, description, and invocation policy. Read `agents/openai.yaml` for
  Codex policy and relevant frontmatter for other harnesses. User-only skills
  require explicit invocation by the user; opening their files is not a bypass.
- Required supporting resources and skills. Resolve the relevant dependency
  chain before starting; a wrapper with a missing primitive is not usable.
- Preconditions, scope, side effects, tool capabilities, model requirements,
  and actual delegation limits. Check the effective enabled/disabled state
  when exposed by the harness. An explicitly disabled skill stays disabled.

If duplicate names resolve to different skills, prefer an explicitly selected
path; otherwise identify which fits the task and disclose an ambiguous choice.
Do not silently assume a project-specific skill is Matt's skill.

Invoke through the harness's skill mechanism when available. In Codex without a
Skill tool, read and follow the permitted skill's `SKILL.md` and needed resources.
Announce its use. Adapt tool names only when the available tool preserves the
required behavior. A critical missing capability is a compatibility failure.

## Workflow ownership and fallback

Luke borrows sequencing from user-only workflows such as `implement`,
`grill-with-docs`, `to-spec`, and `to-tickets`. It does not invoke them implicitly,
copy their content, or load them as a workaround for their policy. If the user
explicitly invokes one, let that workflow own its stage rather than running a
second Luke workflow over it. Apply the user's scope and existing authorization.

Keep one owner of each procedure. Once `tdd`, `diagnosing-bugs`, or `code-review`
is active, follow its actual instructions rather than restating or changing its
method. A requirement the user has already satisfied does not need another
confirmation. If a conflict cannot be resolved within the user's instructions,
skip that candidate, name why, and use direct execution where equivalent evidence
is possible. Do not claim the incompatible skill ran.

Missing optional skills do not block ordinary engineering work. Give a concise
fallback, use project conventions, and preserve the same acceptance criteria.
If the user explicitly requires that skill or the missing capability is essential,
report the blocked step and continue only independent work. Installation,
updating, and editing another skill are separate work, never an automatic repair.

## Verify the actual outcome

Before edits, discover project verification skills from project instructions
and available-skills metadata, matching the affected app and surface (for example,
`verify-drift`). Use the active harness adapter's discovery rules when the catalog
omits a candidate. Resolve policy and compatibility before proceeding. During
verification, invoke applicable, permitted skills; reading instructions alone
provides no execution evidence. If none can be used, disclose why and use
documented scripts, existing tests, and available controls for the real user path
under the fallback rules above. Creating a verification skill is separate
requested work.

Choose evidence before edits and retain commands, relevant outputs, and artifact
locations after execution. Evidence must match the task: failing then passing
symptom for Fix, changed behavior for Implement, equivalent behavior for Refactor,
and inspected sources for Explore or Review. Review assesses evidence; agreement
between reviewers is not a replacement for it. Redact secrets in reported output.

Choose the least costly checks that establish the affected behavior and cover
the identified regression risks. A focused behavioral test can suffice when it
exercises the acceptance criteria; use runtime or integration checks when they
depend on wiring, shared state, or a user interaction that those tests omit.
For trivial edits, a focused inspection or check is enough unless project
requirements or risk justify broader verification. Widen checks when new changes,
failures, or unresolved risks warrant it.

Successful compilation or passing unit tests alone do not prove feature
correctness: identify which acceptance criteria the evidence actually exercises.
Record passed, failed, and unrun checks distinctly, with remaining risks.
Investigate failures in scope; identify unrelated baseline failures or missing
access. Do not mark acceptance criteria verified from a build result, old artifact,
mock-only path, or worker self-report. Inspect a delegate's diff and evidence
before accepting its result.
