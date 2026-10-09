---
name: create-verification-skill
description: Create and prove a project-local app verification skill with a feature map and retained evidence.
license: MIT
---

# Create a verification skill

This is Luke Mode's verification creation companion, adapted from
[PStack](https://github.com/backnotprop/pstack/blob/3a604672c46cd8187d2b19980eae0a34f9f91138/skills/create-verification-skill/SKILL.md)
under the included [MIT license](LICENSE). It retains explicit-only invocation.
Use `$create-verification-skill` in Codex or `/create-verification-skill` in
Cursor Cloud. `$luke-mode create-verification-skill` also explicitly names this
workflow. Ordinary engineering work does not create skills merely because a
verification recipe is missing.

Generate a repository-local `verify-<app>` skill that drives the real app,
captures evidence, and tells a future agent how to repeat the proof. Install
this companion beside `luke-mode`. Read applicable project guidance,
[harness selection](../luke-mode/references/harnesses.md), and the matching
adapter before choosing the output location or controls. Resolve shared
references through the active catalog's Luke installation if sibling links are
unavailable. Keep the working directory in the user's project.

## Discover the app and target

Establish these facts from source, scripts, and project docs; ask only for
choices or access the repository cannot establish:

- **Surface:** the app and user-facing UI, CLI, service, desktop, mobile, or
  library interface to cover. For a monorepo, use the requested app's scope.
- **Launch:** the documented local command, readiness signal, configuration,
  authentication, and fixtures needed for a usable instance.
- **Drive:** existing browser, PTY, HTTP, simulator, or other control harnesses
  available in this runtime. Prefer the project's working controls.
- **Observe:** observable state and artifacts that can prove a user action,
  including relevant persistence or other side effects.
- **Isolation:** instance ownership, ports, data directories, and whether
  concurrent runs can safely use separate instances.

Use an existing harness-compatible project skill root when established;
otherwise use `.agents/skills/` for Codex or `.cursor/skills/` for Cursor Cloud,
scoped to the owning app when project conventions require it. Keep generated
skills in the repository rather than a personal global root. Choose a concrete
`verify-<app>` name. Inspect an existing target before writing; if it already
provides this verification workflow, report its path and offer the
[maintenance workflow](../maintain-verification-skill/SKILL.md) instead of
replacing it. Run maintenance only when explicitly named by the user. Resolve
competing targets before writes.

Check that the documented launch works. If application setup is broken or a
required control is unavailable, report the concrete gap and leave generation
as a draft. App repairs outside the requested skill require their own scope.
Disposable verification fixtures may supply missing sample data or configuration;
identify them and include their teardown.

## Write the runnable skill

Write the target's `SKILL.md` with YAML `name` matching its folder and a
description naming the app, surface, and relevant verification requests.
The generated verification skill should permit normal discovery unless the
user requests explicit-only invocation; the generator's policy is separate.
Ground all commands and controls in the actual repo and runtime. Include:

- **Launch:** exact commands and readiness checks, required fixtures, and
  instance ownership. Use one owned instance for a server or UI; use isolated
  sessions per drive for a short-lived CLI. State platform or service needs.
- **Doctor:** read-only checks for the correct build, instance, configuration,
  and usable authentication. Run before driving and after surprising failures.
- **Drive:** real user entry points and stable selectors, prompts, commands,
  routes, or handles. Link to the feature-map index for individual recipes.
- **Evidence:** the artifact directory and what each proof captures. Record the
  action and resulting state, plus relevant persisted effects. Exercise public
  user paths; use mocks only at established external boundaries. Check what a
  test or dry-run mode actually changes instead of trusting its label.
- **Cleanup:** teardown for processes and scratch state owned by this run,
  including failed attempts. Track concrete handles or PIDs; preserve existing
  sessions and keep evidence outside disposable state removed by teardown.
- **Helpers, when needed:** executable scripts with documented invocations and
  requirements. Prefer existing project helpers over a second control layer.

## Seed the feature map

Use [the feature-map example](references/feature-map-example/README.md) for
the index and recipe shape. Its fictional app and controls illustrate structure;
replace them with findings from this project.

Create `features/README.md` and a file for each initial user-facing feature,
usually the main three to five. For smaller apps, map the features that exist.
The index states common preconditions and links every feature file. The skill
links back to that index. Each recipe describes the user's behavior and uses
four H2 sections: `Sub-features`, `How to get to it (user POV)`,
`Driving it with <harness>`, and `Gotchas`. Replace the harness placeholder with
the actual control name. Pair each action with its concrete command or tool
call and observable result; include supported entry points and prerequisites.

Distinguish mapped behavior from behavior actually exercised. One successful
entry point does not prove the others or the whole feature map.

## Prove and hand over

Follow the generated instructions end to end: launch, doctor, drive at least
one mapped feature through a real user path, capture evidence, then clean up.
Inspect the action, resulting state, and relevant side effects. Confirm the
named artifacts still exist after teardown. Clean up failed iterations too;
repair recipe or harness mistakes in scope and repeat the affected proof.

Read back the generated files, metadata, links, and helper invocations. A
creation is complete only with a runnable skill, a linked feature map, and
retained proof from this run. If execution is blocked, report the files as a
draft and name the unverified step. Report the target path, feature and entry
point exercised, command outcomes, artifact paths, and remaining coverage.
Point to `$maintain-verification-skill` in Codex or
`/maintain-verification-skill` in Cursor for later upkeep. Commits, PRs, and
scheduled maintenance follow the user's requested delivery.
