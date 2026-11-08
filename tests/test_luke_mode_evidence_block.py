"""Verify evidence_block.py renders the Before | After block and replaces only it."""

from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'luke-mode'
SCRIPT = SKILL / 'scripts' / 'evidence_block.py'
WORKFLOW = SKILL / 'templates' / 'luke-mode-evidence-block.yml'
PUBLIC = 'https://evidence.example.com'
HEAD = '8d41c2e0a1b2c3d4e5f60718293a4b5c6d7e8f90'
START = '<!-- luke-mode-evidence:start -->'
END = '<!-- luke-mode-evidence:end -->'


def output(*names, head=HEAD):
    return {'store': 'r2', 'head': head,
            'files': [{'name': n, 'url': f'https://e.example/{n}'} for n in names]}


class EvidenceBlockTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def run_block(self, outputs, body, *args):
        paths = []
        for index, out in enumerate(outputs):
            path = self.tmp / f'out-{index}.json'
            path.write_text(json.dumps(out))
            paths.append(str(path))
        return subprocess.run([sys.executable, str(SCRIPT), *paths, *args],
                              input=body, capture_output=True, text=True)

    def test_renders_pairs_singles_and_videos_with_the_head(self):
        result = self.run_block([output(
            'settings-before-dark.png', 'settings-after-dark.png',
            'onboarding-after.png', 'checkout.gif', 'checkout.mp4',
        )], '', '--block-only')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '\n'.join([
            START,
            f'Captures show commit {HEAD}.',
            '',
            '| Before | After |',
            '| --- | --- |',
            '| ![settings before dark](https://e.example/settings-before-dark.png) '
            '| ![settings after dark](https://e.example/settings-after-dark.png) |',
            '',
            '![onboarding after](https://e.example/onboarding-after.png)',
            '',
            '![checkout](https://e.example/checkout.gif)',
            '',
            '[checkout.mp4](https://e.example/checkout.mp4)',
            '',
            END,
        ]) + '\n')

    def test_replaces_only_the_marked_block(self):
        body = f'## Summary\n\nText.\n\n## Evidence\n\nCaption.\n\n{START}\nold\n{END}\n\nNot captured: x.\n'
        result = self.run_block([output('a-before.png', 'a-after.png')], body)
        self.assertEqual(result.returncode, 0, result.stderr)
        head, block_and_tail = result.stdout.split(START)
        self.assertEqual(head, '## Summary\n\nText.\n\n## Evidence\n\nCaption.\n\n')
        self.assertNotIn('old', block_and_tail)
        self.assertTrue(block_and_tail.endswith(f'{END}\n\nNot captured: x.\n'))
        again = self.run_block([output('a-before.png', 'a-after.png')], result.stdout)
        self.assertEqual(again.stdout, result.stdout)

    def test_inserts_under_the_evidence_heading_when_markers_are_absent(self):
        body = '## Summary\n\nText.\n\n## Evidence\n\nNot captured: x.\n'
        result = self.run_block([output('a.png')], body)
        self.assertTrue(result.stdout.startswith(f'## Summary\n\nText.\n\n## Evidence\n\n{START}\n'))
        self.assertTrue(result.stdout.endswith(f'{END}\n\nNot captured: x.\n'))

    def test_refuses_captures_of_different_commits_and_a_half_block(self):
        mixed = self.run_block([output('a.png'), output('b.png', head='f' * 40)], '')
        self.assertEqual(mixed.returncode, 1)
        self.assertIn('different commits', mixed.stderr)
        half = self.run_block([output('a.png')], f'{START}\nold\n')
        self.assertEqual(half.returncode, 1)
        self.assertIn('only one of', half.stderr)


def store_output(*names, head=HEAD, base=f'{PUBLIC}/acme/app/feat/{HEAD}/0f0f'):
    return {'store': 'r2', 'head': head,
            'files': [{'name': n, 'url': f'{base}/{n}'} for n in names]}


