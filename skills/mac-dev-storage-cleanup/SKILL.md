---
name: mac-dev-storage-cleanup
description: >
  Free disk space on a developer Mac without touching in-progress work. Use
  when the disk is full or low on storage, or to clean Xcode (DerivedData,
  Archives, DeviceSupport, simulators), Gradle, Android SDK and emulators,
  npm/pnpm/Homebrew/CocoaPods caches, Docker, agent git worktrees,
  node_modules and other project build artifacts, or Claude/Codex/Cursor
  leftovers. Do not use on non-macOS machines, or to delete documents,
  photos, mail, or chat history.
---

# Mac dev storage cleanup

Free space on a developer Mac in four moves: scan read-only, report by tier,
delete only what the user confirms, show the before and after. Scripts live in
`scripts/` beside this file; run them with `bash`. `scan.sh` writes a plan
file; `clean.sh` acts on that plan and logs every action to
`~/Library/Logs/dev-cleanup.log`.

## Workflow

### 1. Baseline and project roots

- Run `df -h /` and keep the output as the **before**.
- Find the projects root: `PROJECTS_ROOT` (colon-separated) when set. Otherwise
  ask the user, offering what `bash scripts/scan.sh --print-roots` auto-detects
  (`~/Developer`, `~/Projects`, `~/Code`, `~/src`, `~/Documents/projects`, ...).
- Pass the answer as `--roots a:b` in step 2.

Completion: the **before** is recorded and the roots are confirmed by the user
or by `PROJECTS_ROOT`.

### 2. Scan and report

Run `bash scripts/scan.sh --roots <a:b>` with a timeout of several minutes;
`du` over large caches is slow. Present its report tier by tier with sizes, the
biggest first. Report sizes marked `-` as unknown.

Completion: every tier the scan printed is shown, and the plan file path is known.

### 3. Confirm

Ask the user which rows to clean. Delete nothing before an explicit answer.

- **Safe** and **Old-only**: the user approves a whole tier or picks ids.
- **Ask first**: the user names each id.
- **Build artifacts** (report-only rows): the user names the projects.
- **AI chat history**: point to the tool's own cleanup shown in the row.
- **The Trash**: a move to the Trash frees no space until the Trash is emptied.
  Say so, and say that emptying it also deletes, for good, what this run moves
  there.

Completion: a list of approved tiers, ids, and projects exists.

### 4. Prepare

- Run `bash scripts/clean.sh preflight`. When it names running apps (Xcode,
  Simulator, Android Studio, Cursor), ask the user to quit them, then rerun
  until it passes.
- Run `bash scripts/clean.sh stop-gradle`.

Completion: `preflight` exits 0.

### 5. Clean

Run `bash scripts/clean.sh run --plan <plan> ...` with `--tier safe|old`, row
ids, and `--project <path>` as approved. Start with `--dry-run` when the
selection is large. An approved empty-the-Trash row runs last on its own.

Completion: every approved row printed an outcome. Report each row that did not
succeed, with its reason.

### 6. Verify

Run `df -h /` again and show before and after beside the freed total. When the
Trash was not emptied, give the amount `clean.sh` reports as held in the Trash.
Give the log path.

Completion: the user sees the before, the after, and the log path.

## Tiers

| Tier | Contents | Method |
| --- | --- | --- |
| Safe | Entries older than a day in Claude junk dirs (`debug`, `shell-snapshots`, `statsig`, `paste-cache`; running sessions use the newer ones), Xcode DerivedData, npm, pnpm, Homebrew, and CocoaPods caches, unavailable simulators | official command, else Trash |
| Old-only | iOS DeviceSupport older than 90 days (newest 2 stay), Gradle version stores with no file change in 30 days, Downloads installers and archives older than 30 days, simulator runtimes with a newer runtime of the same major version | official command, else Trash |
| Ask first | Xcode Archives except the newest archive of each app's newest version, Android AVDs and SDK packages, clean and pushed agent git worktrees, nvm and pyenv versions, `docker system prune` (stopped containers can hold data; volumes stay), dangling Docker volumes, iOS backups, the Trash | one named id each |
| Report only | Project build artifacts (`node_modules`, `.next`, `dist`, `build`, `Pods`, `.build`, `.gradle`, `.venv`), AI chat history, in-progress projects, dirty worktrees | only with `--project` for artifacts; nothing else |

**In progress** means a commit or file change in the last 14 days, or dirty,
stashed, or unpushed git work (an unignored untracked artifact dir such as
`build/` does not make a repo dirty). The scan lists such projects as kept, and
`clean.sh` re-checks the state at deletion time.

A build artifact goes only when it sits beside its marker file (`package.json`,
`Podfile`, ...), git does not track it, and it belongs to the project itself,
not to a nested repo or worktree inside it.

A worktree is offered only when it has no changes, its HEAD is on a remote
branch, and it holds no untracked `.env*` file or key: `git worktree remove`
deletes ignored files for good.

## Safety

- Delete only through the official command or the Trash. The scripts never use
  `rm -rf` or `sudo`; stay inside them.
- Never touch: keychains, `~/.ssh`, `.env*`, `.git`, signing certificates,
  provisioning profiles, keystores, agent configs and logins, Mail, Photos,
  iCloud, other apps' Application Support, `/System`. `clean.sh` refuses these
  paths, any path outside its cleanup locations, and paths on another volume
  (a move to the home Trash would copy them onto the full disk).
- Sizes of Docker items and simulator runtimes are unknown. Say so.

## Editing the scripts

Keep them runnable on macOS `/bin/bash` 3.2 with BSD tools: no associative
arrays, `mapfile`, or GNU flags; skip a missing tool with `command -v`; keep
paths relative to `$HOME`. Check with `/bin/bash -n scripts/*.sh` and
`python3 -m unittest discover -s tests -p 'test_mac_dev*'`.
