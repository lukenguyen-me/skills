"""Verify Luke Mode installs as one skill whose links resolve from any location."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'skills' / 'luke-mode'


class BundleTests(unittest.TestCase):
    def test_bundle_has_one_skill_entry_point(self):
        # `npx skills add --full-depth` lists every nested SKILL.md as its own skill.
        self.assertEqual(list(SOURCE.rglob('SKILL.md')), [SOURCE / 'SKILL.md'])

    def test_relative_links_stay_inside_the_bundle(self):
        for markdown in SOURCE.rglob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)', markdown.read_text()):
                path = link.split('#', 1)[0]
                if not path or path.startswith(('https://', 'http://')):
                    continue
                target = (markdown.parent / path).resolve()
                with self.subTest(file=markdown.relative_to(SOURCE), link=link):
                    self.assertTrue(target.exists())
                    self.assertTrue(target.is_relative_to(SOURCE.resolve()))


if __name__ == '__main__':
    unittest.main()
