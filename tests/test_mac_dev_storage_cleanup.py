"""Smoke tests for the mac-dev-storage-cleanup scripts, run against a fake HOME under /bin/bash."""

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import unittest


SKILL = Path(__file__).resolve().parents[1] / "skills/mac-dev-storage-cleanup"
SCRIPTS = SKILL / "scripts"
BASH = "/bin/bash"
OLD_DAYS = 200

ARCHIVE_PLIST = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>ApplicationProperties</key><dict>
<key>CFBundleIdentifier</key><string>{bid}</string>
<key>CFBundleShortVersionString</key><string>{ver}</string>
</dict></dict></plist>
"""


# The format of `xcrun simctl runtime list` on Xcode 26.
RUNTIME_LIST = """== Disk Images ==
-- iOS --
iOS 26.4.1 (23E254a) - 60932D60-E239-4785-A9CB-696919301745 (Ready)
iOS 27.0 (24A434) - 840D277F-5F9F-4911-A109-4785E689B8E6 (Ready)
iOS 18.6 (22G86) - A19C19AD-4971-458C-9F8A-335D8A3F5A12 (Ready)
iOS 26.5 (23F77) - 86785523-2199-4604-BDC9-8C39B2A56667 (Ready)

Total Disk Images: 4 (31.6G)
"""


def age(path, days):
    """Set a path's modification time to `days` ago."""
    stamp = time.time() - days * 86400
    os.utime(path, (stamp, stamp))


