# Play Console fields

Load this file when preparing Play Store copy. Character limits and forbidden
characters are enforced by `scripts/check_limits.py`; run `--list --store play`
if the table below is not in context.

Play Console has no keywords field. Search indexes the title, short
description, and full description.

## Localizable fields

| Field | Limit | Role |
| --- | --- | --- |
| App title | 30 characters | Memorable product name. No keyword stuffing. |
| Short description | 80 characters | First line in search results. One specific benefit. |
| Full description | 4000 characters | Problem, benefits, capabilities, then a close. First ~167 characters show before Read More. |
| Version notes | 500 characters | Why a customer should update. Same claims as App Store, compressed. Follow the version-notes rules in `SKILL.md`. |

## Global fields

| Field | Format |
| --- | --- |
| Primary category | Keep the project's existing category. For a new listing, pick from the current Play Console list. |
| Secondary category | Optional. `None` when unused. |
| Tags | Up to five console tags when the project already uses them or the user asked for listing copy. |
| Content rating | Suggest a starting point. The owner completes the IARC questionnaire from the submitted artifact. |

Support email, website, phone, and privacy-policy URL are owner facts. Keep
existing values or placeholders.

## Character rules

Forbidden in app title and short description: emoji, `★` `☆`, line breaks,
and repeated punctuation such as `??` `!!` `---` `***`.

Forbidden in every Play Store text field: HTML, and ranking or sales claims
such as "ranked #1", "most downloaded", or store-comparison superlatives.

Full description and version notes may use line breaks. Emoji are allowed in
full description. For a dual-store app, match the App Store voice: hyphen
bullets, no emoji, unless the existing Play listing already uses them.

## Full description shape

1. Opening hook: the problem the app solves
2. Why a customer should care
3. Three to six hyphen bullets of things they can do
4. One-sentence close

Keep the first ~167 characters meaningful on their own.

## New document shape

When no Play Store document exists, emit paste-ready markdown per locale, then
global fields. Put each localizable field value in a fenced `text` block so
`scripts/check_limits.py --markdown` can read it:

````markdown
## English (United States)

### App title

```text
<app title>
```

Limit: 30 characters.
````

Repeat that field shape for short description, full description, and version
notes, then add global fields (categories, tags, content rating, contact) the
same way. When updating an existing document, keep its headings, locale names,
and limit annotations.
