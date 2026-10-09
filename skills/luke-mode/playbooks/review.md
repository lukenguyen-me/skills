# Review

Deliver findings about specified code or changes. Leave application files,
branches, and tracker state unchanged. The user may separately authorize fixes.

1. Pin the scope and baseline. Distinguish a committed branch diff from staged
   or unstaged changes. Read the originating requirements and project standards
   where available; say which comparison lacks a source.
2. Compose `code-review` if its installed requirements match. Its current
   committed-diff workflow may not cover uncommitted work. Do not commit work
   merely to make that skill usable.
3. Use Reviewer in a fresh context when independent review earns the cost or
   the user requests it. If `code-review` owns two reviewer agents, assign those
   seats the Reviewer mapping and let it own the review; add no redundant panel.
   Otherwise review directly and label the result accordingly. An explicit
   role/model or independence requirement follows the model policy even when
   direct review would be cheaper.
4. Inspect the actual code and evidence. Reproduce a finding with safe existing
   checks when possible; serialize checks and respect the read-only scope.
   Apply the composed skill's findings format. For direct review, prioritize
   actionable findings with locations, consequences, and supporting evidence.

Done when findings have been assessed against the requested scope. State review
coverage and gaps; an empty findings list is not proof of full correctness.
Report missing spec or verification evidence without inventing either.
