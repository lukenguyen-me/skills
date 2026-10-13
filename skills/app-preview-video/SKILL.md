---
name: app-preview-video
description: Produce an app preview video with motion, captions, music, and sound effects from an app repository. Delivers App Store and Google Play cuts that meet each store's specification, plus a landing-page hero cut. Use for a store preview, promo video, demo video, or landing-page video of a mobile app.
---

# App preview video

Turn real app footage into a 15–30 second preview that converts. One
`plan.json` drives three cuts from the same timeline: App Store, Google Play,
and a landing-page hero. The render engine is an HTML overlay page captured
frame by frame through Chrome, then encoded by ffmpeg. No npm install.

Requirements: `node` ≥ 22, `ffmpeg`/`ffprobe`, and `agent-browser` (or any
Chrome started with `--remote-debugging-port`). Resolve this skill's files
relative to its installed directory.

## 1. Resolve scope and tools

Work in `<app repo>/preview/` unless the user or repository names another
output directory. Reuse an existing `plan.json` there; a saved plan is the
source of truth for scenes, copy, and cues, so change only what the user asks.

Confirm the tools above are installed. Read
[references/store-specs.md](references/store-specs.md) for the current
specifications and content rules; it carries a check date, so verify against
Apple and Google when it is older than a few months or the user is about to
submit. Record which cuts are in scope: default to `appstore`, `googleplay`,
and `landing`.

## 2. Storyboard

Find the app's three to five core benefits from source: screens, models,
onboarding, paywall, store metadata, README. Each scene shows one benefit as
an action the viewer watches happen (a tap that completes something), with a
caption of at most five words that reads while muted. Order the scenes with the
strongest reason to download first; the first second must already show real
app use, so no logo or splash opens the video.

Write the scenes into `plan.json` using the schema in
[references/plan.md](references/plan.md). Target 20–28 seconds total including
a 3-second end card. Let the user revise the scene list and copy before
recording; keep approved wording verbatim.

## 3. Capture footage

Store cuts need real screen recordings; Apple rejects anything else. Read
[references/capture.md](references/capture.md), then record one clip per
scene from a simulator, emulator, or device, trimmed to the scene's duration
and in the plan's screen resolution and orientation. Register each as
`scenes[].clip`.

When no build or device is available, draw mock screens in a `screens.js`
(contract in `references/plan.md`) and say so in the handoff: a mock cut is a
storyboard or landing-page asset, never a store upload.

Completion: every scene has an inspected clip or a declared mock.

## 4. Score the timeline

Place sound cues on the moments the footage shows: `tap` on touches, `check`
or `toggle` on state changes, `chime`/`sparkle` on a success, `whoosh` on
scene cuts, `notif` for a notification, `impact` on the end card. Bundled
sounds and music are in `assets/audio/` and carry no licensing risk;
`scripts/make_audio.py` regenerates them. Use the app's own licensed audio
only when the user confirms rights for every store territory.

## 5. Build

```bash
node <skill>/scripts/build.mjs all --plan preview/plan.json --out preview/out
```

`prepare` writes one `preview/out/preview/<cut>.html` per cut; open it in a
browser to scrub the timeline before a full capture. `capture` screenshots
every frame through agent-browser and writes `work/<cut>.video.mp4`.
`encode` mixes audio, encodes each store preset into `final/`, and prints a
specification checklist; a failed check exits non-zero.

Capture runs at roughly 10 frames per second, so iterate on one cut
(`--cut appstore`) and widen when the timing is right.

## 6. Inspect and deliver

View frames from the final files at scene starts, each cue, and the end card
(`work/<cut>.f<frame>.png` samples every 5 s are written during capture). Reject
clipped captions, mistimed cues, footage that stalls, or any text naming a
price, date, ranking, or a call to action in a store cut. Fix the plan and
rebuild the affected cut.

Report the final paths, the checklist result per cut, the poster frame, the
`.srt` captions for the YouTube upload, and which scenes use mocks. Upload to
the stores is a separate request.
