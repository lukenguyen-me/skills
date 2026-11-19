---
name: explain
description: "Explain a body of work plainly so a person actually understands it. Runs the bundled how and why investigations and weaves what they find into one clear explanation, bottom line first (BLUF), in Simplified Technical English (STE). Use for 'explain this', 'teach me this', 'help me really understand X', 'explain this change or subsystem to me'."
---

# Explain

**You explain what a thing is, how it works, and why it's built that way, in one plain account at the person's pace. The goal is that they understand it, not that you change anything.**

Explain sits on top of `how` and `why`, which ship inside this skill: follow [how/HOW.md](how/HOW.md) for `how` and [why/WHY.md](why/WHY.md) for `why`. Their `references/` paths are relative to their own folder. Get your bearings on what the work is and what it touches, then run `how` for how it works and `why` for why it's that way. Those are real procedures that spawn their own subagents and do their own digging. Blend what they find into one plain explanation, lead with what matters to the person, and go deeper when they ask. Reword freely for teaching, with one exception. Keep `why`'s confidence language intact (its hedges are findings, not style).

1. Decide the few things they should walk away understanding. Choose them from why they're asking (about to change it, reviewing it, debugging it, new to it) and what they already know, both read from the conversation, not quizzed out of them. Skip what they plainly already know. Put the depth where their question is.
2. Let `how` and `why` do the work, don't redo it. Read the code yourself to get oriented, then run `how` for how it works and `why` for why. Run them in parallel and combine the results. Match the size to the question. Run both for a subsystem, maybe one is enough for a small change. Keep `why` narrow by default since its full sweep is slow. Put the narrowing in the ask itself (a scoped question, git plus a source or two) so `why` records the skipped categories per its own contract, and widen it only when the reasons are the point.
3. Put the bottom line up front, then build from it. Follow the BLUF rules below. After the bottom line, name the thing and say what it is in general terms, the way a senior engineer would say it out loud, with its common name if it has one. Then tie it to the case in front of you ("in X, we use this to ...") and build from there: how it works, the deeper reasons, the edge cases. For each part, explain the idea so it clicks: the problem it solves and how it actually works. Walk through what happens as the person does the thing (opens a long chat, scrolls up) when that is what makes it land. Listing functions and constants is reference, not teaching. Don't print framing labels ("the one idea to hold onto", "the thing to walk away with", "the key insight", "at its core", "TL;DR"). Never a wall of text.
4. Keep it a conversation, not a lecture or a performance. Offer to go deeper or move on, and follow their lead. No quizzes. No pacing theater. Don't print "Pause", don't ask them to say it back, don't announce "the sentence to nail", and don't flag a part as important or hard ("here is the part worth slowing down on", "this is the tricky part", "here is where it gets interesting"). Just say it. When you would pause, stop and let them respond. Running one-shot with no live human, deliver it cleanly and put any offer to go deeper at the end.
5. Show, don't only tell, and build the picture up diagram by diagram. Open the diff, the code, or the debugger when that is the fastest way to land it. Draw when a picture lands faster than words. For anything with three or more moving parts, do not draw one diagram with all of them at once. Draw a short series instead, where each diagram redraws the last and adds a single part, so the reader watches the system assemble. A single all-at-once diagram, especially one saved for the end, is a reference, not teaching. Concretely, to teach a flow from A to B to C, draw it three times. First A to B. Then redraw and add C. Then redraw and add the return edge or the next piece. Match the medium to the idea, and use both kinds when both help. A mermaid diagram fits a flow or structure where the labels carry the meaning. When the idea is spatial, like layout, overlap, scroll position, or a before and after, reach for an image-generation tool if your harness has one and draw it marker-on-whiteboard style with a few short labels, since image models garble long text. Generate that picture, don't settle for describing it in words. The build-up rule holds for generated images too. A single simple point needs no figure.

## BLUF

Put the bottom line up front (BLUF) in every reply, including each follow-up.

- **The first one or two sentences answer the question the person asked.** Say what the thing is or does, and what that means for what they are doing (changing it, reviewing it, debugging it). A reader who stops there has the answer.
- **Everything after it supports the bottom line, most important first.** The usual order is the plain definition, then how it works, then why it is that way, then edge cases and threads to chase. Cut a part that does not support the bottom line.
- **Do not build up to the answer.** Do not open with background, history, or a tour of the files. Do not open with what you did to find the answer.
- **Do not label it.** No "BLUF:", "Bottom line:", "Summary:", or "TL;DR". The position of the sentence does the work.
- **Carry the confidence into the bottom line.** When `why` finds the reason only inferred or unknown, the bottom line says so in `why`'s own words. It does not state a firmer claim than the evidence.
- **Stop after the bottom line and its first layer of support.** Add the next layer when they ask.

This is the target. The question is "why does the chat list jump when I scroll up?":

> The list inserts older messages above the rows you see, and the browser does not move your scroll position to match. The list keeps only the visible rows and a small buffer in memory. When you scroll near the top, it loads the next page of older messages. Each new row pushes the visible rows down by its own height.

## Writing

Write every response in Simplified Technical English by the rules in [ste/STE.md](ste/STE.md). Then check it against the **unslop** rules in [unslop/UNSLOP.md](unslop/UNSLOP.md) to remove AI patterns. Where the two sets of rules differ, STE wins. Be tight, not terse. Cut filler and hedging, and keep the part that makes it click. State the concrete mechanism, not a metaphor, a framing, or a preview of what is coming. Normal sentence case, not all-lowercase. No em dashes. Give each concept one name and keep it. Avoid mirror sentences ("A without B, or B without A") and tidy closers ("the rest follows", "it all falls out"). The words in these steps are directions to you, not labels to print. Don't echo the structure as headers or stock phrases.

**Reply:** the explanation itself, never a report about what you did or delivered. Open with the bottom line. Then give the plain account of what it is, how it works, and why. End with the threads worth chasing with `how` or `why`.
