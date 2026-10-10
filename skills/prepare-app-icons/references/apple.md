# Apple app icons

Snapshot checked **2026-10-10**. Open these sources again for a new task:

- [App icons — Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/app-icons).
  If the page exposes only a JavaScript notice, read its
  [official documentation JSON](https://developer.apple.com/tutorials/data/design/human-interface-guidelines/app-icons.json).
- [Creating your app icon using Icon Composer](https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer).
- [Configuring an icon using an asset catalog](https://developer.apple.com/documentation/xcode/configuring-your-app-icon).
- [Apple Design Resources](https://developer.apple.com/design/resources/) for the current production grids.

## Choose the platform and delivery path

Current HIG layout canvases:

| Target | Canvas | System mask | Delivery |
| --- | --- | --- | --- |
| iOS / iPadOS / macOS | 1024 × 1024 | Rounded square | Icon Composer or applicable catalog |
| watchOS | 1088 × 1088 | Circle | Icon Composer or applicable catalog |
| visionOS | 1024 × 1024 | Circle | Xcode layered image stack |
| tvOS | 800 × 480 | Rounded rectangle | Xcode parallax image stack |

These are design canvases, not an exhaustive catalog slot list. Read the actual
Xcode target: legacy watch catalogs and macOS size variants use different slots.
The helper's catalog is for iOS/iPadOS only.

Keep imported backgrounds opaque and edge-to-edge, foreground layers unmasked,
and primary artwork centered. Prefer vectors; outline text. Use Apple's grids
to judge placement. A circle or rounded-square mask belongs to the system.
These design rules come from the [HIG](https://developer.apple.com/design/human-interface-guidelines/app-icons).

## Icon Composer

Export individual foreground SVG/PNG layers with matching canvases. Configure
simple background fills and dynamic effects in Icon Composer. Review default,
dark, clear, and tinted appearances, retaining the same core features. Save the
native `.icon` file and test it through Xcode. Adding it replaces the catalog
delivery path; Xcode derives earlier-system imagery from it. Confirm that this
is appropriate for the app's existing icon behavior.
[Icon Composer instructions](https://developer.apple.com/documentation/xcode/creating-your-app-icon-using-icon-composer).

## Flat catalogs

For an iOS/iPadOS Single Size catalog, export a square 1024-pixel default PNG
with an opaque background and no alpha channel. Preserve an existing All Sizes
catalog's required slots instead of replacing its schema blindly. Dark catalog
variants can have transparent backgrounds; tinted variants use grayscale.
Keep those rules separate from default-icon opacity and from Composer layers.
[Catalog instructions](https://developer.apple.com/documentation/xcode/configuring-your-app-icon).

The helper's 78% logo fit is an adjustable composition starting point. It is not
an Apple requirement. Native appearance previews and platform grids determine
whether a particular logo needs a different scale or position.
