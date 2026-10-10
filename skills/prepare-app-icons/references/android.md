# Android icons

Snapshot checked **2026-10-10**. Reopen:

- [Adaptive icons](https://developer.android.com/develop/ui/compose/system/icon_design_adaptive).
- [AdaptiveIconDrawable](https://developer.android.com/reference/android/graphics/drawable/AdaptiveIconDrawable) for viewport and safe-zone behavior.
- [Create app icons in Android Studio](https://developer.android.com/studio/write/create-app-icons) for resource packaging.
- [Google Play listing icon specifications](https://developer.android.com/distribute/google-play/resources/icon-design-specifications) when listing assets are in scope.

## Launcher composition

Provide independent background and foreground layers, each representing
**108 × 108 dp**. Keep the background edge-to-edge and the essential logo in the
central **66 dp** safe region. The **outer 18 dp** on each side supports masking
and motion, not essential details. The guide recommends a nominal 48–66 dp logo.
Leave masks and outer shadows to the launcher. Supply a monochrome layer for
controlled themed-icon rendering; automatic theming on newer releases is not a
substitute for reviewing the brand's silhouette.
[Adaptive icon guidance](https://developer.android.com/develop/ui/compose/system/icon_design_adaptive).

Judge the actual contour, including corners, rather than just its bounding box.
The helper conservatively fits all visible foreground pixels inside a centered
66 dp circle. Dense square marks therefore use a smaller bounding box than round
marks. Review optical size against the official grid and native previews.

The static launcher viewport is the central 72 dp of the 108 dp layer. Crop that
viewport before mask previews, and check motion in a launcher when available.
[AdaptiveIconDrawable](https://developer.android.com/reference/android/graphics/drawable/AdaptiveIconDrawable).

## Resources

Use density-aware layers: 108/162/216/324/432 px for mdpi through xxxhdpi.
The helper exports those bitmaps, adaptive XML in `mipmap-anydpi-v26`, optional
monochrome XML in `mipmap-anydpi-v33`, and 48/72/96/144/192 px legacy icons.
Keep the API 26 version when adding the API 33 variant. Use compileSdk 33+ for
monochrome XML. Prefer existing vector drawables when the artwork supports them;
a normal SVG file is not an Android VectorDrawable.
[Android Studio resource guidance](https://developer.android.com/studio/write/create-app-icons).

Inspect existing manifest references before choosing `ic_launcher` or round-icon
names. Match `android:icon`; provide a round alias only if the project uses it.
Themed artwork is an alpha silhouette, not a grayscale photograph of a flat tile.

## Optional Play listing

A Play listing icon is separate from the adaptive launcher layers: **512 × 512
px**, **32-bit PNG**, **sRGB**, at most **1024 KB**, full square, with system-applied
outer rounding and shadow. The helper exports opaque RGBA for this asset and
checks its byte size. Do not resize the padded adaptive layer into the listing.
[Play specifications](https://developer.android.com/distribute/google-play/resources/icon-design-specifications).
