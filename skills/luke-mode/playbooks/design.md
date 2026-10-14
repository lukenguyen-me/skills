# Design

Deliver an agreed scope or a proposal ready for a human decision. Take sequencing
cues from Matt's `grill-with-docs` and `to-spec`; invoke neither automatically.

1. Establish the problem, actors, desired behavior, constraints, and non-goals
   from the request and project. Read existing domain vocabulary and decisions.
2. Compose `grilling` for a substantial requirements interview, `domain-modeling`
   for an actual domain-language problem, and `codebase-design` for module shape
   or interface choices, when their installed requirements fit. Reasoning
   analyzes trade-offs and options; the parent runs the interview with the human.
3. Research observable facts before asking the human. Present viable choices
   and a recommendation for unresolved product or architecture decisions. A
   requested prototype answers one named empirical question in an isolated
   location; it does not become production implementation by default.
4. Capture acceptance criteria, agreed public test interfaces, risks, and a
   useful sequence of verifiable slices. A large plan may be better served by
   explicitly invoking `to-spec` or `to-tickets`; recommend that handoff instead
   of publishing tickets or rebuilding those workflows here.

Done when decisions are recorded and scope is buildable, or when the proposal
clearly names the remaining human decisions. Save a design artifact when
requested. A design-only request ends here. For authorized design-and-build
work, route to Implement after the required decisions are settled.
