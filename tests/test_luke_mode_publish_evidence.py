"""Verify publish_evidence.py: the hidden-ref store, the R2 store, and --check."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import datetime
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills' / 'luke-mode' / 'scripts' / 'publish_evidence.py'
WEB = 'https://github.com/acme/app'
PUBLIC = 'https://evidence.example.com'
SECRETS = {
    'R2_ACCOUNT_ID': '0123456789abcdef0123456789abcdef',
    'R2_ACCESS_KEY_ID': 'AKIDEXAMPLEKEYID0001',
    'R2_SECRET_ACCESS_KEY': 'sEcReTvAlUe/DoNoTpRiNt+0123456789abcdef',
}
CONFIG = f"""# PR evidence

| Key | Value |
| --- | --- |
| store | r2 |
| bucket | pr-evidence |
| public-url | {PUBLIC} |
| key-prefix | acme/app |
| account-id-var | R2_ACCOUNT_ID |
| access-key-id-var | R2_ACCESS_KEY_ID |
| secret-access-key-var | R2_SECRET_ACCESS_KEY |
| upload-host | `<account id>.r2.cloudflarestorage.com` |
"""


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
        self.assertEqual(result['store'], 'git-ref')
        self.assertEqual(result['head'], run('git', 'rev-parse', 'HEAD', cwd=self.work))
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


def load_script():
    spec = importlib.util.spec_from_file_location('publish_evidence', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeStore(BaseHTTPRequestHandler):
    """An S3 endpoint on 127.0.0.1 that records each PUT."""

    def do_PUT(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        self.server.requests.append((self.path, dict(self.headers), body))
        status, reply = self.server.reply
        self.send_response(status)
        self.send_header('Content-Length', str(len(reply)))
        self.end_headers()
        self.wfile.write(reply)

    def log_message(self, *args):
        pass


class SigV4Tests(unittest.TestCase):
    def test_matches_the_aws_s3_get_object_example(self):
        headers = load_script().sigv4_headers(
            'GET', 'https://examplebucket.s3.amazonaws.com/test.txt', {'Range': 'bytes=0-9'},
            'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            'AKIAIOSFODNN7EXAMPLE', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
            'us-east-1', 's3', datetime.datetime(2013, 5, 24, tzinfo=datetime.timezone.utc),
        )
        self.assertTrue(headers['authorization'].endswith(
            'Signature=f0e8bdb87c964420e857bd35b5d6ed310bd44f0170aba48dd91039c6036bdb41'))


class R2StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.work = self.tmp / 'work'
        run('git', 'init', '--quiet', '-b', 'claude/feat/login', str(self.work), cwd=self.tmp)
        run('git', 'remote', 'add', 'origin', 'https://github.com/acme/app', cwd=self.work)
        (self.work / 'docs' / 'agents').mkdir(parents=True)
        (self.work / 'docs' / 'agents' / 'evidence.md').write_text(CONFIG)
        run('git', 'add', '.', cwd=self.work)
        run('git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '--quiet',
            '-m', 'init', cwd=self.work)
        self.head = run('git', 'rev-parse', 'HEAD', cwd=self.work)
        self.captures = self.tmp / 'captures'
        self.captures.mkdir()
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), FakeStore)
        self.server.requests = []
        self.server.reply = (200, b'')
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.endpoint = f'http://127.0.0.1:{self.server.server_port}'

    def capture(self, name, data=b'png-bytes'):
        path = self.captures / name
        path.write_bytes(data)
        return path

    def env(self, **overrides):
        env = {k: v for k, v in os.environ.items() if 'proxy' not in k.lower()}
        env.update(SECRETS, NO_PROXY='127.0.0.1,localhost')
        env.update(overrides)
        return {k: v for k, v in env.items() if v is not None}

    def publish(self, *args, env=None):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), '--endpoint', self.endpoint, *map(str, args)],
            cwd=self.work, capture_output=True, text=True, env=env or self.env(),
        )
        for value in SECRETS.values():
            self.assertNotIn(value, result.stdout + result.stderr)
        return result

    def test_uploads_each_file_under_an_unguessable_key_for_the_head(self):
        before = self.capture('login-before.png')
        after = self.capture('login-after.png', b'after-bytes')
        result = self.publish(before, after, '--commit', self.head)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['store'], 'r2')
        self.assertEqual(output['head'], self.head)
        layout = re.compile(
            rf'^acme/app/claude/feat/login/{self.head}/(?P<token>[0-9a-f]{{32}})/$')
        token = layout.match(output['key'])['token']
        keys = [f'acme/app/claude/feat/login/{self.head}/{token}/{n}'
                for n in ('login-before.png', 'login-after.png')]
        self.assertEqual([f['url'] for f in output['files']], [f'{PUBLIC}/{k}' for k in keys])
        self.assertEqual([r[0] for r in self.server.requests],
                         [f'/pr-evidence/{k}' for k in keys])
        path, headers, body = self.server.requests[1]
        self.assertEqual(body, b'after-bytes')
        self.assertEqual(headers['Content-Type'], 'image/png')
        self.assertRegex(
            headers['Authorization'],
            rf'^AWS4-HMAC-SHA256 Credential={SECRETS["R2_ACCESS_KEY_ID"]}/\d{{8}}/auto/s3/'
            r'aws4_request, SignedHeaders=cache-control;content-length;content-type;host;'
            r'x-amz-content-sha256;x-amz-date, Signature=[0-9a-f]{64}$')

    def test_each_publish_writes_new_keys_so_earlier_links_stay(self):
        first = json.loads(self.publish(self.capture('a.png'), '--commit', self.head).stdout)
        second = json.loads(self.publish(self.capture('a.png'), '--commit', self.head).stdout)
        self.assertNotEqual(first['files'][0]['url'], second['files'][0]['url'])
        self.assertEqual(len({r[0] for r in self.server.requests}), 2)

    def test_refuses_a_dirty_tree(self):
        (self.work / 'README.md').write_text('edit')
        result = self.publish(self.capture('a.png'), '--commit', self.head)
        self.assertEqual(result.returncode, 1)
        self.assertIn('uncommitted changes', result.stderr)
        self.assertEqual(self.server.requests, [])

    def test_refuses_a_head_that_is_not_the_captured_commit(self):
        captured = self.head
        run('git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '--quiet',
            '--allow-empty', '-m', 'later', cwd=self.work)
        result = self.publish(self.capture('a.png'), '--commit', captured)
        self.assertEqual(result.returncode, 1)
        self.assertIn(f'the captures show {captured}', result.stderr)
        missing = self.publish(self.capture('b.png'))
        self.assertIn('pass --commit', missing.stderr)
        self.assertEqual(self.server.requests, [])

    def test_errors_never_print_credentials(self):
        self.server.reply = (403, (
            '<Error><Code>SignatureDoesNotMatch</Code>'
            f'<AWSAccessKeyId>{SECRETS["R2_ACCESS_KEY_ID"]}</AWSAccessKeyId></Error>'
        ).encode())
        result = self.publish(self.capture('a.png'), '--commit', self.head)
        self.assertEqual(result.returncode, 1)
        self.assertIn('HTTP 403 (SignatureDoesNotMatch)', result.stderr)
        unset = self.publish(self.capture('a.png'), '--commit', self.head,
                             env=self.env(R2_SECRET_ACCESS_KEY=None))
        self.assertIn('missing credential variables: R2_SECRET_ACCESS_KEY', unset.stderr)

    def test_check_reports_presence_without_values(self):
        result = self.publish('--check', env=self.env(R2_ACCESS_KEY_ID=None))
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['variables'], {
            'R2_ACCOUNT_ID': 'present', 'R2_ACCESS_KEY_ID': 'missing',
            'R2_SECRET_ACCESS_KEY': 'present',
        })
        self.assertEqual(report['upload_host'], '<R2_ACCOUNT_ID>.r2.cloudflarestorage.com')

    def test_store_none_refuses_to_publish(self):
        config = self.tmp / 'none.md'
        config.write_text('| Key | Value |\n| --- | --- |\n| store | none |\n')
        result = self.publish(self.capture('a.png'), '--config', config)
        self.assertEqual(result.returncode, 1)
        self.assertIn('store: none', result.stderr)


if __name__ == '__main__':
    unittest.main()
