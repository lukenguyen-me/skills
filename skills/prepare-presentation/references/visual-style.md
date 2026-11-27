# Visual style

The style is plain on purpose. The examples and diagrams carry the meaning, so nothing else on the screen competes with them. Read this file before you add a component that the templates do not have.

## Tokens

Both templates define these on `:root`. Reuse them. Do not add a colour without a meaning.

| Token | Value | Use |
| --- | --- | --- |
| `--bg` | `#fbfaf7` | The one background, a warm off-white |
| `--ink` | `#18212c` | Titles, headings, key values |
| `--soft` | `#5c6775` | Secondary text |
| `--faint` | `#98a1ac` | Small labels, footer |
| `--line` | `#e3e0d7` | Thin dividing lines, diagram links |
| `--old` | `#b0500f` | The current or "before" side, warnings |
| `--new` | `#1d5bbf` | The proposed or "after" side, accents |
| `--old-tint`, `--new-tint` | pale versions | Only for a value pill or a diagram highlight area |

Fonts: the system sans stack for text and the system mono stack for code, paths, commands, and identifiers. No web fonts.

## Type scale

For slides on the 1280 × 720 stage:

| Element | Size |
| --- | --- |
| Cover title | 46px, bold |
| Slide title | 30px, bold |
| Heading in content | 16.5px, semibold |
| Body | 15px |
| Code and paths | 12.5–14px mono |
| Small caps label | 10.5–12px, bold, letter-spacing .1em, uppercase |
| Callout | 18px, semibold |

These sizes look small in the source and are right in use. The stage scales to the window, and the audience reads a shared screen on their own monitor. Do not enlarge them for "readability" unless the user presents on a projector in a room.

For a page, use 16px body text in a column of about 820px.

## Layout

- Slides: a fixed 1280 × 720 stage scaled to the window, padding 56px 72px. The small label and the title sit at the top. The content block is vertically centred in the space that remains.
- Separate things with space first, then with a 1px line in `--line`. Do not use a box.
- Two columns for a comparison, three or four for parallel items. Do not go past four.

## What to avoid, and why

| Avoid | Why | Use |
| --- | --- | --- |
| Cards: a border, a fill, and a radius around each item | A grid of boxes makes every item look the same and the slide look heavy | Space and thin lines |
| A pale fill with a border in the same hue | It reads as a web-app widget, not a statement | A solid colour, or no fill |
| An outlined number or icon | Same soft look | A solid colour glyph |
| An icon inside a circle or a square | The container is noise | The bare icon |
| A left colour bar for a callout | It reads as a quote block, not as a point to remember | A bare solid icon, then the sentence in bold |
| An underline on a value or an input | It reads as a form field | A solid tint pill with bold text |
| A description sentence under a title | The speaker says it | Nothing |
| Timings, caveats, or notes in the footer | Meta information distracts the audience | Title and page number only |

## Components

Each one is in `assets/deck-template.html`.

**Number row** (cover). Two or three large values with a short label under each, separated by thin vertical lines. Use it for the bottom line.

**Fan** (one to many, many to one). One label, curved links, a list of labels. It shows "one route does twelve things" or "four things become one" without a sentence. The template has a small `fan()` function that draws it as inline SVG. Put a large count above it.

**Pairs** (before → after). A grid with the current thing on the left in `--old`, an arrow, and the proposed thing on the right in `--new`. Thin lines between rows. This is the main proof component.

**Rules with examples.** A solid number, a heading, then a labelled `BEFORE` line and `AFTER` line in mono. Two columns, so each example stays on one line.

**Stepper** (a sequence). Solid numbered dots on one thin line. Under each dot: the step name, then the concrete call, command, or artefact for that step. Add `BEFORE` and `AFTER` lines when the point is that the steps stay and the names change.

**Topology or tree** (structure, blast radius). Hand-written inline SVG: thin dark outlines for nodes, `--line` links, one highlight area in a tint, one dashed outline for a scope. Label the consequence next to the shape ("1 customer", "all customers on the port").

**Timeline.** One axis of small dots, then one row for each case with solid dots or a bar on the same axis. Good for "which time range does each option select".

**Table with range bars** (cost, effort, impact). No outer border. Thin row lines, a heavy line above the total. Put the rate for each unit in a tint pill. Show the range as a bar on a shared scale. Do not add a column that only repeats the bar as numbers. Make assumption values editable inputs that recalculate the total.

**Callout.** One bold sentence with a bare solid icon in front: a lightbulb for a key point, a warning triangle for a risk, a question mark for a question to the audience. At most two on a screen.

**Closing.** Left: next actions as a short numbered list. Right: a large "Q&A" and one closing line.

## Diagrams

- Draw with inline SVG. Keep text in the SVG at 12.5–13.5px and use the same two fonts.
- One idea for each diagram. If it needs a legend, it shows too much.
- Use `--old` and `--new` only with their meaning. Everything else is `--ink` or `--line`.
- A shape that carries meaning needs a text label next to it. Colour alone is not enough.

## Checking the result

When a headless browser is available, capture each slide at 1280 × 720 and look at it. Check these first:

- Text that runs under the footer.
- A mono line that wraps where it must stay on one line. Shorten the text or widen the column.
- A utility class that changed alignment in a place you did not intend.
- The file with the network off: it must look the same.
