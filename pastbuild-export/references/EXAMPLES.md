# Past Build Export Examples

Real project examples that showcase how to write compelling feature-focused sections. Each example demonstrates a different project type and highlights the key patterns: personal voice, quantified impact, problem-first framing, and technical reasoning.

## SaaS Dashboard

```json
{
  "version": 1,
  "name": "MetricFlow Analytics",
  "description": "A real-time analytics dashboard helping SaaS teams monitor key metrics without switching between tools.",
  "projectDate": "2026-02-01",
  "sections": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Real-time data pipelines over WebSocket",
      "subtitle": "Built to handle 10K+ concurrent connections without dropping updates - I learned the hard way that polling just doesn't cut it for live dashboards.",
      "order": 0,
      "media": []
    },
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
      "title": "Drag-and-drop widget customization",
      "subtitle": "Users can compose their own view by dragging widgets onto a canvas - I used a grid-based layout system to make positioning intuitive yet responsive.",
      "order": 1,
      "media": []
    },
    {
      "id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
      "title": "Multi-tenant RBAC with granular permissions",
      "subtitle": "Each organization gets complete isolation - I implemented row-level security at the database level rather than application level for true data separation.",
      "order": 2,
      "media": []
    },
    {
      "id": "d4e5f6a7-b8c9-0123-defa-456789012345",
      "title": "PDF and scheduled email reports",
      "subtitle": "Executives need data in their inbox, not just in the app - I chose Puppeteer for pixel-perfect PDF generation over HTML-to-PDF libraries.",
      "order": 3,
      "media": []
    }
  ],
  "links": [
    { "id": "l1", "text": "Live Demo", "url": "https://metricflow.example.com" },
    { "id": "l2", "text": "GitHub", "url": "https://github.com/username/metricflow" }
  ],
  "exportedAt": "2026-02-12T01:30:00.000Z"
}
```

## Developer Tool / CLI

```json
{
  "version": 1,
  "name": "GitWip CLI",
  "description": "A developer tool that intelligently groups related git changes into sensible work-in-progress commits, so you can switch branches without losing context.",
  "projectDate": "2026-01-15",
  "sections": [
    {
      "id": "e1f2a3b4-c5d6-7890-abcd-ef1234567890",
      "title": "Smart commit grouping with semantic analysis",
      "subtitle": "Instead of asking 'what files did you change?', it analyzes imports and file patterns to auto-group related changes - this reduced our team's WIP commit noise by 70%.",
      "order": 0,
      "media": []
    },
    {
      "id": "f2a3b4c5-d6e7-8901-bcde-f23456789012",
      "title": "Cross-branch stash management",
      "subtitle": "I built this after losing work twice when stashing on one branch and applying on another - it tracks stash context so nothing ever gets applied to the wrong branch.",
      "order": 1,
      "media": []
    },
    {
      "id": "g3a4b5c6-e7f8-9012-cdef-345678901234",
      "title": "VS Code and Neovim extensions",
      "subtitle": "Developers shouldn't leave their editor to use version control - both extension surfaces WIP status inline, right where the code lives.",
      "order": 2,
      "media": []
    },
    {
      "id": "h4b5c6d7-f8a9-0123-defa-456789012345",
      "title": "Optimized for monorepos with millions of files",
      "subtitle": "Standard git status is too slow in large repos - I implemented a Rust-based status scanner that cuts status time from 8s to 200ms in our main monorepo.",
      "order": 3,
      "media": []
    }
  ],
  "links": [
    { "id": "l1", "text": "npm Package", "url": "https://npmjs.com/package/gitwip" },
    { "id": "l2", "text": "Documentation", "url": "https://gitwip.dev/docs" }
  ],
  "exportedAt": "2026-02-12T01:30:00.000Z"
}
```

## Open Source Library

