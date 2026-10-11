"""Verify a single Luke installation, relocated commands, and write boundaries."""

from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'skills' / 'luke-mode'
SCRIPT = ROOT / 'scripts' / 'package-luke-mode-cursor.py'
NAMES = ('setup-luke-mode', 'sync-matt-pocock-skills')


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='luke-bundle-test-')
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)

    def run_script(self, script, argument):
        return subprocess.run(
            [sys.executable, '-B', str(script), str(argument)], cwd=self.work,
            capture_output=True, text=True,
        )

    def check_links(self, bundle):
        for markdown in bundle.rglob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)', markdown.read_text()):
                path = link.split('#', 1)[0]
                if path and not path.startswith(('https://', 'http://')):
                    self.assertTrue((markdown.parent / path).exists(), f'{markdown}: {link}')

    def test_complete_single_cursor_package_from_another_directory(self):
        destination = self.work / 'project with spaces' / '.cursor' / 'skills' / 'luke-mode'
        originals = {p.relative_to(SOURCE): p.read_bytes() for p in SOURCE.rglob('*') if p.is_file()}
        result = self.run_script(SCRIPT, destination)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({p.name for p in destination.parent.iterdir()}, {'luke-mode'})
        self.assertEqual(
            {p.relative_to(destination) for p in destination.rglob('*') if p.is_file()},
            set(originals),
        )
        for relative, original in originals.items():
            prepared = (destination / relative).read_bytes()
            if relative == Path('SKILL.md'):
                _, header, body = prepared.decode().split('---\n', 2)
                _, source_header, source_body = original.decode().split('---\n', 2)
                self.assertEqual(body, source_body)
                self.assertEqual(header.count('disable-model-invocation: true'), 1)
                self.assertEqual(header.replace('disable-model-invocation: true\n', ''), source_header)
            else:
                self.assertEqual(prepared, original)
            self.assertEqual((SOURCE / relative).read_bytes(), original)
        self.assertEqual({p.name for p in (destination / 'skills').iterdir()}, set(NAMES))
        self.check_links(destination)
        self.assertFalse(any(destination.parent.glob('.luke-mode-*')))

    def test_existing_destination_entries_are_preserved(self):
        for kind in ('directory', 'file', 'dangling-link', 'link'):
            with self.subTest(kind=kind):
                destination = self.work / kind / 'luke-mode'
                destination.parent.mkdir()
                if kind == 'directory':
                    destination.mkdir()
                    (destination / 'note').write_text('keep')
                elif kind == 'file':
                    destination.write_text('keep')
                else:
                    target = self.work / (kind + '-target')
                    if kind == 'link':
                        target.mkdir()
                        (target / 'note').write_text('keep')
                    destination.symlink_to(target)
                result = self.run_script(SCRIPT, destination)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(list(destination.parent.iterdir()), [destination])
                if kind in ('directory', 'link'):
                    self.assertEqual((destination / 'note').read_text(), 'keep')
                elif kind == 'file':
                    self.assertEqual(destination.read_text(), 'keep')
                else:
                    self.assertTrue(destination.is_symlink())

    def test_wrong_name_and_source_overlap_are_rejected(self):
        for destination in (self.work / 'wrong', SOURCE / 'nested' / 'luke-mode'):
            with self.subTest(destination=destination):
                self.assertFalse(destination.exists())
                result = self.run_script(SCRIPT, destination)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(destination.exists())

    def test_commands_register_from_only_a_relocated_luke_installation(self):
        root = self.work / 'project with spaces' / '.agents' / 'skills'
        bundle = root / 'luke-mode'
        shutil.copytree(SOURCE, bundle)
        script = bundle / 'scripts' / 'register-subskills.py'
        for attempt in range(2):
            result = self.run_script(script, root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f'Registered {2 if attempt == 0 else 0} new commands', result.stdout)
        self.assertEqual({p.name for p in root.iterdir()}, {'luke-mode', *NAMES})
        for name in NAMES:
            alias = root / name
            self.assertTrue(alias.is_symlink())
            self.assertEqual(alias.resolve(), (bundle / 'skills' / name).resolve())
            self.assertEqual((alias / 'SKILL.md').read_bytes(), (bundle / 'skills' / name / 'SKILL.md').read_bytes())
        self.check_links(bundle)

    def test_registration_conflicts_preserve_all_commands(self):
        for kind in ('file', 'directory', 'dangling-link', 'link'):
            with self.subTest(kind=kind):
                root = self.work / kind
                bundle = root / 'luke-mode'
                shutil.copytree(SOURCE, bundle)
                conflict = root / NAMES[-1]
                if kind == 'file':
                    conflict.write_text('keep')
                elif kind == 'directory':
                    conflict.mkdir()
                    (conflict / 'note').write_text('keep')
                else:
                    conflict.symlink_to(self.work / 'other' if kind == 'dangling-link' else SOURCE)
                result = self.run_script(bundle / 'scripts' / 'register-subskills.py', root)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual({p.name for p in root.iterdir()}, {'luke-mode', NAMES[-1]})
                if kind == 'file':
                    self.assertEqual(conflict.read_text(), 'keep')
                elif kind == 'directory':
                    self.assertEqual((conflict / 'note').read_text(), 'keep')
                else:
                    self.assertTrue(conflict.is_symlink())

    def test_registration_inside_bundle_is_rejected(self):
        bundle = self.work / 'luke-mode'
        shutil.copytree(SOURCE, bundle)
        result = self.run_script(bundle / 'scripts' / 'register-subskills.py', bundle / 'nested')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((bundle / 'nested').exists())


if __name__ == '__main__':
    unittest.main()
