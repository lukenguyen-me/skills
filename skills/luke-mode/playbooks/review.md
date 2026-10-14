# Review

Deliver findings about specified code or changes. Leave application files,
branches, and tracker state unchanged. The user may separately authorize fixes.

1. Pin the scope and baseline. Distinguish a committed branch diff from staged
   or unstaged changes. Read the originating requirements and project standards
   where available; say which comparison lacks a source.
2. Compose `code-review` if its installed requirements match. Its current
   committed-diff workflow may not cover uncommitted work. Do not commit work
   merely to make that skill usable.
3. Reviewer owns the review in a fresh context. Without a profile, review
   directly and label it direct, unless the user requires independence. If `code-review` owns two
   reviewer agents, assign those seats the Reviewer mapping and let it own the
   review; add no redundant panel. Label the result independent only when it
   ran in a separate context.
4. Inspect the actual code and evidence. Reproduce a finding with safe existing
   checks when possible; serialize checks and respect the read-only scope.
   Apply the composed skill's findings format. Without a composed format, prioritize
   actionable findings with locations, consequences, and supporting evidence.

Done when findings have been assessed against the requested scope. State review
coverage and gaps; an empty findings list is not proof of full correctness.
Report missing spec or verification evidence without inventing either.