```json
{
  "version": 1,
  "name": "React Context Store",
  "description": "A 2KB state management library that brings Redux's developer experience to React's built-in Context API - no boilerplate required.",
  "projectDate": "2026-01-20",
  "sections": [
    {
      "id": "i5c6d7e8-a9b0-1234-defa-567890123456",
      "title": "Minimal bundle size with zero dependencies",
      "subtitle": "I stripped everything non-essential - the core is just 2KB gzipped, so it fits even in performance-critical landing pages where every kilobyte matters.",
      "order": 0,
      "media": []
    },
    {
      "id": "j6d7e8f9-b0c1-2345-efab-678901234567",
      "title": "Redux DevTools out of the box",
      "subtitle": "Developers shouldn't need to configure middleware just to time-travel debug - I bundled Redux DevTools connection so it works instantly on first import.",
      "order": 1,
      "media": []
    },
    {
      "id": "k7e8f9a0-c1d2-3456-fabc-789012345678",
      "title": "Full TypeScript inference without generics",
      "subtitle": "Most typed state libraries require boilerplate generics - I designed the API so types flow automatically from your initial state, no annotations needed.",
      "order": 2,
      "media": []
    },
    {
      "id": "l8f9a0b1-d2e3-4567-bcde-890123456789",
      "title": "Selective re-rendering via subscription tuning",
      "subtitle": "Fine-grained selectors prevent unnecessary renders - I benchmarked several approaches and settled on a subscription model that's 3x faster than naive Context usage.",
      "order": 3,
      "media": []
    }
  ],
  "links": [
    { "id": "l1", "text": "npm", "url": "https://npmjs.com/package/react-context-store" },
    { "id": "l2", "text": "Star on GitHub", "url": "https://github.com/username/react-context-store" }
  ],
  "exportedAt": "2026-02-12T01:30:00.000Z"
}
```

## Technical Proof of Concept

```json
{
  "version": 1,
  "name": "DiffReview AI",
  "description": "An experimental tool exploring how LLMs can review pull request diffs with contextual understanding - built to understand code, not just match patterns.",
  "projectDate": "2026-02-05",
  "sections": [
    {
      "id": "m9a0b1c2-e3f4-5678-cdef-901234567890",
      "title": "Diff-aware prompting for contextual understanding",
      "subtitle": "Instead of feeding entire files to the LLM, I extract only changed functions and their callers - this reduced token usage by 80% while improving review relevance.",
      "order": 0,
      "media": []
    },
    {
      "id": "n0a1b2c3-f4e5-6789-defa-012345678901",
      "title": "Custom rule engine for team standards",
      "subtitle": "Every team has different conventions - I built a JSON-configurable rule system so you can teach the AI your patterns without touching code.",
      "order": 1,
      "media": []
    },
    {
      "id": "o1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Comment threading with human-in-the-loop",
      "subtitle": "AI suggestions are starting points, not verdicts - I designed a discussion flow where developers can accept, reject, or iterate on each AI comment.",
      "order": 2,
      "media": []
    },
    {
      "id": "p2c3d4e5-f6a7-8901-bcde-f23456789012",
      "title": "GitHub Actions integration for automated PR reviews",
      "subtitle": "Review should happen before human eyes see the PR - the Action runs automatically on each push and posts comments within minutes, not hours.",
      "order": 3,
      "media": []
    }
  ],
  "links": [
    { "id": "l1", "text": "GitHub Action", "url": "https://github.com/marketplace/actions/diffreview-ai" }
  ],
  "exportedAt": "2026-02-12T01:30:00.000Z"
}
```

## Key Patterns for Writing Compelling Sections

These examples demonstrate techniques that make project descriptions memorable and informative:

**Personal voice**: "I built this after...", "I learned the hard way...", "I chose..." shows ownership and makes the story authentic.

**Quantified impact**: Specific numbers ("70% reduction", "8s to 200ms", "80% token savings") give concrete evidence of value.

**Problem-first framing**: Acknowledge the pain before showing the solution. "Executives need data in their inbox" before explaining the PDF feature.

**Technical reasoning embedded**: Tool choices explained, not just listed. "I chose Puppeteer for pixel-perfect PDF generation" tells readers something about your decision-making.

**Storytelling hooks**: Origin stories like "I lost work twice" create memorable connections that plain feature descriptions cannot.
