# explain

A self-contained copy of the `teach` skill from `patinaproject/skills`
(`plugins/code/skills/teach`, ref `260f6ac02fc3735ce44ec5ab4895c3e87f2b28d2`),
renamed to `explain`. That plugin derives from pstack.

The skills that `teach` depends on are bundled as reference folders:

- `how/HOW.md` and `how/references/`: the `how` skill.
- `why/WHY.md` and `why/references/`: the `why` skill.
- `unslop/UNSLOP.md`: the `unslop` writing rules.

Changes from the source: the links point to the bundled files, and the
pstack-only parts are removed (Codex and Copilot platform mappings, the
`pstack-models.md` override sheet, and the reasoning-effort agent types).
The skill names no model, agent type, or harness-specific tool. Subagent
steps fall back to sequential work in a harness without subagents.

Install: copy this folder into the skills directory your harness reads.
