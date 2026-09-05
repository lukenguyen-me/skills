---
name: appstore-submission-content
description: Generate complete, ready-to-paste App Store Connect text content. Covers all localizable fields, enforces Apple character rules, detects multi-language support, and outputs structured markdown.
---

# App Store Submission Content

Generate polished, App Store-ready text content for your iOS/macOS app submission. This skill handles all localizable fields, enforces Apple's strict character and formatting rules, and outputs clean markdown organized by language.

## When to Use

Users ask things like:
- "Generate App Store description for my app"
- "Write App Store keywords and description"
- "Create submission content for [app name]"
- "Help with App Store Connect text fields"

Your job: gather app details, generate compelling content for all fields, and output structured markdown ready to copy-paste into App Store Connect.

## What Makes Strong App Store Content

Apple's App Store is highly competitive. Your text content is often the deciding factor between a download and being scrolled past.

**App Name (30 chars max)**
- Weak: "My Great Task Manager App"
- Strong: "Done - Simple Tasks"

**Subtitle (30 chars max)**
- Weak: "The best to-do list app ever made"
- Strong: "Focus on what matters, not the noise"

**Description (4000 chars)**
- Weak: "This app has many features. You can add tasks. You can check them off. It is very useful."
- Strong: "Done replaces your scattered notes with a single, elegant system. Add tasks in seconds, organize with natural tags, and get intelligent reminders when it actually matters. No subscription required."

**Keywords (100 chars, comma-separated)**
- Weak: "todo, task, list, tasks, todo list, to do, checklist, check list, productivity, organize"
- Strong: "tasks,focus,productivity,minimal,simple,organize"

**What's New**
- Weak: "Bug fixes and improvements"
- Strong: "Redesigned home screen with quick-add widget. Fixed crash when syncing with iCloud. Added dark mode support."

## Field Reference

### Localizable Fields (per language)

| Field | Max Characters | Notes |
|-------|----------------|-------|
| App Name | 30 | No keyword stuffing allowed |
| Subtitle | 30 | Strongest single differentiator |
| Description | 4000 | First ~255 chars shown before "Read More" |
| Promotional Text | 170 | Only field updatable without new version |
| Keywords | 100 | Comma-separated, no spaces in individual keywords |
| What's New | 4000 | Written for humans deciding whether to update |

### Global Fields (not localized)

| Field | Format | Notes |
|-------|--------|-------|
| Copyright | `YYYY Company Name` | No symbol, year first |
| Primary Category | From category list | Required |
| Secondary Category | From category list | Optional |
| App Review Notes | Free text | Credentials + instructions for reviewer (never public) |

## Character Rules

Your content must NEVER contain characters that trigger App Store rejection:

### Forbidden (rejection risk)

| Category | Forbidden Characters |
|----------|---------------------|
| Emoji | All emoji (U+1F300+) |
| Checkmarks | ✓ (U+2713), ✔ (U+2714) |
| Bullets | • (U+2022), ‣ (U+2023), ◦ (U+25E6) |
| Dagger | † (U+2020), ‡ (U+2021) |
| HTML | Any HTML tags like `<br>`, `<b>`, `<strong>` |

### Allowed

- Standard ASCII and punctuation
- Hyphens (`-`) and asterisks (`*`) as bullet replacements
- Accented/diacritic characters for non-English localizations
- Line breaks within Description and What's New
- Apostrophes (`'`), quotation marks (`"`, `'`)

## Supported Languages

The App Store supports 39 locales. Generate content in these languages as needed:

| Code | Locale |
|------|--------|
| ar | Arabic |
| ca | Catalan |
| zh-Hans | Chinese (Simplified) |
| zh-Hant | Chinese (Traditional) |
| hr | Croatian |
| cs | Czech |
| da | Danish |
| nl | Dutch |
| en | English |
| fi | Finnish |
| fr | French |
| de | German |
| el | Greek |
| he | Hebrew |
| hi | Hindi |
| hu | Hungarian |
| id | Indonesian |
| it | Italian |
| ja | Japanese |
| ko | Korean |
| ms | Malay |
| no | Norwegian |
| pl | Polish |
| pt | Portuguese |
| ro | Romanian |
| ru | Russian |
| sk | Slovak |
| es | Spanish |
| sv | Swedish |
| th | Thai |
| tr | Turkish |
| uk | Ukrainian |
| vi | Vietnamese |

## Multi-Language Detection

### How to Detect Localization in a Project

1. **iOS/macOS Native:**
   - `*.lproj/Localizable.strings` files
   - `knownRegions` in `.xcodeproj/project.pbxproj`

2. **Flutter:**
   - `lib/l10n/*.arb` files

3. **React Native / Generic:**
   - `i18n/`, `locales/`, `translations/` directories

4. **Android / Cross-platform:**
   - `res/values-*/strings.xml`

### Multi-Language Workflow

1. Scan project for localization signals using the paths above
2. If localization detected → report found languages, ask user to confirm multi-language output (recommend yes)
3. If confirmed → generate all localizable fields for each detected language
4. If no localization detected → default to English (US) only

## Project Analysis Guide

### What to Extract

Before generating content, analyze the codebase to gather:

| Source | What to Look For |
|--------|-----------------|
| `package.json`, `Info.plist` | App name, bundle ID |
| `README.md` | App description, key features |
| Source code comments | Unique selling points |
| Existing marketing materials | Brand voice, key phrases |
| Feature flags | Latest features for "What's New" |

### Questions to Ask User

If information is missing, ask:
- What is the app's primary purpose?
- Who is the target audience?
- What are the top 3 features?
- Is there existing copy you'd like to adapt?
- What company/developer name for copyright?

## Per-Field Writing Guidance

### App Name

**Weak:** Contains keywords, too long, generic
**Strong:** Memorable, distinctive, fits 30-char limit

