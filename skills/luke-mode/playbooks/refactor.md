# Refactor

Deliver simpler structure with preserved observable behavior. Follow Matt's
codebase-design practices and implementation sequence for checks and review.

1. Name the behavior to preserve and establish a pin: existing behavioral tests,
   characterization at an agreed public interface, or a comparable replay.
   Obtain any new test-interface agreement the composed `tdd` skill requires.
2. Read relevant contracts, callers, and project decisions. Compose
   `codebase-design` when module shape or interfaces need design. Resolve a
   consequential architecture choice with the human before restructuring.
3. Move in small steps, checking the pin between them. Coding owns the refactor;
   Worker may handle a bounded mechanical step after the owner has finished its
   preceding step. Search callers and non-code references after renames.
4. Run relevant project verification and required checks. Compose compatible
   `code-review` or label a direct review of the final diff. Resolve in-scope
   findings and recheck changed areas.

Done when the resulting structure is easier to follow and the preserved behavior
has evidence. If the desired outcome changes behavior, re-route to Implement or
Fix; do not hide that change under a refactor label.
