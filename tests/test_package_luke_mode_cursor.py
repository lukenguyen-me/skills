"""Exercise the prepared skill and installation boundaries in disposable folders."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "luke-mode"
SCRIPT = ROOT / "scripts" / "package-luke-mode-cursor.py"


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


if __name__ == "__main__":
    unittest.main()
