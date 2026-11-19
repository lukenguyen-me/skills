# STE

Write every explanation in Simplified Technical English (STE), following
[ASD-STE100](https://www.asd-ste100.org/) Issue 9 (January 2025). STE exists so
a reader cannot misread the text. For an explanation, that means the reader
understands it after one read.

This file holds the writing rules only. It does not include the official STE
dictionary (about 900 approved words, each with one meaning and one part of
speech). Do not copy or claim that dictionary. Use short, common words instead.

## Rules

| Rule | Do | Do not |
| --- | --- | --- |
| One meaning per word | Pick one word for a concept and reuse it | Rotate "cache", "store", and "buffer" for the same thing |
| One part of speech | "The loader reads the file." | "Give the file a read." |
| Active voice | "The scheduler starts the job." | "The job is started." |
| Simple tenses | "The cache evicts the item." | "The cache will have been evicting the item." |
| One idea per sentence | "The request reaches the gateway. The gateway checks the token." | "The request reaches the gateway, which checks the token and then forwards it." |
| Sentence length | 20 words or fewer for an instruction. 25 or fewer for a description | Chains of subordinate clauses |
| Noun clusters | Three words or fewer | "session refresh token rotation handler config" |
| No missing words | Keep the subject, the verb, and the article | "Token expired, request rejected" |
| Instructions | Imperative: "Open `auth.ts`." | "It is a good idea to open `auth.ts`." |
| Lists | A vertical list for three or more steps or conditions | A sequence buried in one sentence |
| Paragraphs | One topic. Six sentences or fewer | Paragraphs that change topic |
| Terminology | Keep the project's technical nouns and verbs. Define a new term once, then reuse it | Jargon the reader has not seen, or two names for one thing |

Also:

- Do not use contractions ("does not", not "doesn't").
- Do not use semicolons.
- Use one verb, not a phrasal verb ("start", not "kick off"; "find", not "figure out").
- Use a verb for an action, not a noun ("the parser validates the input", not "the parser performs validation of the input").
- Count a hyphenated word, a number with its unit, or a proper noun as one word.

An explanation is descriptive writing, with a limit of 25 words per sentence.
Steps the reader must follow are procedural writing, with a limit of 20 words
per sentence, in the imperative.

## Hedges

Use at most one hedge in a sentence, and only when the fact is uncertain. Do
not stack "may", "might", "could", and "potentially".

Results from `why` are an exception. Their confidence tiers come from
`why/references/epistemics.md`. Keep that wording as it is, even when it is
longer than STE allows. It reports what the evidence shows, so it is not a
style choice.

## Leave these as they are

- Code, identifiers, file paths, and commands
- Quoted text: user quotes, logs, error strings, commit messages
- The project's own names for screens, products, and domain concepts

## Self-check

Before you send a reply, read it once:

- Does any sentence have more than 25 words (20 for an instruction)?
- Does any sentence have two ideas or two instructions?
- Did one concept get two names?
- Is there a passive verb that hides the actor?
- Is there a contraction or a semicolon?
