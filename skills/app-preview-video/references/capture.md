# Capture footage

Read before recording. The store cuts show this footage full-bleed, so each
clip must be clean, at the right size, and show the scene's action within
its duration.

## Find the route to each scene

Inspect the repository for launch commands, demo accounts, seed data, deep
links, UI tests, Maestro/Detox/XCUITest flows, and simulator or emulator
controls. Prefer a working project workflow to drive the UI; a raw recording
command does not navigate. Plan per scene:

```text
Scene: today
Launch: <build/run command> on <device id>
Data: seeded demo account with four habits, two incomplete
Navigate: deep link ripple://today
Action: tap "Meditate" at ~0.7 s, tap "Read 20 pages" at ~2.0 s, wait for the confetti
Appearance: light mode, en-US, portrait, status bar 9:41 full battery
Output: captures/today.mp4, trimmed to 7.0 s
```

## Record

iOS simulator (produces the simulator's native resolution; pick a device whose
screen matches the plan, e.g. iPhone 16 Pro Max for 886×1920 after scaling):

```bash
xcrun simctl status_bar <udid> override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4 --wifiBars 3
xcrun simctl io <udid> recordVideo --codec h264 --mask ignored captures/today-raw.mp4   # Ctrl-C to stop
```

Android emulator or device:

```bash
adb -s <serial> shell settings put global sysui_demo_allowed 1
adb -s <serial> shell am broadcast -a com.android.systemui.demo -e command clock -e hhmm 0941
adb -s <serial> shell screenrecord --bit-rate 20000000 --time-limit 30 /sdcard/today-raw.mp4
adb -s <serial> pull /sdcard/today-raw.mp4 captures/
```

A physical iPhone records through QuickTime (File › New Movie Recording with
the device as camera) or the Control Center screen recorder; AirDrop the file.

Drive the UI during the recording with the project's automation where it
exists (Maestro `maestro test flow.yaml`, XCUITest, `adb shell input tap`),
so every take has the same timing. Wait for observable readiness before each
action; the preview must not show spinners or empty states.

## Trim and conform

Trim each take to its scene, scale to the plan's `screen`, and strip audio:

```bash
ffmpeg -y -i captures/today-raw.mp4 \
  -vf "fps=30,tpad=stop_mode=clone:stop_duration=5,trim=start=1.20:duration=7.0,setpts=PTS-STARTPTS,scale=886:1920:force_original_aspect_ratio=increase,crop=886:1920" \
  -an -c:v libx264 -crf 10 -pix_fmt yuv420p captures/today.mp4
```

Simulator and `adb screenrecord` takes are variable frame rate: no frames are
written while the screen is still. Do not trim with an input seek (`-ss` before
`-i`): it jumps to the next written frame and drops the still part. `fps=30`
fills the gaps with repeated frames, `tpad` holds the last frame so a take that
ends on a still screen keeps its full length, and `trim` then cuts exact
seconds. Check the result with `ffprobe` before registering the clip.

Set `scenes[].dur` to `clip length × fps` (7.0 s → 210 frames) plus the
crossfade, or shorter to cut early. `clip.in` offsets the start without
re-encoding. A clip shorter than the scene freezes on its last frame.

Inspect the first, middle, and last frame of each clip before registering it:

```bash
ffmpeg -y -ss 0 -i captures/today.mp4 -frames:v 1 captures/today-first.png
```

Retake clips with loading states, debug overlays, permission dialogs, wrong
appearance, or a status bar that was not normalized. Keep raw takes outside
`final/`.

## Timing cues from footage

Note the second of each tap and state change while reviewing the clip
(`ffplay`, or step frames in the preview page's scrubber), convert to frames
(`seconds × fps`), add the scene's start frame, and write the cue. A cue that
lands within ±2 frames of the visual change reads as synchronized.
