# V1 validation

Checked on 2026-10-09. Behavioral checks used independent agents with Luke's
installed instructions and realistic requests in disposable projects. The
evaluators received raw fixtures, scope constraints, and no proposed solution.
The author then inspected the resulting files and verification evidence.

## Observed behavior

| Request | Result |
| --- | --- |
| Fix a 10% discount that leaves 10,000 cents unchanged; public test interface already agreed | Selected Fix, composed the installed TDD skill, and disclosed direct diagnosis and review because the optional primitives were absent. Added a symptom-specific test and corrected percentage savings using integer arithmetic. |
| Set up four already-confirmed exact Codex role mappings in a temporary preferences file | Saved all four mappings and `stop` fallbacks without repeating confirmation. Preserved the existing Claude Code profile and personal note. Validated model/effort support against exposed tool metadata; readback matched the accepted settings. |
| Review uncommitted orders changes using a configured, unadvertised Reviewer model | Selected Review and stopped the required role. Launched no substitute and produced no review findings. The existing code diff and Git status stayed unchanged. Reported the pending model decision. |
| In Codex, review a changed discount function using a file with separate Codex and Cursor Cloud profiles; the Codex Reviewer is unavailable while the Cloud Reviewer is advertised | Selected the Codex profile by session identity and stopped its unsupported Reviewer. Applied no Cloud settings, started no agents, ran no tests, and produced no completed review or verified findings. Fixture files remained unchanged. |

For the discount fix, `python3 -m unittest -v` passed all three tests. The author
also ran the resulting tests against the reconstructed original implementation:
the new 10% regression failed while the two existing endpoint cases passed.
Checks through the actual corrected public function covered fractional savings,
small and zero values, and large integers. Review was direct, not independent.

## Whole-spec routing

Three independent agents assessed read-only preflight requests in disposable
Git projects. The fixture used a local tracker, approved public test seams, and
three implementation tickets: A and B had no blockers; C depended on both.
Evaluators received the copied skill, raw project files, model preferences, and
scope constraints without an expected route or proposed result.

| Request and installation | Observed result |
| --- | --- |
| Implement the parent spec; Matt's original `implement-spec` absent | Selected Implement's Luke-owned whole-spec mode for all three children. Identified A/B as dependency-eligible and C as waiting for verified integration. Reported unresolved locale choices, available TDD, and direct fallbacks for absent optional review and verification skills. |
| Implement ticket A; its file links to the parent and siblings | Selected single-ticket Implement and kept A as the only requested implementation. Did not expand to B/C or require Matt's whole-spec workflow. Reused the approved seams. |
| Explicit `implement-spec` argument; the original workflow installed | Selected Matt as the execution owner, read its provenance and explicit-only policy, and left execution pending because required `code-review` was missing. Did not substitute Luke's direct review for that dependency. |

All three honored preflight-only scope. No implementation, tests, services,
installation, remote actions, or further delegation ran. The author compared
SHA-256 manifests for 38 files in the automatic fixture and 41 in the explicit
fixture; every file matched. HEAD, branch references, clean Git status, and the
single original worktree also matched their baselines.

These checks establish routing and prerequisite handling. They do not establish
runtime model inheritance, concurrent execution, or completed spec implementation.

## Current single-install package checks

Updated on 2026-10-13. Setup and sync are bundle routes (`playbooks/setup.md`
and `playbooks/sync.md`), not separate skills. Every dependency is installed
and updated with the Skills CLI at project scope. The earlier behavioral
observations above do not validate the revised workflow.

```sh
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/luke-mode
python3 -B -m unittest discover -s tests -p 'test_luke_mode_*.py' -v
npx skills@latest add ./ --list --full-depth
```

The first check reports one expected error: `disable-model-invocation` is not in
the Codex validator's allowed keys. Luke keeps it so Claude Code and Cursor
treat the main entry point as explicit-only; any other error is a real failure.

The bundle tests check that `luke-mode/SKILL.md` is the bundle's only skill
entry point and that every relative link resolves inside the bundle, so a CLI
install works from any skill root. The CLI listing must show `luke-mode` and
no setup or sync skill. No Matt or PStack workflow is vendored.

## PR evidence publishing

Checked on 2026-10-13 against a throwaway private GitHub repository.
`agent-browser` 0.38.1 took the screenshots and a recording, and `ffmpeg`
converted the recording to a GIF. GitHub accepted pushes to
`refs/evidence/<branch>`, served the files by commit SHA through the contents
API, and kept the PR body's image URLs unchanged in the rendered HTML. A fresh
`git clone` did not contain the evidence commit. A second publish chained on the
first, so earlier links stayed valid. In a logged-in browser, the PNG, WebP,
and animated GIF rendered inline in the private PR, and the video opened as a
link.

```sh
python3 -B -m unittest discover -s tests -p 'test_luke_mode_*.py' -v
```

The publish tests use a local bare remote: hidden ref and URLs, absence from a
network-style clone, chaining, and size and type limits.

## Remaining coverage

Live first-project setup, upstream dependency installation, native skill-loader
refresh, and Matt's repository configuration have not been exercised by these
local package checks. No global skill root, plugin cache, tracker, or actual
application verifier was modified by the tests. The setup and external
verification [scenarios](scenarios/routing.md) remain manual acceptance cases.

The earlier whole-spec checks establish routing and preconditions only. They do
not prove concurrent ticket execution, integration recovery, completed spec
verification, or external delivery. The blast-radius and runtime-evidence
scenarios remain unrun. No full autopilot run, from request to a draft PR with
captures and recorded decisions from a real application, has been observed yet.

Cursor Cloud native discovery, personal skill sync, model overrides, substitution
handling, and delegated execution remain unverified. Claude Code and Cursor
editor/CLI model adapters remain unimplemented; their native capabilities cannot
be inferred from the Codex or Cloud adapter. Model catalog checks establish
advertised support, not entitlement or observed execution settings.
