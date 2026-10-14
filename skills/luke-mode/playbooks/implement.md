# Implement

Deliver the specified behavior with evidence. Follow the sequence of Matt's
`implement`: scope, TDD, checks, code review, delivery. His user-only workflow is
inspiration; installed primitives own their detailed procedures.

First resolve the supplied ticket or spec and its authoritative implementation
children. A parent spec with buildable children automatically selects the
[whole-spec mode](../references/implement-spec.md), owned by Luke. An individual
ticket stays in the steps below even when it links to a parent and siblings.
A settled spec without implementation children also uses these ordinary steps;
decomposition, when needed, is a Design decision or an explicit `to-tickets`
handoff. Keep read-only and plan-only scope intact.

An explicitly named `implement-spec` selects Matt's installed workflow through
the same contract. That is a separate owner choice; ordinary parent detection
does not bypass Matt's explicit-invocation policy. Both whole-spec paths apply
Luke's role, scoped concurrency, verification, and delivery rules. Do not wrap
these single-ticket steps around every ticket in a whole-spec run.

1. Read the supplied spec, ticket, or contract and the affected code. Resolve
   ambiguous references before starting. Assess blast radius before edits;
   establish acceptance criteria and a review baseline that includes the
   requested working-tree changes.
2. Settle product or architecture forks through Design only when needed.
   Preserve prior agreement on test interfaces. If `tdd` requires approval of a
   new seam, obtain it before writing those tests.
3. Compose `tdd` wherever meaningful behavioral tests are appropriate. Build
   one verifiable slice at a time. Coding owns implementation, its tests, and
   the focused test runs inside its loop. Keep the owner and tests sequential.
4. Run focused tests and applicable type checks as work develops. At the end,
   Verifier runs the project's required checks and verification selected from the blast
   radius. Run the full relevant suite once for substantive changes; a trivial
   isolated edit needs only focused evidence unless risk or project requirements
   warrant more. Verification on a simulator or emulator uses a
   [shared device](../references/evidence.md#shared-devices).
5. Compose `code-review` after implementation and verification when its scope,
   prerequisites, and fan-out fit. Otherwise have Reviewer check the actual diff
   against the requirements and project standards, and disclose that fallback.
   Resolve material in-scope findings, then recheck affected behavior.

Done when the requested behavior is observed, required checks have results,
and review is complete with explicit gaps. Deliver local changes by default;
commit or publish only within existing authorization.
