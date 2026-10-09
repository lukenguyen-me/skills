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

## Remaining coverage

The P0 instruction update adds proportional blast-radius assessment across
change-making routes, project verification skill invocation and discovery, and
acceptance evidence beyond build or unit-test success. Package checks were
repeated after the update. The six new [blast-radius and evidence scenarios](../scenarios/routing.md#blast-radius-and-evidence)
remain unrun; the earlier behavioral results do not validate these changes in
a live session.

Native Codex skill discovery was not verified: the sandbox blocked the optional
app-server check, which was skipped. No global installation or live inference
with the saved role mappings was performed. The model checks establish
advertised support, not account entitlement or observed execution settings.

The remaining [routing scenarios](../scenarios/routing.md) are manual acceptance
cases. Claude Code and Cursor adapters remain unimplemented and unvalidated.
