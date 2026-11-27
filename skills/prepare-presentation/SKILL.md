---
name: prepare-presentation
description: >
  Prepare material that a person presents or shares with other people: slide
  decks, meeting walkthroughs, proposal or design summaries, reports,
  one-pagers, and explainer pages. Sets the communication (bottom line first,
  Simplified Technical English, a proof or example for every claim), the
  structure (general to specific, before and after), the density (the screen
  supports the speaker, it does not replace the speaker), and a plain visual
  style with diagrams, delivered as a standalone local HTML file. Use this
  skill whenever the user asks for slides, a deck, a presentation, a talk, a
  demo walkthrough, a summary page, a report for a team or a manager, or says
  "I have a meeting", "prepare something to present", "help me walk people
  through this", or "turn this doc into slides", even when the user does not
  name a format. Do not use it for chat replies, source code, or documents
  written for agents.
---

# Prepare presentation

Make material that helps a person explain something to other people.

The audience sees the material one time, at the speed of the speaker or of their own scroll. They did not read the source documents. Each choice below follows from that.

This skill decides the words, what goes on the screen, in what order, and how it looks.

## Workflow

1. **Read only the sources the user names.** The folder can hold other work. Do not open other files to "get context" unless the user says so.
2. **Propose before you render.** Reply with a short outline, your suggestions, and the questions that change the result. Then wait. A rendered deck built on a wrong assumption costs more than one round of talk.
3. **Render** in the format the user chose. See [Formats](#formats).
4. **Look at the result.** Open it in a headless browser and capture each slide or section when you can. Check for overflow, wrapped lines, and wrong alignment. Put captures in a temporary folder, not in the user's project. Tell the user what you did not look at.
5. **Iterate with small edits.** The user reviews by reaction ("too dense", "I do not understand this one"). Change the thing they named, then find the same pattern in the other parts and change it there too.

Questions worth asking in step 2, when the request does not answer them:

- What decision or action does the user want from the audience?
- Who is the audience, and what do they already know?
- How much time does the user have?
- What is in scope for the numbers (for example an estimate)?

When the user says "slide 5", check which number they mean if the slides show more than one number (a section number and a page number).

## Communication

**Bottom line first.** The first screen states the conclusion, the size of the thing, and what the user wants from the audience. The reason comes after. A listener who knows the destination follows the route.

**Simplified Technical English.** The audience reads a line one time while they listen, and many read English as a second language. Write so a line cannot be misread:

- One idea for each sentence. Keep a sentence to about 20 words. Most lines on a screen are much shorter.
- Active voice and simple tenses: "The server checks the request", not "The request is checked".
- One word for one thing. If the first screen says "route", do not say "endpoint" or "path" for the same thing later.
- Keep the project's own technical terms. Explain an acronym the first time, or leave it out.
- Use a verb for an action: "replace the full set", not "full set replacement".
- No filler and no stacked hedges ("may possibly", "it is important to note that").

**Each claim brings its proof.** When a screen says something is a problem, show a real case of the problem. When it states a rule, show the rule applied. Take the examples from the source material, not from imagination. A claim without an example asks the audience to trust the speaker. An example lets them see it.

**Before and after.** The strongest proof for a change is a pair: the current thing next to the proposed thing. Label both sides. Use the same pair format through the whole piece so the audience learns it one time.

**General to specific.** Start with the rule that applies anywhere. Then show it in this project. Bring domain knowledge in through one concrete case (a named thing, a real consequence), not through a paragraph of background.

**Say only what the sources support.** If the sources show that a flow does not change and only the names change, say that. Do not present a rename as a change of mindset. When a screen shows only the new way with no old way next to it, the audience cannot tell which one they see.

**Count, do not estimate, what can be counted.** Derive totals and group sizes from the source. When a number is your assumption, keep it editable where the format allows it, and tell the user in the chat which numbers are yours.

**Each fragment must stand alone for a person who did not read the source.** A term, a code, or a status the source introduced ("HTTP 202", a ticket name) means nothing on the screen without its link to what the audience can see. Tie it to an element on the same screen ("Step 3 answers 'accepted', not 'done'") or leave it for the speaker.

## Density

The screen supports the talk. It does not carry the talk.

Imagine the user speaking over each screen. Keep what the audience needs to look at while the user speaks: the title, the example, the diagram, one short takeaway. Remove what the user will say:

- No description sentence under a title.
- No explanation sentence under a step, a rule, or a diagram label.
- No column that only restates another column in words.
- No slide of caveats, open questions, or time budgets, unless the user asks for one. Give those to the user in the chat, where they help the user prepare.

Do not cut the examples and patterns. They are the content. A screen with a heading and a real before-and-after pair is complete. A screen with a heading and a paragraph is not.

When you cut text, check that each fragment that remains still makes sense alone. Short is not the goal. Clear at a glance is the goal.

A callout is one sentence the audience must not miss. Use at most two for each screen.

## Formats

All formats use the same communication rules and the same visual style. The structure changes.

**Slides** (a talk, a meeting, a screen share)

- Cover: title, the bottom line in numbers, nothing else.
- Why: the problem, shown with real cases.
- Approach: the rules, each with a before-and-after example. Then the one domain example.
- Patterns: one slide for each representative pattern. Choose representatives. Do not list everything.
- Cost or impact: a small table with groups, counts, and a total.
- Last slide: next actions on one side, "Q&A" on the other.
- Keep the deck short enough to leave time for discussion and for the real document. Count about one minute for each slide. Do not print timings on the slides.

**Report or page** (people read it alone, by scrolling)

- Open with a bottom-line block: the conclusion, the key numbers, the action needed.
- Use the same section order as the slides. Each section opens with its example or diagram, then at most two or three short sentences. A reader has no speaker, so a little more text is correct here. Keep it to what the diagram cannot show.
- Put reference tables at the end.

**Other formats** (a document, a message, a one-pager): keep the order (bottom line, proof, approach, patterns, cost, next actions) and the density rule. Adapt the layout.

Start from the bundled templates. They hold the style tokens and each component:

- `assets/deck-template.html`: slides on a fixed 16:9 stage, keyboard navigation, all components.
- `assets/page-template.html`: one scrolling column for a report or a page.

Copy the template, replace the sample content, and delete the components you do not use. Read [references/visual-style.md](references/visual-style.md) before you add a component the templates do not have.

## Visual style

The short version. The reference file has the detail and the reasons.

- **Plain.** One quiet background, much white space, thin dividing lines. No cards, no boxes around content, no shadows.
- **Solid, not soft.** A coloured element is a solid colour. Do not draw a pale fill with a border in the same hue. Do not put an icon inside a circle or a box.
- **Two colours with a meaning.** One colour for the current or "before" side, one for the proposed or "after" side. Use them for nothing else.
- **A diagram where there is a structure.** One-to-many, many-to-one, a hierarchy, a topology, a sequence, a timeline, a range: draw it. Do not describe it.
- **Small type for a shared screen.** People read it on their own monitors in a call, not on a projector across a room.
- **Footer:** the title and the page number only.

## Output

Write one standalone HTML file on the user's machine. Use system fonts and inline SVG. Load nothing from the network: no web fonts, no CDN scripts, no remote images.

Do not publish the material to an online service, a hosted page, or a shared document unless the user asks for that. Presentations often hold internal work, and a private-by-default link is still a copy outside the user's machine.

Save the file next to the sources or where the user says. Tell the user the full path and how to move through it.

## Self-check

Before you hand over:

- Does the first screen state the conclusion and what the user wants?
- Does each claim have a real example from the sources?
- Is each before-and-after pair labelled, and does the same colour mean the same side everywhere?
- Can a person who did not read the sources understand each fragment that is on the screen?
- Is there a sentence on the screen that the user will say out loud? Remove it.
- Is there a structure described in words that a diagram can show?
- Does the file open with the network off?
- Did you tell the user which numbers are your assumptions and which parts you did not check by eye?
