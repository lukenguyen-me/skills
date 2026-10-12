"""Verify publish_evidence.py stores files on a hidden ref that clones skip."""

from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills' / 'luke-mode' / 'scripts' / 'publish_evidence.py'
WEB = 'https://github.com/acme/app'


def run(*args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


class PublishEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.remote = self.tmp / 'remote.git'
        self.work = self.tmp / 'work'
        run('git', 'init', '--quiet', '--bare', str(self.remote), cwd=self.tmp)
        run('git', 'init', '--quiet', '-b', 'feat/login', str(self.work), cwd=self.tmp)
        run('git', 'remote', 'add', 'origin', str(self.remote), cwd=self.work)
        run('git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '--quiet',
            '--allow-empty', '-m', 'init', cwd=self.work)
        run('git', 'push', '--quiet', 'origin', 'feat/login', cwd=self.work)
        self.captures = self.tmp / 'captures'
        self.captures.mkdir()

    def capture(self, name, size=100):
        path = self.captures / name
        path.write_bytes(b'x' * size)
        return path

    def publish(self, *files, check=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), '--web-base', WEB, *map(str, files)],
            cwd=self.work, capture_output=True, text=True,
        )
        if check:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        return result

    def test_publishes_to_hidden_ref_with_github_urls(self):
        result = self.publish(self.capture('login-before.png'), self.capture('login-after.png'))
        self.assertEqual(result['ref'], 'refs/evidence/feat/login')
        tip = run('git', 'rev-parse', 'refs/evidence/feat/login', cwd=self.remote)
        self.assertEqual(tip, result['commit'])
        self.assertEqual(
            [f['url'] for f in result['files']],
            [f'{WEB}/blob/{tip}/login-before.png?raw=true',
             f'{WEB}/blob/{tip}/login-after.png?raw=true'],
        )

    def test_clone_does_not_download_evidence(self):
        commit = self.publish(self.capture('a.png'))['commit']
        clone = self.tmp / 'clone'
        run('git', 'clone', '--quiet', '--no-local', str(self.remote), str(clone), cwd=self.tmp)
        missing = subprocess.run(['git', 'cat-file', '-e', commit], cwd=clone)
        self.assertNotEqual(missing.returncode, 0)

    def test_republish_keeps_earlier_commits_and_files(self):
        first = self.publish(self.capture('a.png'))['commit']
        second = self.publish(self.capture('b.gif'))['commit']
        self.assertEqual(run('git', 'rev-parse', f'{second}^', cwd=self.remote), first)
        names = run('git', 'ls-tree', '--name-only', second, cwd=self.remote).split()
        self.assertEqual(names, ['a.png', 'b.gif'])

    def test_rejects_oversized_and_unsupported_files(self):
        big = self.publish(self.capture('big.png', size=11_000_000), check=False)
        self.assertIn('shrink it below', big.stderr)
        text = self.publish(self.capture('notes.txt'), check=False)
        self.assertIn('unsupported type', text.stderr)
        self.assertEqual(run('git', 'for-each-ref', 'refs/evidence', cwd=self.remote), '')


if __name__ == '__main__':
    unittest.main()
