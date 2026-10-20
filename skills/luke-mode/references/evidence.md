# PR evidence

The reviewer of a PR Luke opens sees only the diff and the PR body. Evidence
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
(`git worktree add <tmp> <base-sha>`), run it on a free port or the
[shared device](#shared-devices), capture, and remove the worktree.

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

**iOS device or Simulator.** Claim a [shared device](#shared-devices), listing
connected physical devices first, then build and install with the project's
scheme or scripts. Address the device by UDID: `booted` is ambiguous while
another run has a device booted. `<luke-mode>` is this skill's directory.

```sh
DEV=$(python3 <luke-mode>/scripts/device_claim.py claim <phone-udid> <sim-udid-1> <sim-udid-2> --minutes 30 --label <task>)
```

A physical device builds with `-destination "id=$DEV"` and the project's
development signing team; a signing or install failure moves the run to the
next candidate. Drive it with `devicectl`:

```sh
xcrun devicectl device install app --device "$DEV" <build-dir>/MyApp.app
xcrun devicectl device simulate statusBar preset screenshot --device "$DEV"
xcrun devicectl device process launch --device "$DEV" --terminate-existing --payload-url 'myapp://settings' <bundle-id>
xcrun devicectl device capture screenshot --device "$DEV" --destination "$EV/settings-after.png"
xcrun devicectl device capture screen-record --device "$DEV" --duration 15 --destination "$EV/flow.mp4"
xcrun devicectl device simulate statusBar clear --device "$DEV"
python3 <luke-mode>/scripts/device_claim.py release "$DEV"
```

Dark theme is `xcrun devicectl device settings appearance --device "$DEV" --mode dark`;
read the current setting first with `device info appearance` and set it back.
A device that reports status bar override or screen recording as unsupported
(iOS 18 does) still takes screenshots. There, record a flow as one screenshot per
step and join them into the GIF (`ffmpeg -framerate 1 -i step-%02d.png ...`),
or record it on a simulator when the motion itself is the change.

A simulator boots and runs through `simctl`:

```sh
xcrun simctl boot "$DEV"   # skip when it is already booted
xcrun simctl status_bar "$DEV" override --time 9:41 --batteryState charged --batteryLevel 100
xcrun simctl openurl "$DEV" 'myapp://settings'
xcrun simctl io "$DEV" screenshot "$EV/settings-after.png"
xcrun simctl io "$DEV" recordVideo --codec h264 "$EV/flow.mp4"   # stop with SIGINT
python3 <luke-mode>/scripts/device_claim.py release "$DEV"
```

**Android device or emulator.** Claim a [shared device](#shared-devices),
listing connected phones (by adb serial) before AVDs (by name). A claimed AVD
starts unless it already runs in `adb devices`. Pass the serial to every `adb`
call with `-s`; the same commands drive a phone and an emulator.

```sh
DEV=$(python3 <luke-mode>/scripts/device_claim.py claim <phone-serial> Pixel_8_API_35 --minutes 30 --label <task>)
emulator -avd "$DEV" &   # an AVD only; skip when it is already running
S="$DEV"   # a phone; for an AVD, its emulator-NNNN serial from `adb devices`
adb -s "$S" shell settings put global sysui_demo_allowed 1
adb -s "$S" shell am broadcast -a com.android.systemui.demo -e command clock -e hhmm 0941
adb -s "$S" shell am start -a android.intent.action.VIEW -d 'myapp://settings'
adb -s "$S" exec-out screencap -p > "$EV/settings-after.png"
adb -s "$S" shell screenrecord --time-limit 15 /sdcard/flow.mp4 && adb -s "$S" pull /sdcard/flow.mp4 "$EV/"
adb -s "$S" shell am broadcast -a com.android.systemui.demo -e command exit
python3 <luke-mode>/scripts/device_claim.py release "$DEV"
```

Some vendor builds ignore demo mode; check the status bar in the capture.

**Other surfaces.** Use the project's UI automation for desktop apps, or
`screencapture -l <window-id>` on macOS. Capture terminal output as text.

A missing tool, device, or credential makes that capture a gap; record the
reason and continue with the remaining plan.

## Shared devices

Physical devices, simulators, and emulators are machine-global: every project
and worktree on the machine draws from one device pool. Prefer a physical
device: the app runs on the device's own hardware, so the Mac spends no memory
or CPU on a simulator, and the run sees real performance, camera, and sensors.
Captures, verification, and the scripts a task writes reuse the pool:

1. List the devices. Physical: `xcrun devicectl list devices --json-output -`
   (`hardwareProperties.reality` is `physical`) and `adb devices -l` (serials
   other than `emulator-*`). Virtual: `xcrun simctl list devices available --json`
   and `xcrun simctl list runtimes`, or `avdmanager list avd`.
2. Order the candidates: physical devices first, then booted simulators and
   emulators, then the rest on the newest installed runtime. `claim` skips the
   devices on the machine's skip list (`device_claim.py list` shows it), such
   as the user's personal phone; setup maintains it. A physical device
   is a candidate when it is paired and unlocked (`xcrun devicectl device info lockState`)
   or authorized (`device` in `adb devices`), and its OS meets the app's
   deployment target or `minSdk`. A plan that needs one model or screen size
   names it; otherwise every device of the form factor is a candidate (any
   iPad for an iPad app, any phone for a phone app).
3. Claim the first free candidate with
   [`device_claim.py`](../scripts/device_claim.py) before driving it.
   `hold <candidates> -- <command>` claims for one command; `claim --minutes N`
   then `release` spans several commands. A claimed device is taken: move to the
   next free candidate. Wait (`--wait-minutes N`) only when every candidate is
   claimed.
4. A physical device keeps its pairing, Developer Mode, accounts, and other
   apps across runs. Reset only the app under test:
   `xcrun devicectl device uninstall app --device <device> <bundle-id>`, or `adb -s <serial> shell pm clear <package>`. Restore every setting the run
   changed (status bar, appearance, demo mode) before release. Device-wide
   reset stays with the user: `devicectl device settings reset` erases the
   whole device and its pairing, so leave it unrun.
5. For a clean simulator or emulator, erase the claimed device:
   `xcrun simctl shutdown <device>` then `xcrun simctl erase <device>`, or
   `emulator -avd <name> -wipe-data`.
6. Use a simulator or emulator when the plan needs what no free physical device
   gives: a model, screen size, or OS version none of them has, a device-wide
   clean state, a `simctl`-only hook (`simctl push`, `simctl privacy`), or a
   second device while the physical ones are claimed.
7. Create a simulator or emulator only when no listed device fits the plan; a
   busy pool is a reason to wait. Name it after its device type and runtime
   (`iPhone 16 Pro`, `Pixel_8_API_35`), never after the project, and delete it when the task ends
   (`xcrun simctl delete <device>`, `avdmanager delete avd -n <name>`).
8. Scripts and project docs resolve the device at run time by name or by the
   rule in steps 1 and 2, skip claimed devices, and accept a name or UDID as an
   override (for example `--device`). A script claims with `--pid` set to its
   own process, or imports `claim_first`, so the claim ends when the script
   does. A hardcoded UDID exists on one machine only.
9. Install a runtime only when no installed runtime covers the targeted
   platform generation; each iOS runtime takes about 8 GB. Report unused
   runtimes to the user as cleanup; removing one affects every project.

One run drives a device at a time; parallel runs each claim their own. Pin a
device only when the evidence compares runs: a before and after pair, or a
rerun against a baseline, replays on the device the first capture used, so
claim that device by its identifier and wait for it. Each booted simulator or
emulator takes a few GB of memory: boot another one only while the machine has
the memory free.

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

- Screenshots: PNG with the longest side at most 1600 px: `sips -Z 1600 <file>`
  on macOS, `mogrify -resize '1600x1600>' <file>` (ImageMagick) on Linux. Both
  resize in place, keep the aspect ratio, and never enlarge.
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

**Claude cloud session.** The remote is github.com, but the session's git proxy
accepts branch pushes only: the push to `refs/evidence/<branch>` fails with
HTTP 403, and the REST git data API is refused too. Publish from a GitHub
Actions runner instead, when the project has one. A workflow on pushes to the
session's branches (`claude/**`) with `contents: write` and
`pull-requests: write`:

1. Checks out the branch, sets up the app's toolchain, and replays the capture
   recipes headlessly (a web server with `agent-browser`, Robolectric or
   another JVM screenshot test for Android).
2. Shrinks the captures and runs
   `publish_evidence.py <files> --ref "$GITHUB_REF_NAME"`; the workflow token
   pushes the ref.
3. Writes the URLs to the job summary and into the open PR's description,
   between a start and an end marker line (HTML comments such as
   `<!-- <name>:start -->` and `<!-- <name>:end -->`; the project picks
   `<name>`). Each push replaces only that block. The workflow appends the
   block when the markers are absent, keeps the rest of the body unchanged, and
   posts no PR comment.

When opening the PR, put the empty marker block in the Evidence section and
leave the capture URLs to the workflow. When editing the body later, read the
current body first and keep the block unchanged. The run is done when the block
shows the head commit. A run that finished before the PR existed left the block
empty: start the workflow again on the branch. With no runner, publish nothing:
committing the captures to a branch would carry them into every clone. Name
each planned capture as `Not captured: <what> (<reason>)`.

## Fill the Evidence section

The `pr` skill owns the body. Fill its Evidence section from this plan. In a
Claude cloud session with a runner, the marked block holds the images; write the
captions and gaps around it.

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

Done when every planned capture is published in the PR body (in a cloud
session, in the marked block) or named there as a gap.
