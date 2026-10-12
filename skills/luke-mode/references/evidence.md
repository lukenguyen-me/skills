# PR evidence

The reviewer of an autopilot PR sees only the diff and the PR body. Evidence
lets them judge the outcome without checking out and running the branch: show
the change working, before and after.

## Plan the evidence

Classify each surface the change touches. Plan one capture per affected screen,
state, viewport, and theme.

| Changed surface | Evidence | Before |
| --- | --- | --- |
| Visual UI: layout, style, copy, a new screen | Screenshots | Base build, same screen and state |
| Interaction: flow, navigation, animation, gesture | Recording, published as a GIF | Base recording when the flow exists |
| CLI or terminal output | Output in a code block | Same command on the base |
| API, data, or backend behavior | Request and response, or the test that fails then passes | The failing run |
| Refactor of a UI | Screenshots plus a pixel diff showing no change | Base screenshots |
| No observable surface | Check and test results | None |

A new screen has no before state: show the entry point that leads to it.
Responsive or theme changes add a phone viewport or dark theme to the plan.

## Capture the before state first

The before state exists only until the first edit. Capture it from the base
before changing code. When edits already exist (a resumed run, a whole-spec run
from its pinned SHA), build the base in a temporary worktree
(`git worktree add <tmp> <base-sha>`), run it on a free port or device, capture,
and remove the worktree.

Write down a capture recipe: URL or deep link, account and seed data, viewport
or device, theme, and the steps that reach the state. The after capture replays
the same recipe, so the pair differs only by the change. Keep captures in a
temporary directory outside the repository (`EV=$(mktemp -d)`); they are never
committed to the PR branch.

## Capture routes

Capture commands do not navigate. Reach the state first through a URL, deep
link, launch argument, test hook, or scripted steps. Read the project's
instructions for starting the app, seeding data, and signing in. Use fixtures
and demo accounts; real user data stays out of evidence.

**Web: `agent-browser`.** Run `agent-browser <command> --help` for options.

```sh
agent-browser open http://localhost:3000/settings
agent-browser set viewport 1280 800              # phone: set viewport 390 844
agent-browser screenshot "$EV/settings-after.png"   # --full for the whole page
agent-browser diff screenshot --baseline "$EV/settings-before.png" -o "$EV/settings-diff.png"
agent-browser record start "$EV/checkout.webm" --cursor   # drive the flow, then:
agent-browser record stop
agent-browser close
```

Pass `--color-scheme dark` for dark theme. Recording needs `ffmpeg`.

**iOS Simulator.** Build and install with the project's scheme or scripts.

```sh
xcrun simctl status_bar booted override --time 9:41 --batteryState charged --batteryLevel 100
xcrun simctl openurl booted 'myapp://settings'
xcrun simctl io booted screenshot "$EV/settings-after.png"
xcrun simctl io booted recordVideo --codec h264 "$EV/flow.mp4"   # stop with SIGINT
```

**Android emulator or device.**

```sh
adb shell settings put global sysui_demo_allowed 1
adb shell am broadcast -a com.android.systemui.demo -e command clock -e hhmm 0941
adb shell am start -a android.intent.action.VIEW -d 'myapp://settings'
adb exec-out screencap -p > "$EV/settings-after.png"
adb shell screenrecord --time-limit 15 /sdcard/flow.mp4 && adb pull /sdcard/flow.mp4 "$EV/"
```

**Other surfaces.** Use the project's UI automation for desktop apps, or
`screencapture -l <window-id>` on macOS. Capture terminal output as text.

A missing tool, simulator, or credential makes that capture a gap; record the
reason and continue with the remaining plan.

## Inspect every capture

Look at each image and GIF yourself before it leaves the machine:

- **Correct**: it shows the planned state, and the after state meets the
  acceptance criteria. A capture that reveals a defect sends you back to the
  work.
- **Comparable**: the pair differs only by the change. Review every changed
  region in the pixel diff and explain or fix each unintended one.
- **Safe**: published evidence is permanent. It shows no secrets, tokens,
  personal data, or private URLs. Recapture with fixture data.

## Shrink

Published evidence stays forever, so keep each file small:

- Screenshots: PNG with the longest side at most 1600 px (`sips -Z 1600 <file>`).
- Recordings: at most 15 seconds. Convert to a GIF so it plays inline:

  ```sh
  ffmpeg -i flow.webm -vf "fps=10,scale=720:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" -loop 0 flow.gif
  ```

  Keep each GIF under 5 MB by trimming, lowering `fps`, or narrowing `scale`.
  Publish the source video too when motion detail matters; it shows as a link.

## Publish

GitHub has no API to upload images to a PR. After pushing the PR branch, run
the bundled script from the project repository (`<luke-mode>` is this skill's
installation directory):

```sh
python3 <luke-mode>/scripts/publish_evidence.py "$EV/settings-before.png" "$EV/settings-after.png"
```

It commits the files to the hidden ref `refs/evidence/<branch>` and prints each
file's URL as JSON. Clones skip hidden refs, so evidence never weighs on the
repository's users, and only people who can read the repository can open it.
Republishing adds to the ref; earlier links keep working. Give every file a
unique, descriptive name such as `settings-after-dark.png`. The script refuses
files over 10 MB. For a remote outside github.com, it stops; report the local
capture paths in the handoff and in the PR body's gaps.

## Fill the Evidence section

The `pr` skill owns the body. Fill its Evidence section from this plan:

```markdown
## Evidence

Settings, 1280×800, light, seeded demo account.

| Before | After |
| --- | --- |
| ![Settings before](<url>) | ![Settings after](<url>) |

![Checkout flow](<gif-url>) ([full video](<video-url>))

Not captured: Android layout (no emulator in this environment).
```

Caption each pair with its recipe in one line. Name each planned capture that
did not happen as `Not captured: <what> (<reason>)`.

Done when every planned capture is published in the PR body or named there as
a gap.
