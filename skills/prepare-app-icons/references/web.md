# Web favicons and install icons

Snapshot checked **2026-10-10**. Reopen sources for the applicable surfaces.

## Browser tabs and search

HTML declares icons with `rel="icon"`, using `type`, `sizes`, and optionally
`media` to select variants. `sizes="any"` describes a scalable asset. HTML does
not prescribe one universal raster size set.
[HTML Living Standard](https://html.spec.whatwg.org/multipage/links.html#rel-icon).

Practical default exports: a multi-resolution ICO with 16/32/48-pixel images and
PNG files at 16/32/48/96 pixels. Inspect the mark at actual tab sizes. Retain an
existing vector favicon when useful; add an SVG declaration only if that SVG is
actually supplied and verified. A raster image embedded in SVG gains no detail.

Current Google Search guidance requires a square favicon of at least 8 pixels
and recommends one **larger than 48 pixels**. It no longer states that dimensions
must be multiples of 48. Link a stable 96-pixel PNG from the home page and allow
crawling when Search support matters. SVG can serve browsers, but the current
Search format list calls for a raster/ICO fallback.
[Google Search favicon guidance](https://developers.google.com/search/docs/appearance/favicon-in-search).

## Apple touch icon

For iOS Home Screen bookmarks, supply `apple-touch-icon.png` and its explicit
`rel="apple-touch-icon"` declaration. The helper uses an opaque unmasked
180-pixel PNG. Apple's archived Safari guide documents 180/167/152-pixel
variants; it is historical guidance, so verify behavior on the supported Safari
release rather than presenting the archive as a newly maintained standard.
[Safari Web Content Guide](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariWebContent/ConfiguringWebApplications/ConfiguringWebApplications.html).

## Optional PWA

Use separate `purpose: "any"` and `purpose: "maskable"` files. For maskable icons,
keep essential artwork inside the central circle with radius **40% of the
shorter image side**: its diameter is 80%, not a central 80% square. An opaque
edge-to-edge background avoids a user-agent-chosen fill.
[Web Application Manifest](https://www.w3.org/TR/appmanifest/#icon-masks).

The helper's 192/512-pixel exports are practical defaults, not a universal W3C
size requirement. Merge its icons fragment into the app's existing manifest;
preserve names, start URL, scope, and display mode. Adjust snippets for base paths
or framework metadata conventions and verify referenced files exist.