@unittest.skipUnless(sys.platform == "darwin", "the scripts target macOS and BSD tools")
class CleanupScriptTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.home = self.root / "home"
        self.home.mkdir()
        self.stubs = self.root / "stubs"
        self.stubs.mkdir()
        self.stub_log = self.root / "stub.log"
        # Stubs keep the run hermetic: the real npm, xcrun, and docker never run.
        # Each logs its call; xcrun and docker print canned listings.
        for name, body in (
            ("npm", ""),
            ("xcrun", 'case "$*" in "simctl runtime list") cat <<EOF\n' + RUNTIME_LIST + 'EOF\n;; esac\n'),
            ("docker", 'case "$*" in "volume ls -q -f dangling=true") printf "v1\\nv2\\n" ;; esac\n'),
        ):
            stub = self.stubs / name
            stub.write_text(f'#!/bin/bash\necho "{name} $*" >> "{self.stub_log}"\n{body}')
            stub.chmod(0o755)
        self.env = {
            "HOME": str(self.home),
            "TMPDIR": str(self.root) + "/",
            "PATH": f"{self.stubs}:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
            "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
        }
        self.plan = self.root / "plan.tsv"
        self.projects = self.home / "repos"
        self.projects.mkdir()

    # ---- helpers ----

    def sh(self, script, *args, env=None, check=True, cwd=None):
        merged = dict(self.env, **(env or {}))
        result = subprocess.run([BASH, str(SCRIPTS / script), *args], env=merged,
                                capture_output=True, text=True, cwd=cwd)
        if check:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def git(self, repo, *args, date=None):
        env = dict(self.env)
        if date:
            env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
        subprocess.run(["git", "-C", str(repo), *args], env=env, check=True, capture_output=True)

    def write(self, path, text="x" * 4096):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def age_tree(self, root, days=OLD_DAYS):
        for path in Path(root).rglob("*"):
            if ".git" not in path.parts:
                age(path, days)
        age(root, days)

    def make_repo(self, name, files, old=True, remote=True):
        repo = self.projects / name
        repo.mkdir()
        for rel, text in files.items():
            self.write(repo / rel, text)
        self.git(repo, "init", "-q", "-b", "main")
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-q", "-m", "init",
                 date=f"{time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(time.time() - OLD_DAYS * 86400))}+0000" if old else None)
        if remote:
            bare = self.root / f"{name}.git"
            subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], env=self.env, check=True)
            self.git(repo, "remote", "add", "origin", str(bare))
            self.git(repo, "push", "-q", "origin", "main")
        if old:
            self.age_tree(repo)
        return repo

    def rows(self):
        out = []
        for line in self.plan.read_text().splitlines():
            tier, rid, kb, label, action, target, project = line.split("\t")
            out.append(dict(tier=tier, id=rid, kb=int(kb), label=label, action=action,
                            target=target, project=project))
        return out

    def find(self, **match):
        return [r for r in self.rows() if all(match[k] in r[k] if k in ("label", "target") else r[k] == match[k] for k in match)]

    def scan(self, *extra):
        return self.sh("scan.sh", "--out", str(self.plan), "--roots", str(self.projects), *extra)

    def build_fixture(self):
        h = self.home
        # Safe: Claude junk older than a day, DerivedData, npm cache.
        age(self.write(h / ".claude/debug/log.txt"), 3)
        self.write(h / ".claude/debug/current.txt")  # a running session's log
        age(self.write(h / ".claude/shell-snapshots/snap.sh"), 3)
        self.write(h / ".claude/shell-snapshots/live.sh")  # a running session's snapshot
        self.write(h / ".claude/projects/session.jsonl")  # chat history: report only
        self.write(h / "Library/Developer/Xcode/DerivedData/App/build.o")
        self.write(h / ".npm/_cacache/index")
        # Old-only: DeviceSupport keeps the newest 2 even when old; Gradle store; Downloads.
        for name, days in (("17.0 (A)", 400), ("17.1 (B)", 300), ("17.2 (C)", 200), ("17.3 (D)", 10)):
            d = h / "Library/Developer/Xcode/iOS DeviceSupport" / name
            self.write(d / "sym")
            age(d, days)
        # Gradle 7.0 and 7.5 are idle. 8.0 is in use: a build rewrote a file
        # inside its caches, so its folder date and its wrapper stay old.
        self.write(h / ".gradle/wrapper/dists/gradle-7.0-bin/abc/gradle-7.0/bin")
        self.write(h / ".gradle/caches/7.5/fileHashes/fileHashes.bin")
        self.write(h / ".gradle/wrapper/dists/gradle-8.0-all/def/gradle-8.0/bin")
        self.write(h / ".gradle/caches/8.0/kotlin-dsl/accessors.bin")
        for d in ("wrapper/dists/gradle-7.0-bin", "caches/7.5", "wrapper/dists/gradle-8.0-all", "caches/8.0"):
            self.age_tree(h / ".gradle" / d, 60)
        self.write(h / ".gradle/caches/8.0/fileHashes/fileHashes.lock")
        self.write(h / "Downloads/old.dmg"); age(h / "Downloads/old.dmg", 60)
        self.write(h / "Downloads/new.zip")
        self.write(h / "Downloads/notes.txt"); age(h / "Downloads/notes.txt", 60)
        # Xcode archives: 1.10 is newer than 1.9 numerically.
        for day, name, bid, ver, days in (
            ("2025-01-01", "App 1.9", "com.x.app", "1.9", 5),
            ("2025-02-01", "App 1.10 a", "com.x.app", "1.10", 30),
            ("2025-03-01", "App 1.10 b", "com.x.app", "1.10", 20),
            ("2025-03-02", "Other 2.0", "com.x.other", "2.0", 90),
        ):
            a = h / f"Library/Developer/Xcode/Archives/{day}/{name}.xcarchive"
            self.write(a / "Info.plist", ARCHIVE_PLIST.format(bid=bid, ver=ver))
            age(a, days)
        # Ask first: nvm version, Trash.
        self.write(h / ".nvm/versions/node/v18.0.0/bin/node")
        self.write(h / ".Trash/leftover")
        # Projects.
        self.make_repo("idle-untracked-build", {
            "package.json": "{}", ".gitignore": "",
        })
        art = self.projects / "idle-untracked-build"
        self.write(art / "node_modules/pkg/index.js"); age(art / "node_modules", OLD_DAYS)
        self.write(art / "build/out.js"); age(art / "build", OLD_DAYS)  # untracked, not ignored
        self.make_repo("tracked-dist", {"package.json": "{}", "dist/keep.js": "1"})
        self.write(self.projects / "tracked-dist/node_modules/m.js")
        age(self.projects / "tracked-dist/node_modules", OLD_DAYS)
        self.make_repo("no-marker", {"readme.md": "r"})
        self.write(self.projects / "no-marker/node_modules/m.js")
        age(self.projects / "no-marker/node_modules", OLD_DAYS)
        dirty = self.make_repo("dirty", {"package.json": "{}", "a.txt": "a"})
        self.write(self.projects / "dirty/node_modules/m.js")
        self.write(dirty / "a.txt", "changed")
        age(dirty / "a.txt", OLD_DAYS)
        self.make_repo("recent", {"package.json": "{}"}, old=False)
        self.write(self.projects / "recent/node_modules/m.js")
        unpushed = self.make_repo("unpushed", {"package.json": "{}"})
        self.write(unpushed / "b.txt", "b"); age(unpushed / "b.txt", OLD_DAYS)
        self.git(unpushed, "add", "-A")
        self.git(unpushed, "commit", "-q", "-m", "local",
                 date=time.strftime("%Y-%m-%dT%H:%M:%S+0000", time.gmtime(time.time() - OLD_DAYS * 86400)))
        self.write(unpushed / "node_modules/m.js")

    # ---- static checks ----

    def test_scripts_parse_under_bash_3_2(self):
        for name in ("lib.sh", "scan.sh", "clean.sh"):
            result = subprocess.run([BASH, "-n", str(SCRIPTS / name)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_no_hardcoded_home_path_sudo_or_rm_rf(self):
        for path in [SKILL / "SKILL.md", *SCRIPTS.iterdir()]:
            text = path.read_text()
            self.assertNotRegex(text, r"/Users/|/home/\w", f"hardcoded home path in {path.name}")
        for path in SCRIPTS.iterdir():
            text = path.read_text()
            self.assertNotRegex(text, r"\bsudo\b", f"sudo in {path.name}")
            self.assertNotRegex(text, r"\brm\s+-\w*r\w*f|\brm\s+-\w*f\w*r", f"rm -rf in {path.name}")

    def test_frontmatter_name_matches_folder(self):
        text = (SKILL / "SKILL.md").read_text()
        self.assertRegex(text, r"(?m)^name: mac-dev-storage-cleanup$")
        self.assertRegex(text, r"(?m)^description: ")

    # ---- roots ----

    def test_roots_split_on_colons_and_keep_spaces(self):
        (self.root / "a b").mkdir()
        (self.root / "c").mkdir()
        result = self.sh("scan.sh", "--print-roots", env={"PROJECTS_ROOT": f"{self.root}/a b:{self.root}/c:{self.root}/missing"})
        self.assertEqual(result.stdout.splitlines(), [f"{self.root}/a b", f"{self.root}/c"])

    def test_roots_auto_detect_common_folders(self):
        (self.home / "Developer").mkdir()
        (self.home / "Projects").mkdir()
        result = self.sh("scan.sh", "--print-roots")
        self.assertEqual(sorted(result.stdout.splitlines()), sorted([str(self.home / "Developer"), str(self.home / "Projects")]))

    # ---- scan ----

    def test_scan_tiers_and_thresholds(self):
        self.build_fixture()
        result = self.scan()
        self.assertIn("SAFE", result.stdout)
        safe = {r["label"] for r in self.find(tier="safe")}
        self.assertTrue(any("~/.claude/debug" in label for label in safe))
        self.assertTrue(any("DerivedData" in label for label in safe))
        self.assertTrue(any(r["target"] == "npm-cache" for r in self.find(tier="safe")))

        old = [r["label"] for r in self.find(tier="old")]
        # The newest 2 DeviceSupport dirs stay even though 17.2 is past 90 days.
        support = sorted(l for l in old if "DeviceSupport" in l)
        self.assertEqual(len(support), 2)
        self.assertTrue("17.0 (A)" in support[0] and "17.1 (B)" in support[1])
        self.assertTrue(any("Gradle 7.0 distribution" in l for l in old))
        self.assertTrue(any("Gradle 7.5 caches" in l for l in old))
        self.assertFalse(any("Gradle 8.0" in l for l in old), old)
        self.assertTrue(any("old.dmg" in l for l in old))
        self.assertFalse(any("new.zip" in l or "notes.txt" in l for l in old))

    def test_xcode_archive_keeps_newest_of_newest_version(self):
        self.build_fixture()
        self.scan()
        superseded = sorted(Path(r["target"]).name for r in self.find(tier="ask") if "Xcode archive" in r["label"])
        self.assertEqual(superseded, ["App 1.10 a.xcarchive", "App 1.9.xcarchive"])
        self.assertTrue(all("dSYMs" in r["label"] for r in self.find(label="Xcode archive")))

    def test_untracked_build_folder_does_not_mark_a_project_in_progress(self):
        self.build_fixture()
        self.scan()
        idle = str(self.projects / "idle-untracked-build")
        names = sorted(Path(r["target"]).name for r in self.find(action="artifact") if r["project"] == idle)
        self.assertEqual(names, ["build", "node_modules"])
        self.assertFalse(any("In progress" in r["label"] and idle in r["label"].replace("~", str(self.home)) for r in self.rows()))

    def test_in_progress_projects_are_kept_and_unsafe_artifacts_skipped(self):
        self.build_fixture()
        self.scan()
        labels = "\n".join(r["label"].replace("~", str(self.home)) for r in self.find(tier="report"))
        for name, reason in (("dirty", "uncommitted"), ("recent", "commit in last"), ("unpushed", "unpushed")):
            self.assertRegex(labels, rf"In progress, kept: .*/repos/{name} \({reason}")
        artifact_projects = {Path(r["project"]).name for r in self.find(action="artifact")}
        self.assertEqual(artifact_projects, {"idle-untracked-build", "tracked-dist"})
        tracked = [Path(r["target"]).name for r in self.find(action="artifact") if r["project"].endswith("tracked-dist")]
        self.assertEqual(tracked, ["node_modules"])  # tracked dist/ never listed; no-marker repo never listed

    def test_chat_history_is_report_only(self):
        self.build_fixture()
        self.scan()
        chat = self.find(label="Claude chat history")
        self.assertEqual([(r["tier"], r["action"]) for r in chat], [("report", "none")])

    def test_scan_is_read_only(self):
        self.build_fixture()
        before = sorted(str(p) for p in self.home.rglob("*"))
        self.scan()
        self.assertEqual(before, sorted(str(p) for p in self.home.rglob("*")))

    def test_worktree_offered_only_when_clean_and_pushed(self):
        repo = self.make_repo("wt", {"package.json": "{}"})
        for name in ("pushed", "dirty"):
            self.git(repo, "worktree", "add", "-q", "-b", name, str(self.projects / f"wt-{name}"))
        self.git(self.projects / "wt-pushed", "push", "-q", "origin", "pushed")
        self.write(self.projects / "wt-dirty/new.txt")
        self.scan()
        offered = [Path(r["target"]).name for r in self.find(action="worktree")]
        kept = [r["label"] for r in self.find(tier="report") if "Git worktree" in r["label"]]
        self.assertEqual(offered, ["wt-pushed"])
        self.assertEqual(len(kept), 1)
        self.assertIn("wt-dirty", kept[0])

    # ---- clean ----

    def test_dry_run_changes_nothing(self):
        self.build_fixture()
        self.scan()
        before = sorted(str(p) for p in self.home.rglob("*"))
        self.stub_log.unlink(missing_ok=True)  # the scan called the xcrun stub
        result = self.sh("clean.sh", "run", "--plan", str(self.plan), "--dry-run", "--tier", "safe", "--tier", "old")
        self.assertIn("would", result.stdout)
        self.assertEqual(before, sorted(str(p) for p in self.home.rglob("*")))
        self.assertFalse(self.stub_log.exists())
        self.assertFalse((self.home / "Library/Logs/dev-cleanup.log").exists())

    def test_safe_tier_uses_official_command_and_trash_and_logs(self):
        self.build_fixture()
        self.scan()
        self.sh("clean.sh", "run", "--plan", str(self.plan), "--tier", "safe")
        self.assertIn("npm cache clean --force", self.stub_log.read_text())
        self.assertFalse((self.home / ".claude/debug/log.txt").exists())
        self.assertTrue((self.home / ".Trash/claude-debug/log.txt").exists())
        self.assertTrue((self.home / ".claude/debug/current.txt").exists())
        self.assertTrue((self.home / ".claude/shell-snapshots/live.sh").exists())
        self.assertTrue((self.home / ".claude/projects/session.jsonl").exists())
        log = (self.home / "Library/Logs/dev-cleanup.log").read_text()
        self.assertIn("npm-cache", log)
        self.assertIn(str(self.home / ".claude/debug"), log)

    def test_summary_reports_space_held_in_trash(self):
        self.build_fixture()
        self.scan()
        result = self.sh("clean.sh", "run", "--plan", str(self.plan), "--tier", "old")
        self.assertIn("moved to Trash:", result.stdout)
        self.assertIn("once the Trash is emptied", result.stdout)

    def test_old_tier_removes_only_listed_items(self):
        self.build_fixture()
        self.scan()
        self.sh("clean.sh", "run", "--plan", str(self.plan), "--tier", "old")
        self.assertFalse((self.home / "Downloads/old.dmg").exists())
        self.assertTrue((self.home / "Downloads/notes.txt").exists())
        self.assertTrue((self.home / "Downloads/new.zip").exists())
        support = self.home / "Library/Developer/Xcode/iOS DeviceSupport"
        self.assertTrue((support / "17.2 (C)").exists() and (support / "17.3 (D)").exists())
        self.assertFalse((support / "17.0 (A)").exists() or (support / "17.1 (B)").exists())

    def test_ask_rows_need_their_id_and_tier_flag_rejects_ask(self):
        self.build_fixture()
        self.scan()
        result = self.sh("clean.sh", "run", "--plan", str(self.plan), "--tier", "ask", check=False)
        self.assertEqual(result.returncode, 2)
        self.sh("clean.sh", "run", "--plan", str(self.plan), "--tier", "safe")
        self.assertTrue((self.home / ".nvm/versions/node/v18.0.0").exists())
        nvm = self.find(label="Node version")[0]
        self.sh("clean.sh", "run", "--plan", str(self.plan), nvm["id"])
        self.assertFalse((self.home / ".nvm/versions/node/v18.0.0").exists())

    def test_artifacts_go_only_for_a_named_project(self):
        self.build_fixture()
        self.scan()
        idle = self.projects / "idle-untracked-build"
        by_id = self.find(action="artifact", target=str(idle / "node_modules"))[0]["id"]
        self.sh("clean.sh", "run", "--plan", str(self.plan), by_id, check=False)
        self.assertTrue((idle / "node_modules").exists(), "an artifact id alone must not delete")
        self.sh("clean.sh", "run", "--plan", str(self.plan), "--project", str(idle))
        self.assertFalse((idle / "node_modules").exists())
        self.assertFalse((idle / "build").exists())
        self.assertTrue((idle / "package.json").exists())
        self.assertTrue((idle / ".git").exists())
        self.assertTrue((self.projects / "tracked-dist/dist/keep.js").exists())

    def test_artifact_rechecked_at_delete_time(self):
        self.build_fixture()
        self.scan()
        idle = self.projects / "idle-untracked-build"
        self.write(idle / "fresh.txt", "work in progress")  # becomes dirty after the scan
        result = self.sh("clean.sh", "run", "--plan", str(self.plan), "--project", str(idle), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("project in progress", result.stdout)
        self.assertTrue((idle / "node_modules").exists())

    def test_protected_and_outside_paths_are_refused(self):
        secret = self.write(self.home / ".ssh/id_ed25519", "key")
        outside = self.write(self.home / "Documents/thesis.txt", "thesis")
        plan = self.root / "forged.tsv"
        plan.write_text(
            f"safe\t1\t1\tssh\ttrash\t{secret}\t-\n"
            f"safe\t2\t1\tdocs\ttrash\t{outside}\t-\n"
            f"safe\t3\t1\tgit\ttrash\t{self.home}/Downloads/../.ssh\t-\n"
            f"safe\t4\t1\tcmd\tcmd\trm-everything\t-\n")
        result = self.sh("clean.sh", "run", "--plan", str(plan), "--tier", "safe", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(secret.exists() and outside.exists())
        self.assertIn("refused", result.stdout)

    def test_worktree_removed_with_git(self):
        repo = self.make_repo("wt", {"package.json": "{}"})
        self.git(repo, "worktree", "add", "-q", "-b", "done", str(self.projects / "wt-done"))
        self.git(self.projects / "wt-done", "push", "-q", "origin", "done")
        self.scan()
        wt = self.find(action="worktree")[0]
        self.sh("clean.sh", "run", "--plan", str(self.plan), wt["id"])
        self.assertFalse((self.projects / "wt-done").exists())
        self.assertTrue(repo.exists())

    def test_unknown_id_fails(self):
        self.build_fixture()
        self.scan()
        result = self.sh("clean.sh", "run", "--plan", str(self.plan), "9999", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not in the plan", result.stdout)

    def test_preflight_blocks_on_running_app(self):
        busy = subprocess.Popen(["/bin/sleep", "30"])
        self.addCleanup(lambda: (busy.kill(), busy.wait()))
        blocked = self.sh("clean.sh", "preflight", env={"DEV_CLEANUP_APPS": "sleep"}, check=False)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("sleep", blocked.stdout)
        clear = self.sh("clean.sh", "preflight", env={"DEV_CLEANUP_APPS": "no-such-process-xyz"})
        self.assertIn("ok", clear.stdout)

    def test_sdkmanager_prefers_cmdline_tools_over_legacy_on_path(self):
        # The legacy tools/bin is on PATH, as many shell profiles set it. Its
        # sdkmanager needs Java 8 and crashes, so the cmdline-tools copy must win.
        sdk = self.home / "Library/Android/sdk"
        self.write(sdk / "ndk/27.1.12297006/source.properties")
        for rel, body in (("tools/bin/sdkmanager", "exit 1"),
                          ("cmdline-tools/latest/bin/sdkmanager", "")):
            tool = self.write(sdk / rel, f'#!/bin/bash\necho "{rel} $*" >> "{self.stub_log}"\n{body}\n')
            tool.chmod(0o755)
        env = {"PATH": f"{sdk}/tools/bin:{self.env['PATH']}"}
        self.sh("scan.sh", "--out", str(self.plan), "--roots", str(self.projects), env=env)
        row = self.find(action="cmd", label="ndk;27.1.12297006")[0]
        self.sh("clean.sh", "run", "--plan", str(self.plan), row["id"], env=env)
        log = self.stub_log.read_text()
        self.assertIn("cmdline-tools/latest/bin/sdkmanager --uninstall ndk;27.1.12297006", log)
        self.assertNotIn("\ntools/bin/sdkmanager", "\n" + log)


    # ---- review regressions ----

    def test_runtime_outdated_only_within_its_major_version(self):
        self.scan()
        old = sorted(r["label"] for r in self.find(tier="old") if "Simulator runtime" in r["label"])
        self.assertEqual(len(old), 1, old)
        self.assertIn("iOS 26.4.1", old[0])  # 26.5 supersedes it; 18.6 is the only iOS 18

    def test_docker_prune_and_volumes_are_ask_first(self):
        self.scan()
        docker = [(r["tier"], r["target"]) for r in self.rows() if r["target"].startswith("docker")]
        self.assertEqual(sorted(docker), [("ask", "docker-prune"), ("ask", "docker-volumes")])
        self.assertIn("2 Docker volume(s)", self.find(target="docker-volumes")[0]["label"])

    def test_nested_repo_artifacts_belong_to_the_nested_repo(self):
        outer = self.make_repo("outer", {"package.json": "{}", ".gitignore": "inner/\n"})
        self.write(outer / "node_modules/m.js")
        inner = self.projects / "outer/inner"
        inner.mkdir()
        self.write(inner / "package.json", "{}")
        self.git(inner, "init", "-q", "-b", "main")
        self.git(inner, "add", "-A")
        self.git(inner, "commit", "-q", "-m", "fresh")  # in progress: committed today
        self.write(inner / "node_modules/m.js")
        self.age_tree(inner)
        self.age_tree(outer)
        self.scan()
        artifacts = [r["target"] for r in self.find(action="artifact")]
        self.assertEqual(artifacts, [str(outer / "node_modules")])
        self.assertTrue(self.find(label="In progress, kept: ~/repos/outer/inner"))
        self.sh("clean.sh", "run", "--plan", str(self.plan), "--project", str(outer))
        self.assertTrue((inner / "node_modules/m.js").exists())
        self.assertFalse((outer / "node_modules").exists())

    def test_worktree_with_untracked_secret_is_kept(self):
        repo = self.make_repo("wt", {"package.json": "{}", ".gitignore": ".env\n"})
        wt = self.projects / "wt-secret"
        self.git(repo, "worktree", "add", "-q", "-b", "secret", str(wt))
        self.git(wt, "push", "-q", "origin", "secret")
        self.write(wt / ".env", "API_KEY=1")  # ignored, so git worktree remove would delete it
        self.scan()
        self.assertFalse(self.find(action="worktree"))
        kept = [r["label"] for r in self.rows() if "Git worktree" in r["label"]]
        self.assertEqual(len(kept), 1)
        self.assertIn("holds untracked .env", kept[0])
        forged = self.root / "forged.tsv"
        forged.write_text(f"ask\t1\t1\twt\tworktree\t{wt}\t{repo}\n")
        result = self.sh("clean.sh", "run", "--plan", str(forged), "1", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((wt / ".env").exists())

    def test_trash_names_never_collide(self):
        mono = self.make_repo("mono", {"package.json": "{}", "packages/a/package.json": "{}",
                                       "packages/b/package.json": "{}"})
        for rel in ("node_modules", "packages/a/node_modules", "packages/b/node_modules"):
            self.write(mono / rel / "m.js", rel)
        self.age_tree(mono)
        self.write(self.home / ".Trash/mono node_modules/old.js")  # an earlier run's item
        self.scan()
        self.sh("clean.sh", "run", "--plan", str(self.plan), "--project", "mono")
        trash = sorted(p.name for p in (self.home / ".Trash").iterdir())
        self.assertEqual(len(trash), 4, trash)
        contents = sorted((p / "m.js").read_text() for p in (self.home / ".Trash").iterdir() if (p / "m.js").exists())
        self.assertEqual(contents, ["node_modules", "packages/a/node_modules", "packages/b/node_modules"])
        self.assertTrue((self.home / ".Trash/mono node_modules/old.js").exists())

    def test_empty_trash_runs_after_everything_else(self):
        self.build_fixture()
        self.scan()
        empty = self.find(target="empty-trash")[0]["id"]
        nvm = self.find(label="Node version")[0]["id"]
        result = self.sh("clean.sh", "run", "--plan", str(self.plan), "--dry-run", f"{empty},{nvm}")
        lines = [l for l in result.stdout.splitlines() if l.startswith("[")]
        self.assertEqual([l.split("]")[0][1:] for l in lines], [nvm, empty])

    def test_relative_roots_become_absolute(self):
        self.build_fixture()
        self.sh("scan.sh", "--out", str(self.plan), "--roots", "repos", cwd=self.home)
        targets = [r["target"] for r in self.find(action="artifact")]
        self.assertTrue(targets)
        self.assertTrue(all(t.startswith("/") for t in targets), targets)

    def test_project_named_by_folder_or_trailing_slash(self):
        self.build_fixture()
        self.scan()
        idle = self.projects / "idle-untracked-build"
        self.sh("clean.sh", "run", "--plan", str(self.plan), "--project", "idle-untracked-build")
        self.assertFalse((idle / "node_modules").exists())
        self.make_repo("tracked-dist-copy", {"package.json": "{}"})
        self.sh("clean.sh", "run", "--plan", str(self.plan), "--project", str(self.projects / "tracked-dist") + "/")
        self.assertFalse((self.projects / "tracked-dist/node_modules").exists())

    def test_ambiguous_project_name_is_refused(self):
        for group in ("a", "b"):
            (self.projects / group).mkdir()
            repo = self.make_repo(f"{group}/app", {"package.json": "{}"}, remote=False)
            self.write(repo / "node_modules/m.js")
            self.age_tree(repo)
        self.scan()
        result = self.sh("clean.sh", "run", "--plan", str(self.plan), "--project", "app", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("full path", result.stderr)
        self.assertTrue((self.projects / "a/app/node_modules").exists())


if __name__ == "__main__":
    unittest.main()
