---
name: store-release
description: >
  Prepare App Store and Play Store release content for one public version.
  Inspect the source-verified change since the last release, write version
  notes / What's New, refresh listing copy when the release makes it
  inaccurate, and sync version configuration when those files exist. Use
  for store-release, release-store, App Store Connect text (name, subtitle,
  keywords, description, promotional text), Play Console text (title, short
  description, full description), or when the user names a version to
  prepare for the stores. Do not use for screenshots, git tags, binary
  upload, TestFlight, or publishing.
---

# Store Release

Prepare local App Store and Play Store text for one public version.
Every store claim must map to production source or user-facing resources.

## Scope

This workflow may update version configuration and in-repo store documents.
It prepares local artifacts only. Commit, tag, upload, and publish need a
separate explicit request.

## Workflow

### 1. Gate on the target version

- Read the target public version only from the invocation.
- When it is absent, ask exactly one blocking question:
  `Which public version should I prepare for release (for example, 1.6)?`
- Make no edits after asking; wait for the answer. Do not infer a version from
  configuration, the branch name, or tags.
- Remove one optional leading `v`, then require `^[0-9]+(\.[0-9]+)+$`. If
  invalid, ask one blocking question for a valid numeric dotted version and
  make no edits.

Completion: one explicit, normalized target public version is recorded.

### 2. Detect stores, locales, and artifacts

- Honor an explicit store constraint from the user.
- Otherwise enable App Store when iOS or macOS project files exist, and Play
  Store when Android project files exist. If neither platform is present, ask
  which store to prepare.
- Locales: prefer the locale set already used in store documents; otherwise
  detect from `*.lproj`, `.xcstrings`, `res/values-*/`, `lib/l10n/*.arb`,
  Compose resources, `i18n/`, `locales/`, or `translations/`. Default to the
  app's primary language when localization is unclear.
- Store documents: `docs/store/`, `fastlane/metadata/`,
  `fastlane/metadata/android/`, or another listing file the project already
  treats as canonical.
- Version files: Gradle `versionName`/`versionCode`, xcconfig
  `MARKETING_VERSION`/`CURRENT_PROJECT_VERSION`, Info.plist
  `CFBundleShortVersionString`/`CFBundleVersion`, Flutter `pubspec.yaml`
  `version`.
- Validators: project scripts such as `scripts/validate-store-metadata*`,
  identity checks, or equivalently named tasks.

Read [references/app-store.md](references/app-store.md) before writing App
Store copy. Read [references/play-store.md](references/play-store.md) before
writing Play Store copy.

Completion: each enabled store, locale, version file, store document, and
validator is known, or the workflow has stopped to ask for a missing store
constraint.

### 3. Establish the release baseline

- Inspect `git status --short` before changing files.
- If the user names a previous version, tag, branch, or commit, use it as the
  base.
- Otherwise list tags reachable from `HEAD` that match `v[0-9]*`, retain exact
  numeric dotted release tags, and use the highest version as the previous
  release tag.
- If `v<target>` already exists, stop and ask for direction. Do not create,
  fetch, push, or modify tags.
- Require the target to be greater than the previous release version when a
  previous release exists.
- If no previous release tag can be resolved: for a first `1.0` / `1.0.0`
  listing, treat the current product as the baseline; otherwise stop and ask
  for a base.
- Read current version values and, when a base tag exists, the values at that
  tag.

Completion: the base, current versions, and previous versions are known, or
the workflow has stopped without edits.

### 4. Audit the shipped delta

- Inspect the commit log and diff from the base through `HEAD`.
- Include staged and unstaged changes plus relevant untracked work reported by
  `git status` so the pending release is represented completely.
- Identify user-visible behavior in production code and resources. Verify each
  proposed store claim in those sources; commit messages alone are not proof.
- Include visible features, behavior changes, felt performance, crashes, data
  loss, sync, login, purchase, accessibility, localization, and UI.
- Exclude tests, refactors, documentation, CI, scripts, dependency bumps,
  formatting, and tooling unless they change a user outcome.

