# Explain

Help the person understand how specified code, a change, or a subsystem works
and why it has that shape. Application files and repository state stay
unchanged. The deliverable is their understanding, not a diagnosis, a fix, or a
report file.

1. Resolve the installed `explain` skill through [composition](../references/composition.md)
   and read its `SKILL.md` and bundled `how`, `why`, `ste`, and `unslop` files.
   `explain` owns the procedure, the BLUF reply shape, and the STE writing rules;
   follow them rather than restating them. `explain` is a Luke
   [dependency](../references/dependencies.md) that setup installs. If it is
   missing, disabled, or incompatible, report it as a pending dependency, point
   to `$luke-mode setup` (`/luke-mode setup` in Cursor Cloud and Claude Code),
   and answer through [Explore](explore.md) instead. Ordinary work does not
   install it.
2. Pin the subject and why the person is asking: about to change it, reviewing
   it, debugging it, or new to it. Read from the conversation; do not quiz them.
   A request to find a cause, measure behavior, or recommend a change is Explore,
   even when worded as "explain".
3. Map each subagent step in `how` and `why` to a role. With a configured
   profile, the parent runs the `explain` procedure as orchestrator and spawns
   every step itself; no delegate starts another agent.

   | `explain` step | Role |
   | --- | --- |
   | `how` explorer, one per angle | Explorer |
   | `how` explainer, direct or after explorers | Reasoning |
   | `why` source-control investigator (git and `gh`) | Explorer |
   | `why` investigator for an MCP category | A role whose native definition can reach that MCP |
   | `why` synthesizer | Reasoning |

   Brief each delegate with the step's bundled prompt template, the code anchor,
   and the person's question. Keep `why` narrow by default: source control plus
   any source the question names. When no role can reach an MCP category, record
   it as a gap in Sources Consulted, as `why` requires; the parent does not run
   it directly. Without a profile, follow `explain` in the current session and
   report it as direct execution.
4. Blend the results through `explain`. Lead with the bottom line, keep `why`'s
   confidence language intact, and build up diagrams one part at a time. Safe
   existing checks can show behavior when that lands the point faster; their
   side effects must fit the read-only request.

Done when the reply opens with a bottom line that answers the person's
question, every claim points to inspected files, symbols, commits, or sources,
and `why`'s inferred and unknown findings stay labeled as such. Put Luke's
delivery notes (direct or delegated execution, skipped `why` categories, other
gaps) after the explanation, not before it. Offer `how` or `why` threads, or
another route, only when the person's next step warrants one.