class AllowedPrefixTests(unittest.TestCase):
    """--allow-url-prefix lets the block embed only the project's own store."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def run_block(self, out, prefix=PUBLIC):
        path = self.tmp / 'out.json'
        path.write_text(json.dumps(out))
        return subprocess.run([sys.executable, str(SCRIPT), str(path), '--block-only',
                               '--allow-url-prefix', prefix],
                              capture_output=True, text=True)

    def test_accepts_files_under_the_prefix(self):
        result = self.run_block(store_output('a-before.png', 'a-after.png'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'![a before]({PUBLIC}/acme/app/feat/{HEAD}/0f0f/a-before.png)', result.stdout)

    def test_refuses_anything_outside_the_store(self):
        cases = {
            'another host': store_output('a.png', base='https://evil.example/x'),
            'a look-alike host': store_output('a.png', base=f'{PUBLIC}.evil.example/x'),
            'markdown in the URL': {'head': HEAD, 'files': [{
                'name': 'a.png', 'url': f'{PUBLIC}/x/a.png) ![t](https://evil.example/t.png'}]},
            'a path that does not end in the name': {'head': HEAD, 'files': [{
                'name': 'a.png', 'url': f'{PUBLIC}/x/b.png'}]},
            'a parent directory': store_output('a.png', base=f'{PUBLIC}/../x'),
            'markdown in the name': {'head': HEAD, 'files': [{
                'name': 'a](x).png', 'url': f'{PUBLIC}/x/a](x).png'}]},
            'a short head': store_output('a.png', head='8d41c2e'),
            'a missing url': {'head': HEAD, 'files': [{'name': 'a.png'}]},
        }
        for label, out in cases.items():
            with self.subTest(label):
                result = self.run_block(out)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertTrue(result.stderr.startswith('evidence_block: '), result.stderr)

    def test_refuses_a_prefix_that_is_not_a_plain_https_url(self):
        for prefix in ('http://evidence.example.com', 'https://evidence.example.com/a b', ''):
            with self.subTest(prefix):
                self.assertEqual(self.run_block(store_output('a.png'), prefix).returncode, 1)


def workflow_script():
    """Return the shell of the workflow's run step, as the runner sees it."""
    lines = WORKFLOW.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == 'run: |')
    indent = len(lines[start]) - len(lines[start].lstrip())
    body = []
    for line in lines[start + 1:]:
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        body.append(line)
    return textwrap.dedent('\n'.join(body)) + '\n'


class BlockWorkflowTests(unittest.TestCase):
    """Run the workflow's step in a project checkout, with a stub gh on PATH."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.repo = self.tmp / 'repo'
        shutil.copytree(SKILL / 'scripts', self.repo / '.agents/skills/luke-mode/scripts')
        (self.repo / 'docs/agents').mkdir(parents=True)
        (self.repo / 'docs/agents/evidence.md').write_text(
            f'| Key | Value |\n| --- | --- |\n| store | r2 |\n| bucket | b |\n'
            f'| public-url | {PUBLIC} |\n')
        subprocess.run(['git', 'init', '--quiet', str(self.repo)], check=True)
        bin_dir = self.tmp / 'bin'
        bin_dir.mkdir()
        self.state = self.tmp / 'gh'
        self.state.mkdir()
        (self.state / 'body.md').write_text('## Summary\n\nText.\n\n## Evidence\n\nNot captured: x.\n')
        gh = bin_dir / 'gh'
        gh.write_text(textwrap.dedent(f"""\
            #!/bin/sh
            echo "$*" >> {self.state}/calls
            case "$1 $2" in
              "pr view") cat {self.state}/body.md ;;
              "pr edit") cp "$5" {self.state}/body.md ;;
            esac
            """))
        gh.chmod(0o755)
        self.env = {**os.environ, 'PATH': f'{bin_dir}:{os.environ["PATH"]}',
                    'RUNNER_TEMP': str(self.tmp), 'GITHUB_STEP_SUMMARY': str(self.tmp / 'summary.md'),
                    'GH_TOKEN': 'x', 'GH_REPO': 'acme/app'}

    def run_step(self, pr, published):
        return subprocess.run(['bash', '-c', workflow_script()], cwd=self.repo,
                              env={**self.env, 'PR': pr, 'PUBLISHED': json.dumps(published)},
                              capture_output=True, text=True)

    def test_writes_the_block_into_the_pr_body_and_the_summary(self):
        result = self.run_step('42', store_output('a-before.png', 'a-after.png'))
        self.assertEqual(result.returncode, 0, result.stderr)
        body = (self.state / 'body.md').read_text()
        self.assertIn(f'## Evidence\n\n{START}\nCaptures show commit {HEAD}.', body)
        self.assertIn('| Before | After |', body)
        self.assertTrue(body.endswith(f'{END}\n\nNot captured: x.\n'))
        self.assertIn(START, (self.tmp / 'summary.md').read_text())
        self.assertIn('pr edit 42 --body-file', (self.state / 'calls').read_text())

    def test_refuses_a_url_outside_the_store_and_leaves_the_body(self):
        before = (self.state / 'body.md').read_text()
        result = self.run_step('42', store_output('a.png', base='https://evil.example/x'))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.state / 'body.md').read_text(), before)
        self.assertNotIn('pr edit', (self.state / 'calls').read_text())

    def test_refuses_a_pr_that_is_not_a_number(self):
        result = self.run_step('42; touch pwned', store_output('a.png'))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.state / 'calls').exists())
        self.assertFalse((self.repo / 'pwned').exists())

    def test_refuses_a_project_whose_store_is_not_r2(self):
        (self.repo / 'docs/agents/evidence.md').write_text('| Key | Value |\n| --- | --- |\n| store | git-ref |\n')
        result = self.run_step('42', store_output('a.png'))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('does not set store: r2', result.stderr)
        self.assertFalse((self.state / 'calls').exists())


if __name__ == '__main__':
    unittest.main()
