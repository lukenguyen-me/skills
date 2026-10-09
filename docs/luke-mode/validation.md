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

## Package checks

The Codex `skill-creator` validator passed for the main skill and all four companions:

```sh
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/luke-mode
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/setup-luke-mode
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sync-matt-pocock-skills
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/create-verification-skill
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/maintain-verification-skill
```

Relative Markdown file links resolve. YAML metadata specifies
`allow_implicit_invocation: false` for the main skill and verification companions,
and `true` for setup and sync.
Files contain no trailing whitespace or
unfinished endings. The package contains Markdown, Codex metadata, and the
upstream MIT notices.

## Cursor Cloud implementation

The Cloud adapter and harness selection are implemented. `scripts/package-luke-mode-cursor.py`
prepares the main skill and all four companions as sibling folders, preserving
the sources and Codex metadata. The main skill and verification companions get
Cursor's native explicit-only field; setup and sync retain normal discovery.
An optional repository models file
supports Cloud portability with a separate `Cursor Cloud` profile.

All eleven local packaging checks passed in disposable directories:

```sh
python3 -B -m unittest discover -s tests -v
```

These checks cover all five skills' completeness, cross-skill file links, native
invocation metadata, unchanged sources/resources, a target path with spaces,
invocation from another working directory, existing files/directories/symlinks
in any bundle slot, preservation of the target when a sub-skill already exists,
and rejection of a destination inside any source skill. Live Cursor behavior needs the
[Cloud scenarios](scenarios/routing.md#cursor-cloud-compatibility).

The source skill still passes the Codex validator. Relative file links and
anchors resolve in both the source and generated package. YAML parsing confirmed
Cursor's explicit-invocation flag and preserved Codex policy. The independent
Codex profile evaluation above checks the revised selection rules; it does not
exercise Cursor's runtime.

## Remaining coverage

The P0 instruction update adds proportional blast-radius assessment across
change-making routes, project verification skill invocation and discovery, and
acceptance evidence beyond build or unit-test success. Package checks were
repeated after the update. The six new [blast-radius and evidence scenarios](scenarios/routing.md#blast-radius-and-evidence)
remain unrun; the earlier behavioral results do not validate these changes in
a live session.

Full setup now also checks Matt's per-repository configuration and observes
`setup-matt-pocock-skills`'s explicit invocation policy. Model-only setup remains
available. Package checks were repeated after this update; the new
[setup scenarios](scenarios/routing.md#setup-and-portability) remain unrun.
Earlier model-profile validation covers only the personal model stage.

Setup now lives in `setup-luke-mode`; `sync-matt-pocock-skills` adds a separate
workflow for refreshing the complete upstream toolkit. Luke routes the legacy
setup commands and explicit sync requests to these sub-skills. The three source
skills pass static validation, and the eleven bundle checks pass. The new direct
sub-skill and [sync scenarios](scenarios/routing.md#matt-toolkit-sync) remain unrun;
no Matt plugin, global skill root, or live Cloud environment was changed during
these package checks.

PStack-derived verification creation and maintenance now live beside Luke's
setup and sync companions. All five source skills pass static validation, and
the eleven bundle checks pass with the expanded inventory. The checks include
the original feature-map examples and license files, explicit-only metadata in
both harness formats, and collision preservation for every companion slot.
The new [verification authoring scenarios](scenarios/routing.md#verification-creation-and-maintenance)
remain unrun: no generated app verifier or live maintenance pass was exercised
by the package suite. Packaging results do not establish live native discovery
or behavioral correctness of those workflows.

Whole-spec execution now belongs to Implement, with automatic parent detection
and an optional explicit Matt owner. The shared reference is included by the
existing bundle checks; all five skill validators, relative links and anchors,
and eleven packaging checks pass. The preflight results above cover mode and
owner selection. The remaining [whole-spec scenarios](scenarios/routing.md#whole-spec-execution)
are unrun: no live ticket coding, parallel worktree dispatch, stale-candidate
refresh, integration failure recovery, resumed execution, full-spec review,
cleanup, PR, or tracker delivery was exercised. The Cloud whole-spec route was
not run in a live Cloud environment.

Native Codex skill discovery was not verified: the sandbox blocked the optional
app-server check, which was skipped. No global installation or live inference
with the saved role mappings was performed. The model checks establish
advertised support, not account entitlement or observed execution settings.

The remaining [routing scenarios](scenarios/routing.md) are manual acceptance
cases. Cursor Cloud native discovery, skill sync, model overrides, substitution
handling, and delegated execution have not been run in Cursor. The local package
checks do not establish account access or native execution. Claude Code and
Cursor editor/CLI adapters remain unimplemented.