| Weak | Strong |
|------|--------|
| "Best Task Manager Todo List App 2024" | "Done" |
| "Professional Calendar Scheduler Pro" | "Cal" |

### Subtitle

**Weak:** Generic praise, keyword stuffing
**Strong:** Specific benefit, unique positioning

| Weak | Strong |
|------|--------|
| "The best productivity app ever!" | "Your tasks, organized beautifully" |
| "Todo list checklist organizer app" | "Stop forgetting, start doing" |

### Description

**Weak:** Feature list without context, generic claims
**Strong:** Benefit-driven opening, specific features, social proof

Structure:
1. Opening hook (1-2 sentences) - What problem do you solve?
2. Key benefits (2-3 sentences) - Why should someone care?
3. Features (3-5 bullet-style lines) - What can they do?
4. Call to action (1 sentence) - Download now

**Weak:**
"This app has many features. You can add tasks. You can organize them into lists. You can set due dates. You can get reminders. It is very useful. Download now."

**Strong:**
"Done replaces scattered notes with a single, elegant system. Capture tasks in seconds, organize with natural tags, and get intelligent reminders when it matters. No subscription required. Download now."

### Keywords

- 100 characters maximum
- Comma-separated, no spaces after commas
- No repeated words from name/subtitle
- Include competitor names if relevant

| Weak | Strong |
|------|--------|
| "todo,task,list,check,organize,productivity" | "tasks,focus,minimal,simple,habits,daily" |

### What's New

- Write for users deciding whether to update
- Highlight meaningful changes, not just "bug fixes"
- Include new features by name when possible
- Keep it scannable

| Weak | Strong |
|------|--------|
| "Bug fixes and improvements" | "Redesigned home screen with quick-add widget. Fixed crash when syncing with iCloud." |
| "Performance improvements" | "App now launches 2x faster on older devices" |

## Output Format

Generate structured markdown with one section per language, then global fields:

```markdown
## English (US)

### App Name
[Your app name]

### Subtitle
[Your subtitle]

### Description
[Your description]

### Promotional Text
[Your promotional text]

### Keywords
[Your keywords]

### What's New
[Your what's new]

---

## French (France)

### App Name
[Your app name in French]

[... same subsections ...]

---

## Global Fields

### Copyright
YYYY Company Name

### Primary Category
[Category]

### Secondary Category
[Category or "None"]

### App Review Notes
[Your notes for the reviewer]
```

## Example: Productivity App

```
## English (US)

### App Name
Done

### Subtitle
Focus on what matters, not the noise

### Description
Done replaces your scattered notes with a single, elegant system. Add tasks in seconds, organize with natural tags, and get intelligent reminders when it actually matters. No subscription required.

• Capture tasks instantly with natural language input
• Organize with smart tags and custom lists
• Get reminders that actually help, not annoy
• Sync across all your Apple devices
• Works completely offline

Download Done today and finally get things done.

### Promotional Text
Now with dark mode and Siri shortcuts

### Keywords
tasks,focus,productivity,minimal,simple,organize,goals,daily

### What's New
• Redesigned home screen with quick-add widget
• Dark mode support
• Siri Shortcuts integration
• Fixed crash when syncing with iCloud

---

## Global Fields

### Copyright
2026 Example Studio

### Primary Category
Productivity

### Secondary Category
None

### App Review Notes
Test account: demo@example.com / TestPassword123
Use the included test account to access all premium features.
```

## Example: Health App

```
## English (US)

### App Name
Pulse

### Subtitle
Your daily health companion

### Description
Pulse helps you build healthier habits with personalized insights and easy tracking. From sleep to steps, see your complete health picture in one beautiful app.

• Track sleep, activity, and mindfulness
• Personalized daily recommendations
• Beautiful charts and progress insights
• Health data stays on your device
• Apple Watch companion app

Start your wellness journey with Pulse today.

### Promotional Text
Free for a limited time - all features unlocked

### Keywords
health,fitness,wellness,sleep,activity,track,steps,exercise

### What's New
• New sleep analysis with sleep stages
• Apple Watch Series 10 support
• Bug fixes and performance improvements

---

## German (Germany)

### App Name
Pulse

### Subtitle
Dein täglicher Gesundheitsbegleiter

### Description
Pulse hilft dir, gesündere Gewohnheiten aufzubauen - mit personalisierten Einblicken und einfachem Tracking. Von Schlaf bis Schritte, sieh dein komplettes Gesundheitsbild in einer schönen App.

[... continue with German localization ...]

---

## Global Fields

### Copyright
2026 Example Studio

### Primary Category
Health & Fitness

### Secondary Category
Medical

### App Review Notes
Test account: demo@example.com / TestPassword123
The app uses HealthKit - no special setup needed for testing.
```

## Quick Reference

### Character Limits

| Field | Limit |
|-------|-------|
| App Name | 30 |
| Subtitle | 30 |
| Description | 4000 |
| Promotional Text | 170 |
| Keywords | 100 |
| What's New | 4000 |

### Keyword Format
- Comma-separated: `word1,word2,word3`
- No spaces after commas
- No duplicate keywords
- No words from name/subtitle

### Copyright Format
- `YYYY Company Name`
- No © symbol
- No period at end

### Forbidden Characters
- All emoji
- ✓ ✔ • ‣ ◦ † ‡
- Any HTML tags

### App Store Categories

**Primary Categories:**
- Books
- Business
- Catalogs
- Education
- Entertainment
- Finance
- Food & Drink
- Games
- Health & Fitness
- Lifestyle
- Medical
- Music
- Navigation
- News
- Photo & Video
- Productivity
- Reference
- Shopping
- Social Networking
- Sports
- Stickers
- Travel
- Utilities
- Weather
