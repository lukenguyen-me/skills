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

## Package checks

The Codex `skill-creator` validator passed:

```sh
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/luke-mode
```

Relative Markdown file links resolve. YAML metadata specifies
`allow_implicit_invocation: false`. Files contain no trailing whitespace or
unfinished endings. The package contains Markdown and Codex metadata only.

## Cursor Cloud implementation

The Cloud adapter and harness selection are implemented. `scripts/package-cursor.py`
prepares a standalone skill with Cursor's native explicit-invocation field while
preserving the source and Codex metadata. An optional repository models file
supports Cloud portability with a separate `Cursor Cloud` profile.

All seven local packaging checks passed in disposable directories:

```sh
python3 -B -m unittest discover -s tests -v
```

These checks cover package completeness and native invocation metadata, unchanged
source/resources, a target path with spaces, invocation from another working
directory, existing files/directories/symlinks, and rejection of a destination
inside the source. Live Cursor behavior needs the
[Cloud scenarios](../scenarios/routing.md#cursor-cloud-compatibility).

The source skill still passes the Codex validator. Relative file links and
anchors resolve in both the source and generated package. YAML parsing confirmed
Cursor's explicit-invocation flag and preserved Codex policy. The independent
Codex profile evaluation above checks the revised selection rules; it does not
exercise Cursor's runtime.

## Remaining coverage

The P0 instruction update adds proportional blast-radius assessment across
change-making routes, project verification skill invocation and discovery, and
acceptance evidence beyond build or unit-test success. Package checks were
repeated after the update. The six new [blast-radius and evidence scenarios](../scenarios/routing.md#blast-radius-and-evidence)
remain unrun; the earlier behavioral results do not validate these changes in
a live session.

Full setup now also checks Matt's per-repository configuration and observes
`setup-matt-pocock-skills`'s explicit invocation policy. Model-only setup remains
available. Package checks were repeated after this update; the new
[setup scenarios](../scenarios/routing.md#setup-and-portability) remain unrun.
Earlier model-profile validation covers only the personal model stage.

Native Codex skill discovery was not verified: the sandbox blocked the optional
app-server check, which was skipped. No global installation or live inference
with the saved role mappings was performed. The model checks establish
advertised support, not account entitlement or observed execution settings.

The remaining [routing scenarios](../scenarios/routing.md) are manual acceptance
cases. Cursor Cloud native discovery, skill sync, model overrides, substitution
handling, and delegated execution have not been run in Cursor. The local package
checks do not establish account access or native execution. Claude Code and
Cursor editor/CLI adapters remain unimplemented.
