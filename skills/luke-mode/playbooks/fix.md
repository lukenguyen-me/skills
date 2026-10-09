# Fix

Deliver a correction tied to the reported symptom. Follow Matt's
`diagnosing-bugs` discipline, then the implementation workflow's review stage.

1. Establish expected versus actual behavior and run a repro that detects this
   symptom. Compose `diagnosing-bugs` when installed and compatible. Without it,
   use the project's existing tests or control surface to establish a causal
   feedback loop; this is a direct fallback, not an invocation of that skill.
2. Trace the mechanism and test the explanation against the repro. Use
   Reasoning for complex debugging only when helpful. For a performance
   regression, measure a comparable baseline before changing code.
3. At an agreed public interface, compose `tdd` for a meaningful regression
   test before the fix. If no faithful test interface exists, retain the repro
   and report that coverage gap. Make the smallest causal correction, with
   Coding or direct execution as appropriate.
4. Rerun the original scenario and relevant project verification after the fix.
   Run required checks, remove temporary instrumentation, then compose compatible
   `code-review` or perform and label a direct diff review. Recheck findings
   that lead to further changes.

Done when failing-then-passing evidence covers the original symptom and the
reviewed correction. If the symptom cannot be reproduced or observed, report
attempts and the missing evidence or access. Do not describe a speculative patch
as a verified fix. Performance claims include the baseline and measurement method.
