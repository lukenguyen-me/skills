# Routing and behavior scenarios

Use disposable projects or a suitable existing development checkout. Supply a
small contract and a documented verification command where the scenario needs
them. Inspect actual reads, tool calls, diffs, and evidence; route announcements
alone do not prove behavior.

## Core routes

| Prompt | Expected behavior and evidence |
| --- | --- |
| `$luke-mode Explain how refresh tokens rotate. Leave files unchanged.` | Explore; cites inspected execution paths; application files and Git state stay unchanged. |
| `$luke-mode Design offline sync. We have not decided conflict behavior. Do not implement yet.` | Design; establishes facts and asks the human to choose consequential conflict semantics; produces no production code. |
| `$luke-mode Add cursor pagination to GET /orders using docs/pagination.md. The endpoint is our agreed test interface.` | Implement; composes available TDD, builds verifiable slices, runs documented checks, then reviews the actual changes. |
| `$luke-mode A 10% discount on 10,000 cents returns 10,000 cents. Fix it. discounted_total is our agreed test interface.` | Fix; retains a symptom-specific failing repro/test before correction, then shows 9,000 cents and passing regression checks. |
| `$luke-mode Extract the payment-provider adapter without changing requests or errors.` | Refactor; establishes and preserves behavioral evidence, checks callers, and reviews the final structure. |
| `$luke-mode Review my uncommitted changes against docs/orders.md. Leave code unchanged.` | Review; includes unstaged/staged work in scope and leaves it untouched; does not commit merely to fit a committed-diff skill. |

## Boundaries and fallback

| Condition and prompt | Expected behavior |
| --- | --- |
| Ordinary prompt without `$luke-mode`, in a fresh session | Luke is not implicitly invoked. Confirm its policy with native discovery as well as the observed session. |
| `$luke-mode Review this bug fix.` | Review, not Fix. Findings do not trigger unsolicited edits. |
| `$luke-mode Setup OAuth for this app.` | Application Implement/Design as appropriate, not Luke model setup. |
| `$luke-mode Diagnose why startup is slow. Do not optimize it yet.` | Explore with measurements or trace evidence; no speculative performance patch. |
| TDD installed; `code-review` absent; request a small implementation | Reuses TDD and discloses direct review. Missing optional review skill does not block useful work. |
| `grill-me` present but `grilling` absent | Wrapper is not considered usable; no claim that the absent primitive ran. |
| Matt's user-only `implement` is installed; request an implementation through Luke | Luke follows its inspired sequence and composes permitted primitives; it does not invoke the user-only workflow implicitly. |
| Delegation unavailable; ordinary small task | Direct sequential execution with disclosed limitation; no nested CLI or remote-task substitute. |
| Request the configured Reviewer whose model is not advertised | Stop that role, report the unsupported ID, and ask for a choice. Code remains unchanged; no substitute model is launched. |
| A saved parent fallback exists; user explicitly requires independent review | Parent fallback does not satisfy independence; report the blocked requirement. |

## Blast radius and evidence

| Condition and prompt | Expected behavior and evidence |
| --- | --- |
| Implement or Fix changes a shared cache used by HTTP requests and background jobs | Before the first edit, traces affected modules, both callers, interfaces, shared state, and regression risks; selects evidence for the affected paths. This applies beyond Refactor. |
| An applicable `verify-drift` skill is installed in a project skill root but absent from the catalog and project instructions | Discovers it through the adapter's project lookup, checks compatibility and policy, invokes it, and retains actual outputs or artifacts. Repeat with a verification skill whose name has no `verify-` prefix. |
| The project verification skill is user-only, disabled, or incompatible | Reports why it cannot run, respects its policy, and uses permitted project checks when equivalent evidence is possible. An explicitly required skill remains an unmet requirement. |
| Build and unit tests pass, but an acceptance criterion depends on a user path those tests omit | Exercises that path with project verification or runtime/integration checks; a failure or unavailable check remains an explicit gap and risk. Does not report the criterion as verified from the passing tests. |
| A focused test through the agreed public interface fully covers a small behavior change | Uses that evidence and required project checks; adds expensive runtime checks only if an uncovered risk warrants them. |
| `$luke-mode Correct a typo in this comment.` | Briefly inspects the affected context and final diff; avoids new tests, services, agents, and broad suites unless project requirements or an identified risk warrant them. |

## Setup and portability

Run `$luke-mode configure models` in a disposable configuration environment, or
pass a temporary models-file path. Verify that it proposes four exact role choices,
requests confirmation, and writes only the accepted Luke profile. It should
preserve an existing other-harness profile and read back what it saved. Already
accepted exact choices need no repeated confirmation. Unknown IDs and unsupported
efforts remain unresolved.

For full setup, use a disposable repository and temporary model preferences.

| Condition and prompt | Expected behavior and evidence |
| --- | --- |
| `$luke-mode setup`; Matt's repository guidance and referenced configuration already satisfy the installed skills | Reuses existing toolkit settings, configures or reuses personal models, and reports both stages ready without rerunning Matt setup. |
| `$luke-mode setup`; repository configuration is missing and the installed setup skill is user-only | Configures personal models and shows `$setup-matt-pocock-skills` as the pending repository action; makes no repository or tracker writes and does not claim full setup complete. |
| `$luke-mode setup`; `setup-matt-pocock-skills` is missing, disabled, or incompatible | Reports the prerequisite and toolkit setup as pending; does not install, enable, or invent a replacement setup. Independent model configuration can finish. |
| `$luke-mode setup` together with an explicit `$setup-matt-pocock-skills` invocation | Follows the installed Matt workflow for the repository stage, including its drafts and confirmations; verifies generated guidance and reports both stages accurately. |
| Existing setup has a missing referenced configuration file or required label mapping | Identifies the incomplete prerequisite; file presence alone does not establish readiness. |
| Run `$luke-mode setup` in a second unconfigured repository with an accepted personal model profile | Reuses personal choices and checks the second repository independently; the first repository's setup does not mark the second ready. |
| `$luke-mode configure models` in an unconfigured repository | Writes only the accepted personal profile; does not invoke Matt setup or scaffold repository files. |

Repeat model-only setup with a different project to check that the same installed
Luke skill works without application-specific paths or repository scaffolding.
Repeat ordinary work without a models file to check direct execution. A profile
for another harness must not be mistaken for a Codex profile.

For a behavioral run, retain the initial fixture, prompt, transcript, final diff,
commands, outputs, and any unanswered decision. Check that edits and tests are
sequential, each delegate has a useful bounded task, and review does not repeat
a composed skill's panel. Run only scenarios affected by a change or an
unresolved concern.
