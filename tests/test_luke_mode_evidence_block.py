"""Verify evidence_block.py renders the Before | After block and replaces only it."""

from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills' / 'luke-mode' / 'scripts' / 'evidence_block.py'
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


if __name__ == '__main__':
    unittest.main()
