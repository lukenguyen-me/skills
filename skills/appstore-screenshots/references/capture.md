# Capture the real app

Read this before asking for screenshots. Discovery should produce a runnable
route to each benefit's screen, not merely a list of installed frameworks.

## Discover in the target repository

Use `rg --files` and targeted `rg` searches. Scope to the owning app in a monorepo,
excluding dependency/build directories. Inspect:

- Repo instructions and verification skills in `.agents/skills`, `.codex/skills`,
  `.claude/skills`, or the repository's established location.
- README/developer docs, Makefile/justfile, package scripts, CI workflows, and
  `scripts/` for build, seed, launch, test, snapshot, or capture commands.
- Fastlane `Snapfile`/`Fastfile` and snapshot helpers; Xcode UI tests, schemes,
  test plans, launch arguments, and `.xcresult` screenshot attachments.
- Maestro flows; Detox/Appium configs; Android instrumentation tests; Flutter
  integration tests; Playwright/Cypress/Electron or desktop UI automation.
- Demo accounts, seed scripts, local backend instructions, sample data, screenshot
  modes, feature flags, deep links, and stable accessibility identifiers.

Then check runtime availability: installed CLI/tool help, simulator/emulator
devices, connected controllers, local services, and app build prerequisites.
Inspect scripts before running them so their data effects and dependencies are
understood. Record what was found, the source path, and whether it was executed.

## Choose controls from evidence

| Repository/runtime evidence | Preferred route | Capture boundary |
| --- | --- | --- |
| Working Fastlane snapshot or screenshot UI test | Run/adapt the existing targeted flow | Use its exported images or extract its actual attachments |
| Native iOS app with XCTest/deep-link/demo hooks | Existing scheme + simulator + UI controls | `simctl io <device-id> screenshot <path>` captures only the current state |
| Native Android app with instrumentation/Maestro/Appium | Existing emulator/device flow | Existing capture helper or `adb -s <serial> exec-out screencap -p` |
| Flutter / React Native app | Existing integration/Detox/Maestro tests and launcher | Capture the actual mobile runtime, after navigation |
| Web/Electron app with browser tests | Existing page routes, fixtures, selectors, and viewport | A browser image is valid only for the surface it actually represents |
| Desktop app with UI automation | Existing app launcher and window controls | Capture the intended app window at the target scale |

Raw screenshot commands do not navigate. Use a proven UI harness or source-defined
deep link/launch state to reach the screen first. Discover a connected browser or
simulator-control tool from its actual schema; do not invent tool names. Read any
applicable installed browser/control skill before invoking its tools.

A mobile web preview does not prove a native app capture. If only a web harness
exists for a native app, look for a mobile route before falling back to the user.

## Plan, execute, inspect

For each benefit record:

```text
Benefit: TRACK YOUR PROGRESS
Screen: weekly history chart
Launch: exact repository command + app identifier + device ID
Data: existing local demo fixture with a populated history
Navigate: concrete test, selectors, or verified deep link
Ready: chart and last data point visible; loading indicator absent
Appearance: chosen light/dark mode, locale, orientation, status-bar override
Capture: absolute output path
Evidence: executed command, exit/result, observed screen, image dimensions
Cleanup: local instance/overrides created by this run
```

Use the app's existing setup and seed workflows. Small automation additions may
use its current harness, selectors, and local fixtures; describe such repo edits
in the handoff. Keep unrelated app feature repairs separate. Realism comes from
representative demo content, not post-capture rewriting of UI or numbers.

Run on a known device ID/serial, especially when several are active. Wait for
observable readiness instead of arbitrary delays. Normalize status-bar appearance
through supported simulator controls where available. Capture a full-size PNG,
then **view it** and verify the intended benefit and state. Save capture failures
and resume from the failed navigation step. Retake through the same route when
content, appearance, or overlays are poor.

Restore temporary overrides and clean up only processes/devices/data owned by
this run. Keep captures and recipes after cleanup.

## When blocked

After an actual launch/navigation failure, diagnose once from build output,
runtime state, and the available recipe. Retry when evidence supports a specific
fix; avoid repeatedly running the same failure. Record the exact blocked step.

If credentials, an unavailable host/device, or an external prerequisite are
necessary, request that intervention and continue independent analysis/layout
work. Never embed secrets in the capture plan. If no automation can be used,
request a screenshot for the exact screen, content, device, and appearance already
identified, explain what discovery ruled out, and retain the manual capture's
provenance. Reassess it with the same Great/Usable/Retake criteria.
