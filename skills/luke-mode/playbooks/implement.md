# Implement

Deliver the specified behavior with evidence. Follow the sequence of Matt's
`implement`: scope, TDD, checks, code review, delivery. His user-only workflow is
inspiration; installed primitives own their detailed procedures.

1. Read the supplied spec, ticket, or contract and the affected code. Resolve
   ambiguous references before starting. Assess blast radius before edits;
   establish acceptance criteria and a review baseline that includes the
   requested working-tree changes.
2. Settle product or architecture forks through Design only when needed.
   Preserve prior agreement on test interfaces. If `tdd` requires approval of a
   new seam, obtain it before writing those tests.
3. Compose `tdd` wherever meaningful behavioral tests are appropriate. Build
   one verifiable slice at a time. Coding owns substantial implementation;
   Worker can own bounded mechanical work or test execution when delegation
   earns its cost. Keep the owner and tests sequential.
4. Run focused tests and applicable type checks as work develops. At the end,
   run the project's required checks and verification selected from the blast
   radius. Run the full relevant suite once for substantive changes; a trivial
   isolated edit needs only focused evidence unless risk or project requirements
   warrant more.
5. Compose `code-review` after implementation and verification when its scope,
   prerequisites, and fan-out fit. Otherwise review the actual diff directly
   against the requirements and project standards, and disclose that fallback.
   Resolve material in-scope findings, then recheck affected behavior.

Done when the requested behavior is observed, required checks have results,
and review is complete with explicit gaps. Deliver local changes by default;
commit or publish only within existing authorization.
