"""Verify device_claim.py hands each run a different free device and frees it when the run ends."""

from pathlib import Path
import datetime
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills' / 'luke-mode' / 'scripts' / 'device_claim.py'
spec = importlib.util.spec_from_file_location('device_claim', SCRIPT)
dc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dc)


class DeviceClaimTests(unittest.TestCase):
    def setUp(self):
        self.pool = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.pool)

    def claim(self, *devices, **kwargs):
        return dc.claim_first(list(devices), directory=self.pool, **kwargs)

    def cli(self, *args):
        env = dict(os.environ, DEVICE_CLAIMS_DIR=self.pool)
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)

    def test_a_second_run_gets_the_next_free_device(self):
        self.assertEqual(self.claim('LARGE', 'SMALL', label='a'), ('LARGE', None))
        self.assertEqual(self.claim('LARGE', 'SMALL', label='b'), ('SMALL', None))

    def test_all_taken_returns_the_holders(self):
        self.claim('LARGE', label='a')
        device, holders = self.claim('LARGE')
        self.assertIsNone(device)
        self.assertEqual(holders['LARGE']['label'], 'a')

    def test_a_claim_frees_when_its_process_exits(self):
        child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])
        self.addCleanup(child.kill)
        self.claim('LARGE', pid=child.pid)
        self.assertIn('LARGE', dc.live_claims(self.pool))
        child.kill()
        child.wait()
        self.assertEqual(self.claim('LARGE'), ('LARGE', None))

    def test_a_timed_claim_frees_when_it_expires(self):
        self.claim('LARGE', minutes=1)
        record = dc.read_claim(dc.claim_path(self.pool, 'LARGE'))
        later = datetime.datetime.fromisoformat(record['expires_utc']) + datetime.timedelta(seconds=1)
        self.assertTrue(dc.is_live(record))
        self.assertFalse(dc.is_live(record, now=later))

    def test_a_reused_pid_does_not_keep_a_claim(self):
        record = {'device': 'LARGE', 'pid': 42, 'pid_started': 'Mon Jan  1 00:00:00 2024'}
        self.assertFalse(dc.is_live(record, start_of=lambda pid: 'Tue Oct 14 09:00:00 2026'))

    def test_release_frees_the_device(self):
        self.claim('LARGE', label='a')
        self.assertEqual(dc.release('LARGE', self.pool)['label'], 'a')
        self.assertEqual(self.claim('LARGE'), ('LARGE', None))

    def test_device_names_with_spaces_and_slashes_are_safe_file_names(self):
        self.assertEqual(self.claim('iPad Pro 13-inch (M5)/x'), ('iPad Pro 13-inch (M5)/x', None))
        self.assertIn('iPad Pro 13-inch (M5)/x', dc.live_claims(self.pool))

    def test_cli_claim_prints_the_device_and_list_shows_it(self):
        self.assertEqual(self.cli('claim', 'LARGE', 'SMALL', '--label', 'strokie-129').stdout.strip(), 'LARGE')
        self.assertIn('LARGE: strokie-129', self.cli('list').stdout)
        taken = self.cli('claim', 'LARGE')
        self.assertEqual(taken.returncode, 1)
        self.assertIn('strokie-129', taken.stderr)

    def test_cli_hold_passes_the_device_and_releases_it(self):
        self.cli('claim', 'LARGE')
        held = self.cli('hold', 'LARGE', 'SMALL', '--', sys.executable, '-c',
                        'import os; print(os.environ["DEVICE_CLAIM"])')
        self.assertEqual((held.returncode, held.stdout.strip()), (0, 'SMALL'))
        self.assertNotIn('SMALL', dc.live_claims(self.pool))


if __name__ == '__main__':
    unittest.main()
