# Research and design choices

Research date: 2026-10-09. PStack snapshot:
`3a604672c46cd8187d2b19980eae0a34f9f91138`. Matt Pocock snapshot:
`b0618bc436ad893b3c5e84e55fba86586d34a404`. The inspected local Codex CLI was
`0.162.0`; runtime capabilities remain authoritative on another installation.

## PStack

The useful patterns are intent-based playbook selection, separate playbook files,
bounded delegation, context pointers, and verification of real behavior. PStack's
implementation and design defaults often require delegation and multiple-model
exploration. Luke uses direct execution for bounded tasks and delegates when
isolation, expertise, or independent review improves the outcome. It also stops
unsupported exact model requests instead of using
the mirror's closest-equivalent model rule.
[Poteto Mode](https://github.com/backnotprop/pstack/blob/3a604672c46cd8187d2b19980eae0a34f9f91138/skills/poteto-mode/SKILL.md),
[model setup](https://github.com/backnotprop/pstack/blob/3a604672c46cd8187d2b19980eae0a34f9f91138/skills/setup-pstack/SKILL.md)

`automate-me` sequences existing capabilities and references their instructions.
It cautions against copying another person's mode or capturing generic rules.
Luke starts from the user's agreed preferences; transcript mining, automatic
skill repair, and automatic PR creation are outside V1.
[Automate Me](https://github.com/backnotprop/pstack/blob/3a604672c46cd8187d2b19980eae0a34f9f91138/skills/automate-me/SKILL.md)

Project-specific verification recipes should take priority over invented generic
checks. Creating such a skill is a separate task when none exists.
[Verification-skill pattern](https://github.com/backnotprop/pstack/blob/3a604672c46cd8187d2b19980eae0a34f9f91138/skills/create-verification-skill/SKILL.md)

## Matt Pocock

Matt separates user-only orchestration workflows from model-reachable primitives.
Luke respects this boundary while borrowing workflow sequencing. Implement uses
the scope → TDD → checks → review sequence, with local delivery as agreed by the
user rather than Matt's automatic final commit.
[Organization](https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/README.md#reference),
[invocation rules](https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/productivity/writing-for-agents/SKILL-MECHANICS.md),
[Implement](https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/engineering/implement/SKILL.md)

Installed versions can differ from upstream. The inspected local installation
included TDD, but lacked `grilling`, `diagnosing-bugs`, and `code-review`; `grill-me`
and `implement` referenced absent dependencies. Discovery must validate actual
installed files and prerequisites instead of treating installation as usability.

Matt's Code Review uses two independent axes and a committed diff against a fixed
point. Luke composes it when compatible; uncommitted work, absent tracker setup,
or unavailable delegation capabilities can require a disclosed direct review.
[Code Review](https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/engineering/code-review/SKILL.md)

## Codex and portability

Codex supports progressive disclosure, explicit `$skill` invocation, user-level
`.agents/skills`, symlinked folders, and `allow_implicit_invocation: false` in
`agents/openai.yaml`. Standalone Markdown packaging is enough for personal V1.
[Build skills](https://developers.openai.com/codex/skills)

Native subagents support model/reasoning configuration, but actual tool schemas,
configured defaults, custom agents, and permissions determine what a session can
apply. A full-history fork may require inheritance. Luke has no dependency on
Cursor cloud delegation or PStack custom agents.
[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)

Model catalogs describe advertised capabilities; they are not a universal access
guarantee. Parent model selection uses launch settings or the model picker.
[Model discovery](https://learn.chatgpt.com/docs/app-server#list-models-modellist),
[parent model selection](https://learn.chatgpt.com/docs/models)

The shared core keeps models abstract and harness mechanics in adapters. Claude
Code needs its own invocation controls; blindly using Codex metadata would not
preserve explicit-only behavior. Claude and Cursor support are future work.
[Claude skill controls](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill)

## Agreed V1

Six routes: Explore, Design, Implement, Fix, Refactor, Review. Performance work
and bounded prototypes fit those routes initially. Work adapts to uncertainty
and impact, with beneficial delegation and sequential modifications/tests.
Setup configures four portable model roles: Reasoning, Coding, Worker, and
Reviewer, using exact models per harness. The human keeps product and
consequential architecture decisions. Verification and local delivery are the
default completion boundary.
