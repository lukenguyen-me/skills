# explain

A self-contained copy of the `teach` skill from `patinaproject/skills`
(`plugins/code/skills/teach`, ref `260f6ac02fc3735ce44ec5ab4895c3e87f2b28d2`),
renamed to `explain`. That plugin derives from pstack.

The skills that `teach` depends on are bundled as reference folders:

- `how/HOW.md` and `how/references/`: the `how` skill.
- `why/WHY.md` and `why/references/`: the `why` skill.
- `unslop/UNSLOP.md`: the `unslop` writing rules.
- `ste/STE.md`: the Simplified Technical English (ASD-STE100) writing rules.
  This is a local copy of the rules, so the skill does not depend on
  `write-to-human`.

Changes from the source: the links point to the bundled files, and the
pstack-only parts are removed (Codex and Copilot platform mappings, the
`pstack-models.md` override sheet, and the reasoning-effort agent types).
Explanations are written in STE, with `unslop` as a second pass for AI
patterns, and every reply puts the bottom line up front (BLUF).
The skill names no model, agent type, or harness-specific tool. Subagent
steps fall back to sequential work in a harness without subagents.

Install: copy this folder into the skills directory your harness reads.
