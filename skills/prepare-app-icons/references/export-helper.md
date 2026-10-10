# Export helper

Requires Python 3.10+ and Pillow with ImageCms support. Use the project's existing
environment or an isolated environment to install Pillow when needed.
The script accepts Pillow-readable raster files. Rasterize SVG/PDF through an
available native renderer first, and keep the vector original.

From this installed skill directory:

```sh
python3 scripts/export_icons.py inspect /path/to/logo.png
python3 scripts/export_icons.py export \
  --source /path/to/logo.png --source-kind logo \
  --background '#183153' --platforms apple android web \
  --out /path/to/output/app-icons \
  --guidelines /path/to/guideline-check.json
```

The output directory must be new. The script never replaces input files and
publishes the bundle after its checks pass. Use `--help` for all options.

For a finished opaque square icon, use `--source-kind flat-icon`. The flat icon
remains intact for Apple and touch-icon output. Add `--foreground` with a
transparent, separable logo for Android and Apple foreground handoff layers.
If unavailable, export Apple/web independently while resolving Android's source.
Use `--favicon-source` to supply an existing compact mark for browser icons.

Scale flags control compositions, not platform rules: `--apple-scale` defaults
to 0.78 and `--favicon-scale` to 0.9. Android fits the visible contour to a 66 dp
circle on a 108 dp canvas, with a conservative 4 dp resampling margin kept
consistent across densities. Favicon framing is
independent of that padding. Existing fully transparent padding on logos is
trimmed before composing; the helper expects a mark, not an already composed
108 dp Android layer.

Add `--monochrome-source` for an existing monochrome mark. Alternatively,
`--monochrome-from-alpha` preserves the color foreground's alpha as a candidate
silhouette; review internal details before accepting it. The flags are exclusive.
Add `--play-store` for the separate Play listing asset and `--pwa` for install
icons. These options require their corresponding platform in `--platforms`.

## Output

| Location | Purpose |
| --- | --- |
| `sources/` | Unchanged copies of supplied raster input files |
| `apple/AppIcon.appiconset/` | iOS/iPadOS Single Size default PNG and metadata |
| `apple/icon-composer-layers/` | Transparent 1024-pixel foreground and setup notes, when a foreground is available |
| `android/res/` | Adaptive XML, density-specific layers, legacy fallbacks, optional monochrome resources |
| `android/play-store-icon.png` | Optional separate listing image |
| `web/` | ICO, PNG favicons, touch icon, HTML snippet, optional PWA images and manifest icons fragment |
| `preview.png` | Approximate platform masks, Android safe region, and favicons on light/dark surfaces |
| `asset-report.json` | Input hashes, composition settings, warnings, files, and structural checks |
| `guideline-check.json` | Supplied source-check record, copied unchanged |

`apple/icon-composer-layers/` is a handoff, not a native `.icon` file. The helper
does not generate appearance variants, macOS/Watch catalogs, or tvOS/visionOS
stacks. Use their native workflow as described in [apple.md](apple.md).

Provide a guideline record made from sources actually read, for example:

```json
{
  "checked_at": "2026-10-10",
  "status": "verified",
  "platforms": {
    "android": {
      "urls": ["https://developer.android.com/develop/ui/compose/system/icon_design_adaptive"],
      "requirements": {"layer_dp": 108, "safe_region_dp": 66}
    }
  }
}
```

Include every requested platform in a real record. The helper records the
caller's evidence; it does not browse or authenticate that evidence. Without
`--guidelines`, the report marks current-guideline verification as pending.
Its defaults reflect this skill's 2026-10-10 snapshot. If current requirements
change, adapt the exporter or use native tooling before claiming compliance.

Warnings flag raster upscaling and missing monochrome/native appearance review.
The report separates structural checks from visual and native-tool checks, which
remain pending until the agent performs them.
