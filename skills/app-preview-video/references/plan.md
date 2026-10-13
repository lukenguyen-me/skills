# plan.json

One plan drives every cut. Paths are relative to the plan file. Durations are
frames at `fps`. The complete example is `examples/ripple/plan.json`.

```jsonc
{
  "app": {"name": "Ripple", "tagline": "Small habits. Big change.", "category": "Habit tracker", "icon": "icon.png"},
  "brand": {"primary": "#5B5BF7", "primary2": "#9B6BFF", "accent": "#1FC79A", "ink": "#11142A", "bg": "#F4F5FB"},
  "fps": 30,                      // ≤ 30 for the App Store
  "crossfade": 10,                // dissolve length between scenes, frames
  "screen": {"w": 886, "h": 1920},// footage resolution: the App Store canvas
  "mock": "screens.js",           // optional; mock screens for scenes without a clip
  "scenes": [
    {
      "id": "today", "dur": 210,
      "clip": {"src": "captures/today.mp4", "in": 0.4},   // real footage; `in` = start offset in seconds
      "caption": "Build habits that stick",               // store cuts, ≤ 5 words, muted-friendly
      "headline": ["Build habits", "that stick."],        // landing cut, two lines
      "sub": "One tap to check in.",                      // landing cut
      "chip": {"text": "🎉  Perfect day", "at": 88}       // landing callout, frame within the scene
    }
  ],
  "end": {"dur": 90, "disclosure": "Free to download · Optional Premium subscription", "stores": ["App Store", "Google Play"]},
  "music": {"src": "music", "vol": 0.42},                 // name or path; omit for silence under the cues
  "cues": [
    {"at": 20, "sfx": "tap", "vol": 0.5},
    {"at": 222, "sfx": "tick", "vol": 0.16, "repeat": 10, "every": 6}   // ten ticks, six frames apart
  ],
  "outputs": ["appstore", "googleplay", "landing"]
}
```

## Cuts

| id | Canvas | Layout | Encode |
| --- | --- | --- | --- |
| `appstore` | 886×1920 | store | H.264 High 4.0, CBR 11 Mbps, AAC 256k |
| `appstore-ipad` | 1200×1600 | store | same, level 4.1 |
| `appstore-landscape` | 1920×886 | store | same |
| `googleplay` | 1080×1920 | store | H.264 CRF 16, AAC 256k, plus `.srt` |
| `landing` | 1920×1080 | landing | H.264 CRF 20 + muted VP9 `.webm` + poster `.jpg` |

An output may be an object to override fields: `{"id": "landing", "w": 1600, "h": 900}`.

**store** layout: footage fills the canvas, scenes dissolve, one caption per
scene above the tab bar, end card with app icon, name, tagline, and
`end.disclosure`. **landing** layout: dark gradient background, 3D phone
mockup at `landing.phoneX` (default 1180) and `landing.phoneScale` (0.43),
kinetic headline, chips, end card with store buttons. The end card uses
`app.icon` when given; otherwise `window.APP_ICON` from the mock file.

Footage at a different resolution than `screen` is scaled to cover the canvas,
so match `screen` to the recording and the recording to the store canvas.

## Mock screens contract

`mock` names a script loaded into the overlay page. It defines
`window.SCREENS = {<scene id>: (f, w, h) => html}`, returning an HTML string
for frame `f` of that scene on a `w`×`h` canvas; a scene with a `clip` ignores
its mock. Helpers are on `window.R`: `interpolate(v, [in...], [out...], easing)`,
`spring(frame, {damping, stiffness, mass})`, `pop(f, at, config)` (spring that
starts at `at`), `ease(f, a, b, from, to, easing)`, `random(seed)`, `css(style)`,
`div(style, children)`, `esc(text)`. Style objects follow React conventions
(camelCase, numbers in px). Everything must derive from `f` alone: no timers,
no `Date`, no `Math.random`.

`examples/ripple/screens.js` is a complete reference with a status bar, tab
bar, cards, touch hotspots, and confetti.

## Audio

Sound names resolve from the plan directory, `audio_dir`, then the skill's
`assets/audio/`, with or without extension. Bundled: `music` (25 s, 120 BPM,
C major, ends on a chord at 22 s), `tap`, `check`, `toggle`, `tick`, `chime`,
`sparkle`, `stamp`, `whoosh`, `notif`, `impact`. Regenerate or extend with
`python3 scripts/make_audio.py <dir>` (needs numpy and scipy).

The mix is music + cues → `amix` → `loudnorm` to −16 LUFS, −1.5 dBTP, then
AAC 256 kbps 48 kHz stereo in every cut. A video longer than the music fades
to silence after it ends; supply a longer `music.src` for timelines over 25 s.

## Build commands

```bash
node scripts/build.mjs prepare --plan plan.json --out out      # preview pages with a scrubber
node scripts/build.mjs capture --plan plan.json --out out --cut appstore
node scripts/build.mjs encode  --plan plan.json --out out [--dry-run]
node scripts/build.mjs all     --plan plan.json --out out
```

`capture` launches a named agent-browser session (`apv-<pid>`), connects over
CDP, sets the viewport to the cut size at scale 1, waits for `window.ready`
(clips decoded), then calls `window.seek(f)` and screenshots each frame into
an ffmpeg pipe (`work/<cut>.video.mp4`, CRF 8). Pass `--cdp ws://…` to use a
Chrome you started yourself. Sample frames every 5 s land in `work/<cut>.f<frame>.png`.

`encode` writes `work/audio.wav` and `final/<app>-<cut>-<w>x<h>.*`, then
prints the checklist (resolution, codec and level, fps, duration, audio,
size, App Store bit rate). Exit code 2 means a check failed.
