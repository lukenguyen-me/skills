# App Store Connect fields

Load this file when preparing App Store copy. Character limits and forbidden
characters are enforced by `scripts/check_limits.py`; run `--list --store app`
if the table below is not in context.

## Localizable fields

| Field | Limit | Role |
| --- | --- | --- |
| App name | 30 characters | Memorable product name. No keyword stuffing. |
| Subtitle | 30 characters | Specific benefit. Strongest single differentiator. |
| Promotional text | 170 characters | Highlight this release. Updatable without a new binary. |
| Description | 4000 characters | Problem, benefits, capabilities, then a close. First ~255 characters show before Read More. |
| Keywords | 100 UTF-8 bytes | Comma-separated discovery terms. |
| Version notes | 4000 characters | Why a customer should update. Follow the version-notes rules in `SKILL.md`. |

## Global fields

| Field | Format |
| --- | --- |
| Copyright | `YYYY Company Name` with no copyright symbol and no trailing period |
| Primary category | Keep the project's existing category. For a new listing, pick from the current App Store Connect list. |
| Secondary category | Optional. `None` when unused. |
| App Review notes | Reviewer-only. Credentials plus how to exercise new behavior. Never public listing copy. |

Support URL, marketing URL, and privacy-policy URL are owner facts. Keep
existing values or placeholders.

## Character rules

Forbidden in every App Store text field: emoji, `✓` `✔` `•` `‣` `◦` `†` `‡`,
and HTML.

Allowed: ASCII punctuation, hyphens as bullets, accented characters needed by
a locale, and line breaks in description, promotional text, version notes, and
review notes.

## Keywords

- Comma-separated with no spaces after commas: `tasks,focus,minimal`
- No duplicate keywords
- No word that already appears in the app name or subtitle
- Count UTF-8 bytes, not characters

## Description shape

1. Opening hook: the problem the app solves
2. Why a customer should care
3. Three to six hyphen bullets of things they can do
4. One-sentence close

Keep the first ~255 characters meaningful on their own.

## New document shape

When no App Store document exists, emit paste-ready markdown per locale, then
global fields. Put each localizable field value in a fenced `text` block so
`scripts/check_limits.py --markdown` can read it:

````markdown
## English (US)

### App name

```text
<app name>
```

Limit: 30 characters.
````

Repeat that field shape for subtitle, promotional text, description, keywords,
and version notes, then add global fields (copyright, categories, review notes)
the same way. When updating an existing document, keep its headings, locale
names, and limit annotations.
