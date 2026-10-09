# Explore

Deliver an evidence-backed explanation, diagnosis, or recommendation. Application
files and repository state stay unchanged; write a report only when requested.

1. Pin the question and the evidence that would answer it. Trace relevant entry
   points, callers, tests, and history; use primary documentation for external
   facts. Read the project's existing glossary or ADRs when relevant.
2. Use Worker for an independent reading task only when its scope warrants
   delegation. A complex causal investigation can use Reasoning. Compose
   `research` only if its background-agent and report-writing requirements fit
   the request and available capabilities. Otherwise investigate directly.
3. Distinguish observed behavior, inference, and unknowns. Safe existing checks
   can establish behavior; a command's side effects must fit the read-only
   request. Finding a defect does not authorize its fix.

Done when the answer points to inspected files, symbols, commands, or sources
that support its claims. Report an access or evidence gap when it prevents an
answer. Offer a further route only when the next outcome warrants one.
