# Research and design choices

Research date: 2026-10-09. PStack snapshot:
`3a604672c46cd8187d2b19980eae0a34f9f91138`. Matt Pocock snapshot:
`b0618bc436ad893b3c5e84e55fba86586d34a404`. The inspected local Codex CLI was
`0.162.0`; runtime capabilities remain authoritative on another installation.
The later `implement-spec` integration was checked against Matt's snapshot
`49dd158d1076134a641b33efb035946536778336` on the same date.

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

Project-specific verification recipes take priority over invented generic
checks. Luke setup installs `create-verification-skill` and
`maintain-verification-skill` externally from PStack, preserving upstream
instructions and resources rather than maintaining adapted copies. Creation
remains explicitly requested when no project recipe exists. The installed
workflows own their prerequisites, evidence requirements, and delivery rules.
[Creation](https://github.com/backnotprop/pstack/blob/main/skills/create-verification-skill/SKILL.md),
[maintenance](https://github.com/backnotprop/pstack/blob/main/skills/maintain-verification-skill/SKILL.md)

## Matt Pocock

Matt separates user-only orchestration workflows from model-reachable primitives.
Luke respects this boundary while borrowing workflow sequencing. Implement uses
the scope → TDD → checks → review sequence, with local delivery as agreed by the
user rather than Matt's automatic final commit.
[Organization](https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/README.md#reference),
[invocation rules](https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/productivity/writing-for-agents/SKILL-MECHANICS.md),
[Implement](https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/engineering/implement/SKILL.md)

Matt's new `implement-spec` is a user-only workflow over a ticket dependency
graph, with concurrent worktree implementers, one integration branch, TDD,
merger delegation, and final code review. Luke adapts that sequencing as a mode
inside Implement: resolving a parent spec with implementation children selects
Luke-owned graph execution automatically, using permitted primitives. A child
ticket stays scoped to itself. This mode does not require or implicitly invoke
Matt's user-only workflow. Explicitly naming `implement-spec` instead selects
the installed Matt workflow under the shared contract; no Matt files are copied
into Luke.
[Workflow](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/implement-spec/SKILL.md),
[Codex policy](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/skills/engineering/implement-spec/agents/openai.yaml)

The contract permits concurrent writing only in isolated owned worktrees and
runtime resources, with a single integration writer. It computes the frontier
from verified integrations, avoiding stale GitHub blocker counts. Candidates
must refresh and re-prove if the integration tip advances; required skipped
tests remain gaps. The integrated app is verified before one full-spec review,
and corrections receive focused rechecks rather than an automatic broad review
loop. Resume restores the original baseline. User changes and dirty worktrees
are preserved; external delivery follows existing authorization. These Luke
constraints address the upstream usage notes' shared-resource, stale-blocker,
skipped-fixture, and review-loop cases. Luke-owned graph execution can proceed
sequentially when concurrency is unavailable and the user's model and review
requirements permit it. The explicit Matt path retains its installed procedure
and required capabilities; each path has one workflow owner.
[Usage notes](https://github.com/mattpocock/skills/blob/49dd158d1076134a641b33efb035946536778336/docs/engineering/implement-spec.md)

Installed versions can differ from upstream. The inspected local installation
included TDD, but lacked `grilling`, `diagnosing-bugs`, and `code-review`; `grill-me`
and `implement` referenced absent dependencies. Discovery must validate actual
installed files and prerequisites instead of treating installation as usability.

Matt's Code Review uses two independent axes and a committed diff against a fixed
point. Luke composes it when compatible; uncommitted work, absent tracker setup,
or unavailable delegation capabilities can require a disclosed direct review.
[Code Review](https://github.com/mattpocock/skills/blob/b0618bc436ad893b3c5e84e55fba86586d34a404/skills/engineering/code-review/SKILL.md)

`setup-matt-pocock-skills` configures repository tracker guidance, domain docs,
and triage labels when applicable. It is user-only in both its frontmatter and
Codex policy. Luke's full setup checks repository readiness and hands off for
explicit invocation when needed; model-only setup stays portable. The installed
Matt workflow owns its drafts, confirmations, and writes.
[Setup](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md),
[Codex policy](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/agents/openai.yaml)

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
preserve explicit-only behavior. Claude Code support remains future work.
[Claude skill controls](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill)

## Cursor Cloud

Cursor's skill format supports explicit slash-command invocation using
`disable-model-invocation: true`. The Cursor package is generated from the shared
source with that frontmatter field, retaining Codex metadata and all linked
resources. Cloud delivery uses actual project files or personal skill sync from
`~/.cursor/skills/`; `.agents` user skills and arbitrary personal config do not
sync. The optional repository models file carries separately keyed harness
profiles into a clone.
[Skills and sync](https://cursor.com/docs/skills)

Native subagents are supported in Cloud and use independent context. Runtime
schemas decide launch controls. Cursor documents exact model selection and
native model-parameter syntax, but restrictions can trigger model substitution.
Luke records base IDs and effort separately, checks execution evidence, and keeps
an exact-model requirement unresolved when it cannot establish the chosen model.
[Subagents](https://cursor.com/docs/subagents),
[Cloud catalog](https://cursor.com/docs/cloud-agent/api/endpoints#list-models)

The managed VM's preview metadata API and optional Cloud MCP can expose current
runtime and serving-model evidence. Those values do not enumerate models or
verify a subagent. Cloud model configuration is separate from application
environment setup and the harness's authorized branch/PR delivery.
[Metadata](https://cursor.com/docs/cloud-agent/metadata),
[Cloud capabilities](https://cursor.com/docs/cloud-agent/capabilities),
[Environment setup](https://cursor.com/docs/cloud-agent/setup)

## Agreed V1

Six routes: Explore, Design, Implement, Fix, Refactor, Review. Performance work
and bounded prototypes fit those routes initially. Work adapts to uncertainty
and impact, with beneficial delegation and sequential modifications/tests.
Implement selects whole-spec mode for parent specs with implementation children;
an explicit `implement-spec` command selects Matt's original workflow. Whole-spec
execution permits concurrency only across independently owned worktrees and
resources, under one integration writer and native capacity.
Setup configures four portable model roles: Reasoning, Coding, Worker, and
Reviewer, using exact models per harness. Full setup installs missing Matt and
PStack dependencies and runs Matt's per-repository setup. Setup and Matt sync
ship inside Luke; verification creation and maintenance remain external.
The human keeps product and consequential architecture decisions. Verification
and the authorized workspace delivery are the default completion boundary.