Completion: every version-note claim maps to verified user-visible behavior,
and internal-only changes are excluded.

### 5. Synchronize release versions

Skip this step when the project has no mobile version files.

- Set each public version field exactly to the target.
- Keep Android and iOS integer build identifiers equal when both exist, never
  lower either current value, and make both strictly greater than their values
  at the previous release tag.
- Reuse already-equal current build identifiers when they meet those
  constraints. Otherwise set both to
  `max(current Android, current iOS, previous Android + 1, previous iOS + 1)`.
- For a single platform, apply the same monotonicity rule to that platform
  only. For Flutter `version: x.y.z+code`, set `x.y.z` to the target and keep
  `code` monotonic the same way.
- If a required version or build value cannot be parsed safely, stop and ask
  for direction instead of guessing.

Completion: every public version equals the target, and every synchronized
build identifier satisfies monotonicity, or this step was skipped.

### 6. Prepare store content

- Update in-repo store documents when they exist. Otherwise emit paste-ready
  markdown in the same field shape as the store reference.
- Always write version notes for each enabled store and locale from the
  verified delta.
- Update App Store promotional text to highlight this release.
- Update reviewer notes when the verified delta changes how a reviewer
  exercises the app.
- If a privacy or review checklist lives with the store documents, update
  current-release version mentions and reviewer steps this delta changes.
  Leave owner-controlled checkboxes and legal claims untouched.
- Refresh evergreen listing fields (name, subtitle, description, keywords,
  short description, title) only when no listing exists, the user asked for
  listing copy, or this release makes an existing claim inaccurate.
- Write for customers in clear, current, everyday language. Translate
  implementation details into concrete behavior they can notice.
- Keep the same factual claims across locales; phrase them naturally for each
  locale rather than translating word for word.
- Keep the same factual claims across stores. Play version notes are a
  compressed equivalent that fits 500 characters, not a truncation of the App
  Store text.
- Preserve document structure, field-limit annotations, current locales, and
  owner placeholders such as `[[OWNER:...]]`.
- Do not invent owner, legal, privacy, contact, or seller facts.

Version notes:

- Lead with the user-visible result, not the implementation.
- Prefer 3 to 8 concrete points. Combine related changes. One idea per
  sentence.
- Use simple verbs: Added, Fixed, Improved, Updated, Reduced, Restored,
  Prevented.
- Omit weak evidence rather than guessing.
- Do not write generic filler, change-type labels (`Feature:`, `Fix:`,
  `Improvement:`), commit hashes, file names, branches, pull requests,
  internal modules, or architecture, framework, or database names.

Example:

```text
Add a task from the home screen in one step.

Home lists load faster when you have hundreds of events.

A crash that could happen while iCloud was syncing no longer occurs.
```

Completion: each enabled store describes the same verified release, and
owner-supplied facts remain explicit values or placeholders.

### 7. Validate the result

- Search store documents for the previous release version and other stale
  current-release references. Fix current-release mismatches; retain genuinely
  historical references.
- From this skill's `scripts/` directory, run
  `python3 check_limits.py --markdown <store-doc>` on each store document, or
  `python3 check_limits.py --store app|play --field "<field>" --text "<value>"`
  for paste-ready fields.
- Run the project's store-metadata validator when one exists. If that
  validator supports an owner-placeholder allowance, use it while
  placeholders remain, then run the strict form when none remain.
- Run project identity or release-config checks when they exist.
- If version configuration changed, run the project's cheapest relevant
  compile or assemble task.
- Run product tests only when production code was separately changed in the
  same release task.
- Leave visual review to the user. Do not launch apps or devices, capture
  screenshots, or change simulator or emulator state.

Completion: every applicable command passes, or each failure is diagnosed and
reported without expanding the task.

### 8. Hand off the prepared release

- Report the target and base; versions and builds before and after; stores
  and locales written; the verified delta represented; changed files; and
  validation results.
- Call out unresolved owner placeholders, user visual review, and
  release-console gates.
- State that no tag, commit, upload, or publish was performed.

Completion: the user can distinguish completed local preparation from every
remaining manual or externally mutating release step.
