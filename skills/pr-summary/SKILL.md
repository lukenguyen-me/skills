---
name: pr-summary
description: >
  Add a concise Before/After/Solution block at the top of every new or
  refreshed pull request description. Use when opening a PR, writing or
  updating a PR title/body, refreshing an existing PR after material
  changes, or when the user asks for a PR summary. Use alongside pr-writer
  when that skill is available.
---

# PR Summary

For every new or refreshed PR, use `pr-writer` for the title and standard
description when it is available, then place this block at the very top of
the PR body:

```markdown
## Summary

- **Before:** <the problem, missing capability, or limitation before this PR>
- **After:** <the behavior or state reviewers should expect after this PR>
- **Solution:** <the main implementation approach taken by this PR>
```

Derive all three statements from the verified issue or specification and the
current base-to-head diff. Keep each statement to one concise sentence when
possible. For a refactor with no intended behavior change, say so explicitly
in **After** and describe the structural improvement in **Solution**.

Keep the remaining reviewer context produced under `pr-writer` below this
block, including useful tradeoffs, risks, verification, review focus, and
verified issue references. The summary is an entry point, not a replacement
for detail that helps review the change. Remove repetition between the summary
and the remaining body, and never invent behavior, evidence, or issue links.
