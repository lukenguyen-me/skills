---
name: appstore-release-notes
description: Generate compact App Store release notes for a new iOS or macOS release from git history, tags, commits, and changed files. Use when asked for App Store "What's New", release notes, update notes, or app version notes, especially when previous or target versions may be specified.
---

# App Store Release Notes

Create ready-to-paste App Store Connect "What's New" notes for a new release. The output must be compact, clear, user-facing, and based on real changes.

## Workflow

1. Identify the comparison range.
   - If the user specifies a previous version, tag, branch, or commit, use it as the base.
   - If no previous version is specified, find the latest relevant git tag and use it as the base.
   - If the user specifies a target version, tag, branch, or commit, use it as the target.
   - If no target is specified, use the latest code, normally `HEAD`.
   - If no tags exist, compare against the earliest useful commit or summarize recent history, and state the assumption briefly before the notes.

2. Inspect git history and changed files.
   - Prefer commands like `git tag --sort=-v:refname`, `git log --oneline <base>..<target>`, `git diff --stat <base>..<target>`, and targeted `git diff --name-only <base>..<target>`.
   - Read relevant files or diffs when commit messages are too vague.
   - Look for app version files only when needed to confirm the release version.

3. Check localization support.
   - Detect supported App Store locales from project files when possible: `*.lproj`, `Localizable.strings`, `InfoPlist.strings`, `.xcstrings`, `fastlane/metadata`, `metadata`, Flutter `lib/l10n/*.arb`, React Native `locales`, `i18n`, or `translations`.
   - If the app supports multiple languages, generate release notes for each supported App Store locale.
   - If supported languages are unclear, default to the main language and mention the assumption briefly before the notes.
   - Adapt each localized note to sound natural for that locale and culture. Do not translate word by word.
   - Keep the same factual meaning across languages, but allow phrasing, word order, and tone to fit local App Store expectations.

4. Keep only user-facing changes.
   - Include: visible features, behavior changes, usability improvements, performance improvements that users can feel, crashes, data loss fixes, sync fixes, login fixes, purchase fixes, accessibility improvements, localization changes, and UI changes.
   - Exclude: CI, build scripts, dependency bumps, internal refactors, formatting, tests, lint, docs, and developer-only changes unless they clearly affect users.

5. Classify every note.
   - Start each item with one of these plain labels: `Feature:`, `Fix:`, or `Improvement:`.
   - Use `Feature:` for new capabilities or newly exposed user options.
   - Use `Fix:` for corrected broken behavior, crashes, display issues, incorrect data, or reliability problems.
   - Use `Improvement:` for better speed, polish, accessibility, usability, copy, layout, flow, or existing behavior.

## Output Rules

- Output only the release notes unless a range assumption must be stated.
- Each item must start with a hyphen.
- Use plain text only.
- Do not use emoji, bullet symbols, checkmarks, arrows, smart quotes, or decorative characters.
- For localized notes, use the locale's normal writing system and diacritics when needed for natural text.
- Do not use Markdown headings unless the user asks for them.
- For multiple languages, group by locale code or language name, then use hyphen bullets under each group.
- Keep each item to one sentence.
- Prefer 3 to 8 items.
- Combine duplicate or closely related changes.
- Do not write generic filler such as "Bug fixes and improvements", "Performance improvements", "Stability updates", or "General enhancements".
- Do not mention commit hashes, file names, branch names, pull requests, internal modules, or implementation details.
- Do not invent changes. If evidence is weak, omit the item or ask one concise clarification question.

## Writing Style

- Make each item specific enough that a user understands what changed.
- Lead with the user-visible result, not the implementation.
- Use simple verbs: Added, Fixed, Improved, Updated, Reduced, Restored, Prevented.
- Avoid marketing language, hype, and vague claims.
- Avoid "now" unless it improves clarity.

## Example Output

```text
- Feature: Added quick note capture from the home screen.
- Improvement: Improved calendar loading speed for large event lists.
- Fix: Fixed a crash that could happen when syncing iCloud data.
- Fix: Fixed incorrect totals shown after editing a saved expense.
```

## Example Multilingual Output

```text
en-US
- Feature: Added quick note capture from the home screen.
- Fix: Fixed a crash that could happen when syncing iCloud data.

vi
- Feature: Thêm cách ghi chú nhanh ngay từ màn hình chính.
- Fix: Khắc phục lỗi có thể khiến ứng dụng bị văng khi đồng bộ dữ liệu iCloud.
```
