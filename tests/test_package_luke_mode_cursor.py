"""Exercise the prepared skill and installation boundaries in disposable folders."""

from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "luke-mode"
SCRIPT = ROOT / "scripts" / "package-luke-mode-cursor.py"
SKILL_NAMES = (
    "luke-mode",
    "setup-luke-mode",
    "sync-matt-pocock-skills",
    "create-verification-skill",
    "maintain-verification-skill",
)
EXPLICIT_ONLY = {
    "luke-mode", "create-verification-skill", "maintain-verification-skill"
}


class CursorPackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="luke-cursor-test-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)

    def run_package(self, destination):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(destination)],
            cwd=self.work,
            capture_output=True,
            text=True,
        )

    def test_complete_standalone_package_from_another_working_directory(self):
        destination = self.work / "project with spaces" / ".cursor" / "skills" / "luke-mode"
        original = (SOURCE / "SKILL.md").read_text()
        result = self.run_package(destination)
        self.assertEqual(result.returncode, 0, result.stderr)

        prepared = (destination / "SKILL.md").read_text()
        _, header, body = prepared.split("---\n", 2)
        self.assertIn("\ndisable-model-invocation: true\n", "\n" + header)
        self.assertEqual(body, original.split("---\n", 2)[2])
        self.assertEqual(prepared.count("disable-model-invocation:"), 1)
        self.assertEqual(
            {p.relative_to(destination) for p in destination.rglob("*") if p.is_file()},
            {p.relative_to(SOURCE) for p in SOURCE.rglob("*") if p.is_file()},
        )
        for original_file in SOURCE.rglob("*"):
            if original_file.is_file() and original_file.name != "SKILL.md":
                self.assertEqual(
                    (destination / original_file.relative_to(SOURCE)).read_bytes(),
                    original_file.read_bytes(),
                )
        self.assertTrue((destination / "adapters" / "cursor-cloud.md").is_file())
        for name in SKILL_NAMES[1:]:
            source = SOURCE.parent / name
            sibling = destination.parent / name
            self.assertEqual(
                {p.relative_to(sibling) for p in sibling.rglob("*") if p.is_file()},
                {p.relative_to(source) for p in source.rglob("*") if p.is_file()},
            )
            for original_file in source.rglob("*"):
                if original_file.is_file() and original_file != source / "SKILL.md":
                    self.assertEqual(
                        (sibling / original_file.relative_to(source)).read_bytes(),
                        original_file.read_bytes(),
                    )
            _, source_header, source_body = (source / "SKILL.md").read_text().split(
                "---\n", 2
            )
            _, header, body = (sibling / "SKILL.md").read_text().split("---\n", 2)
            self.assertEqual(body, source_body)
            if name in EXPLICIT_ONLY:
                self.assertIn("\ndisable-model-invocation: true\n", "\n" + header)
                self.assertEqual(header.count("disable-model-invocation:"), 1)
                self.assertEqual(
                    header.replace("disable-model-invocation: true\n", ""),
                    source_header,
                )
            else:
                self.assertEqual(header, source_header)
                self.assertNotIn("disable-model-invocation:", header)
        self.assertEqual(
            {p.name for p in destination.parent.iterdir()}, set(SKILL_NAMES)
        )
        for skill_name in SKILL_NAMES:
            policy = (
                destination.parent / skill_name / "agents" / "openai.yaml"
            ).read_text()
            expected = "false" if skill_name in EXPLICIT_ONLY else "true"
            self.assertRegex(policy, rf"allow_implicit_invocation: {expected}\b")
            for markdown in (destination.parent / skill_name).rglob("*.md"):
                for link in re.findall(r"\]\(([^)]+)\)", markdown.read_text()):
                    path = link.split("#", 1)[0]
                    if path and not path.startswith(("https://", "http://")):
                        self.assertTrue(
                            (markdown.parent / path).exists(), f"{markdown}: {link}"
                        )
        self.assertEqual((SOURCE / "SKILL.md").read_text(), original)
        self.assertFalse(any(destination.parent.glob(".luke-mode-*")))

    def test_existing_installation_is_preserved(self):
        destination = self.work / "luke-mode"
        destination.mkdir()
        marker = destination / "personal-note.md"
        marker.write_text("Keep this customization.\n")
        result = self.run_package(destination)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(marker.read_text(), "Keep this customization.\n")
        self.assertEqual(list(destination.iterdir()), [marker])

    def test_existing_file_is_preserved(self):
        destination = self.work / "luke-mode"
        destination.write_text("Keep this file.\n")
        result = self.run_package(destination)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(destination.read_text(), "Keep this file.\n")

    def test_dangling_symlink_is_preserved(self):
        destination = self.work / "luke-mode"
        destination.symlink_to(self.work / "missing")
        result = self.run_package(destination)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(destination.is_symlink())
        self.assertEqual(destination.readlink(), self.work / "missing")

    def test_symlink_to_existing_installation_is_preserved(self):
        installed = self.work / "installed"
        installed.mkdir()
        marker = installed / "SKILL.md"
        marker.write_text("Keep this installation.\n")
        destination = self.work / "luke-mode"
        destination.symlink_to(installed, target_is_directory=True)
        result = self.run_package(destination)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(destination.is_symlink())
        self.assertEqual(marker.read_text(), "Keep this installation.\n")

    def test_wrong_folder_name_does_not_create_files(self):
        result = self.run_package(self.work / "wrong-name")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.work.iterdir()), [])

    def test_packaging_inside_source_is_rejected(self):
        destination = SOURCE / "nested" / "luke-mode"
        self.assertFalse(destination.exists())
        result = self.run_package(destination)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(destination.parent.exists())

    def test_existing_subskill_preserves_the_entire_target(self):
        for name in SKILL_NAMES[1:]:
            with self.subTest(skill=name):
                target_root = self.work / name
                sibling = target_root / name
                sibling.mkdir(parents=True)
                marker = sibling / "personal-note.md"
                marker.write_text("Keep this customization.\n")
                result = self.run_package(target_root / "luke-mode")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(marker.read_text(), "Keep this customization.\n")
                self.assertEqual(list(target_root.iterdir()), [sibling])

    def test_existing_subskill_file_is_preserved(self):
        for name in SKILL_NAMES[1:]:
            with self.subTest(skill=name):
                target_root = self.work / name
                target_root.mkdir()
                sibling = target_root / name
                sibling.write_text("Keep this file.\n")
                result = self.run_package(target_root / "luke-mode")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(sibling.read_text(), "Keep this file.\n")
                self.assertEqual(list(target_root.iterdir()), [sibling])

    def test_dangling_subskill_symlink_is_preserved(self):
        for name in SKILL_NAMES[1:]:
            with self.subTest(skill=name):
                target_root = self.work / name
                target_root.mkdir()
                sibling = target_root / name
                sibling.symlink_to(self.work / "missing")
                result = self.run_package(target_root / "luke-mode")
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(sibling.is_symlink())
                self.assertEqual(sibling.readlink(), self.work / "missing")
                self.assertEqual(list(target_root.iterdir()), [sibling])

    def test_packaging_inside_a_subskill_is_rejected(self):
        for name in SKILL_NAMES[1:]:
            with self.subTest(skill=name):
                destination = SOURCE.parent / name / "nested" / "luke-mode"
                self.assertFalse(destination.parent.exists())
                result = self.run_package(destination)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(destination.parent.exists())


if __name__ == "__main__":
    unittest.main()
