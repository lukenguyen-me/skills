"""Verify device_pick.py takes devices in Luke's order, passes over busy ones, and claims what it picks."""

from pathlib import Path
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills' / 'luke-mode' / 'scripts'
spec = importlib.util.spec_from_file_location('device_pick', SCRIPTS / 'device_pick.py')
dp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dp)


def device(kind, id, name=None, os_=(1,), form_factor='tablet', transport='usb', state='connected', serial=''):
    return {'kind': kind, 'platform': dp.PLATFORM_OF[kind], 'id': id, 'name': name or id, 'model': '', 'os': os_,
            'form_factor': form_factor, 'transport': transport, 'state': state, 'serial': serial}


NO_PROBES = {}


class RankTests(unittest.TestCase):
    pool = [device('android-emulator', 'Pixel_Tablet_API_35', os_=(35, 0), state='running', serial='emulator-5554', transport='local'),
            device('ios-simulator', 'SIM-IPAD', 'iPad Pro 13-inch (M5)', os_=(27, 0), state='booted', transport='local'),
            device('ios-device', 'IPAD', 'iPadLuke', os_=(18, 7)),
            device('android-device', 'R5CT1', 'SM-X810', os_=(35,))]

    def rank(self, devices, claimed=None, excluded=(), **filters):
        candidates, skipped = dp.rank(devices, filters, claimed or {}, set(excluded), NO_PROBES)
        return [d['id'] for d in candidates], {d['id']: reason for d, reason in skipped}

    def test_android_device_then_ios_device_then_ios_simulator_then_android_emulator(self):
        self.assertEqual(self.rank(self.pool)[0], ['R5CT1', 'IPAD', 'SIM-IPAD', 'Pixel_Tablet_API_35'])

    def test_a_named_platform_keeps_the_order_within_it(self):
        self.assertEqual(self.rank(self.pool, platform='ios')[0], ['IPAD', 'SIM-IPAD'])
        self.assertEqual(self.rank(self.pool, platform='android')[0], ['R5CT1', 'Pixel_Tablet_API_35'])

    def test_a_claimed_device_is_passed_over_for_the_next_one(self):
        claimed = {'R5CT1': {'label': 'other', 'cwd': '/w'}, 'emulator-5554': {'label': 'x', 'cwd': '/y'}}
        candidates, skipped = self.rank(self.pool, claimed=claimed)
        self.assertEqual(candidates, ['IPAD', 'SIM-IPAD'])
        self.assertEqual(skipped['R5CT1'], 'claimed by other from /w')
        self.assertIn('claimed by x', skipped['Pixel_Tablet_API_35'])   # the running emulator's serial holds the claim

    def test_an_excluded_device_is_passed_over(self):
        candidates, skipped = self.rank(self.pool, excluded={'IPAD'})
        self.assertNotIn('IPAD', candidates)
        self.assertEqual(skipped['IPAD'], "on the pool's skip list")

    def test_within_a_tier_usb_then_booted_then_newest_os_then_name(self):
        devices = [device('ios-simulator', 'B', 'iPhone 16', os_=(26, 0), state='stopped', transport='local'),
                   device('ios-simulator', 'A', 'iPhone 17', os_=(27, 0), state='stopped', transport='local'),
                   device('ios-simulator', 'C', 'iPhone 15', os_=(18, 0), state='booted', transport='local'),
                   device('android-device', 'wifi:5555', os_=(36,), transport='network'),
                   device('android-device', 'USB1', os_=(33,)),
                   device('android-device', 'USB0', os_=(33,))]
        self.assertEqual(self.rank(devices)[0], ['USB0', 'USB1', 'wifi:5555', 'C', 'A', 'B'])

    def test_form_factor_and_minimum_os_filters(self):
        devices = self.pool + [device('ios-device', 'IPHONE', 'Luke iPhone', os_=(26, 6), form_factor='phone')]
        self.assertEqual(self.rank(devices, form_factor='phone')[0], ['IPHONE'])
        candidates, skipped = self.rank(devices, min_ios=(26,), min_sdk=(36,))
        self.assertEqual(candidates, ['IPHONE', 'SIM-IPAD'])
        self.assertEqual(skipped['IPAD'], 'iOS 18.7 is below the minimum 26')
        self.assertEqual(skipped['R5CT1'], 'API 35 is below the minimum 36')

    def test_a_device_with_its_own_reason_is_never_a_candidate(self):
        locked = dict(device('ios-device', 'LOCKED'), reason='locked or unreachable; unlock it and keep it awake')
        self.assertEqual(self.rank([locked])[1], {'LOCKED': 'locked or unreachable; unlock it and keep it awake'})

    def test_requested_device_matches_id_or_name(self):
        self.assertEqual([d['id'] for d in dp.match_requested('ipadluke', self.pool)], ['IPAD'])
        self.assertEqual([d['id'] for d in dp.match_requested('sim-ipad', self.pool)], ['SIM-IPAD'])


def devicectl_row(udid, name, device_type='iPad', reality='physical', os_version='18.7', transport='wired',
                  pairing='paired', developer_mode='enabled'):
    return {'identifier': udid,
            'hardwareProperties': {'udid': udid, 'deviceType': device_type, 'reality': reality, 'marketingName': 'iPad (7th generation)'},
            'deviceProperties': {'name': name, 'osVersionNumber': os_version, 'developerModeStatus': developer_mode},
            'connectionProperties': {'pairingState': pairing, 'transportType': transport}}


DEVICECTL = {'devices': [devicectl_row('IPAD-UDID', 'iPadLuke'),
                         devicectl_row('LOCKED-UDID', 'Luke iPhone', device_type='iPhone', os_version='26.6', transport='localNetwork'),
                         devicectl_row('SIM', 'iPad Pro', reality='simulated'),
                         devicectl_row('UNPAIRED', 'Unpaired', pairing='unpaired'),
                         devicectl_row('NODEV', 'No Developer Mode', developer_mode='disabled')]}

SIMCTL = {'devices': {'com.apple.CoreSimulator.SimRuntime.iOS-27-0': [
    {'udid': 'SIM-IPAD', 'name': 'iPad Pro 13-inch (M5)', 'state': 'Booted', 'isAvailable': True,
     'deviceTypeIdentifier': 'com.apple.CoreSimulator.SimDeviceType.iPad-Pro-13-inch-M5'},
    {'udid': 'SIM-IPHONE', 'name': 'iPhone 17', 'state': 'Shutdown', 'isAvailable': True,
     'deviceTypeIdentifier': 'com.apple.CoreSimulator.SimDeviceType.iPhone-17'},
    {'udid': 'SIM-GONE', 'name': 'iPhone 11', 'state': 'Shutdown', 'isAvailable': False}],
    'com.apple.CoreSimulator.SimRuntime.watchOS-12-0': [{'udid': 'WATCH', 'name': 'Apple Watch', 'state': 'Shutdown'}]}}

ADB_DEVICES = 'List of devices attached\nR5CT1\tdevice\nUNAUTH\tunauthorized\nemulator-5554\tdevice\n'
ADB_PROPS = {'R5CT1': {'sdk': '35', 'model': 'SM-X810', 'size': 'Physical size: 1600x2560\n', 'density': 'Physical density: 320\n'},
             'emulator-5554': {'avd': 'Pixel_Tablet_API_35'}}
TABLET_CFG = 'tag.ids=google_apis_playstore,tablet\nhw.device.name=medium_tablet\nimage.sysdir.1=system-images/android-35/google_apis_playstore_tablet/arm64-v8a/\n'
PHONE_CFG = 'tag.id=google_apis_playstore\nhw.device.name=pixel_8\nimage.sysdir.1=system-images/android-36/google_apis_playstore/arm64-v8a/\n'

XCRUN_STUB = '''#!/usr/bin/env python3
import json, os, sys
fixtures = os.environ['PICK_FIXTURES']
args = sys.argv[1:]
if args[:2] == ['devicectl', 'list']:
    out = args[args.index('--json-output') + 1]
    with open(out, 'w') as f: json.dump({'result': json.load(open(os.path.join(fixtures, 'devicectl.json')))}, f)
elif args[:3] == ['devicectl', 'device', 'info']:
    udid = args[args.index('--device') + 1]
    out = args[args.index('--json-output') + 1]
    with open(out, 'w') as f: json.dump({'result': {'passcodeRequired': udid.startswith('LOCKED')}}, f)
elif args[:2] == ['simctl', 'list']:
    print(open(os.path.join(fixtures, 'simctl.json')).read())
else:
    sys.exit(1)
'''

ADB_STUB = '''#!/usr/bin/env python3
import json, os, sys
fixtures = os.environ['PICK_FIXTURES']
props = json.load(open(os.path.join(fixtures, 'adb_props.json')))
args = sys.argv[1:]
if args == ['devices']:
    print(open(os.path.join(fixtures, 'adb_devices.txt')).read())
elif args[0] == '-s':
    serial, rest = args[1], args[2:]
    p = props.get(serial, {})
    if rest == ['emu', 'avd', 'name']:
        print(p.get('avd', 'KO: unknown') + '\\nOK')
    elif rest == ['shell', 'getprop', 'ro.build.version.sdk']:
        print(p.get('sdk', ''))
    elif rest == ['shell', 'getprop', 'ro.product.model']:
        print(p.get('model', ''))
    elif rest == ['shell', 'wm', 'size']:
        print(p.get('size', ''))
    elif rest == ['shell', 'wm', 'density']:
        print(p.get('density', ''))
    with open(os.path.join(fixtures, 'adb_calls.log'), 'a') as f: f.write(' '.join(args) + '\\n')
'''

EMULATOR_STUB = '''#!/usr/bin/env python3
import sys
if sys.argv[1:] == ['-list-avds']:
    print('INFO    | Storage: ...')
    print('Pixel_Tablet_API_35')
    print('Pixel_8_API_36')
'''


class CliTests(unittest.TestCase):
    """The CLI against stub `xcrun`, `adb`, and `emulator` tools on PATH, so the whole path runs on any host."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.bin, self.fixtures, self.pool = self.root / 'bin', self.root / 'fixtures', self.root / 'pool'
        self.avds = self.root / 'avd'
        for folder in (self.bin, self.fixtures, self.pool):
            folder.mkdir()
        for name, text in (('xcrun', XCRUN_STUB), ('adb', ADB_STUB), ('emulator', EMULATOR_STUB)):
            path = self.bin / name
            path.write_text(text)
            path.chmod(path.stat().st_mode | stat.S_IXUSR)
        (self.fixtures / 'devicectl.json').write_text(json.dumps(DEVICECTL))
        (self.fixtures / 'simctl.json').write_text(json.dumps(SIMCTL))
        (self.fixtures / 'adb_devices.txt').write_text(ADB_DEVICES)
        (self.fixtures / 'adb_props.json').write_text(json.dumps(ADB_PROPS))
        for avd, config in (('Pixel_Tablet_API_35', TABLET_CFG), ('Pixel_8_API_36', PHONE_CFG)):
            (self.avds / f'{avd}.avd').mkdir(parents=True)
            (self.avds / f'{avd}.avd' / 'config.ini').write_text(config)
        self.env = dict(os.environ, PATH=f'{self.bin}:{os.environ["PATH"]}', PICK_FIXTURES=str(self.fixtures),
                        DEVICE_CLAIMS_DIR=str(self.pool), DEVICE_EXCLUDED_FILE=str(self.root / 'excluded.txt'),
                        ANDROID_AVD_HOME=str(self.avds))

    def run_script(self, script, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True, text=True, env=self.env)

    def pick(self, *args):
        result = self.run_script('device_pick.py', 'pick', *args)
        return result.returncode, result.stdout.strip(), result.stderr

    def test_each_pick_takes_the_next_device_in_order_until_none_is_free(self):
        taken = [self.pick('--label', f'run-{n}')[1] for n in range(6)]
        self.assertEqual(taken, ['R5CT1', 'IPAD-UDID', 'SIM-IPAD', 'SIM-IPHONE', 'Pixel_Tablet_API_35', 'Pixel_8_API_36'])
        code, out, err = self.pick()
        self.assertEqual((code, out), (1, ''))
        self.assertIn('PROBLEM: every device is claimed', err)
        self.assertIn('claimed by run-0', err)
        self.assertIn('LOCKED-UDID: locked or unreachable', err)
        self.assertIn('UNAUTH', err)
        self.assertIn('Unpaired (iOS 18.7, tablet, connected) UNPAIRED: not paired', err)

    def test_a_named_platform_takes_its_own_first_device(self):
        self.assertEqual(self.pick('--platform', 'ios')[1], 'IPAD-UDID')
        self.assertEqual(self.pick('--platform', 'ios')[1], 'SIM-IPAD')
        self.assertEqual(self.pick('--platform', 'android', '--min-sdk', '36')[1], 'Pixel_8_API_36')

    def test_a_phone_comes_from_the_simulator_when_the_iphone_is_locked(self):
        code, out, err = self.pick('--form-factor', 'phone')
        self.assertEqual(out, 'SIM-IPHONE')
        self.assertIn('passed over: ios-device Luke iPhone (iOS 26.6, phone, connected) LOCKED-UDID: locked', err)
        self.assertIn('picked ios-simulator iPhone 17 (iOS 27.0, phone, stopped) SIM-IPHONE', err)

    def test_the_skip_list_wins_even_when_the_device_is_requested(self):
        self.run_script('device_claim.py', 'exclude', 'R5CT1', '--note', 'personal')
        self.assertEqual(self.pick()[1], 'IPAD-UDID')
        code, out, err = self.pick('--device', 'R5CT1')
        self.assertEqual((code, out), (1, ''))
        self.assertIn("skip list", err)
        self.assertNotIn('R5CT1 shell', (self.fixtures / 'adb_calls.log').read_text())   # never probed

    def test_a_requested_device_by_name_is_the_only_candidate(self):
        code, out, err = self.pick('--device', 'iPad Pro 13-inch (M5)', '--json')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {'platform': 'ios', 'kind': 'ios-simulator', 'id': 'SIM-IPAD', 'name': 'iPad Pro 13-inch (M5)',
                                           'model': 'iPad Pro 13-inch (M5)', 'form_factor': 'tablet', 'state': 'booted',
                                           'serial': '', 'os': '27.0'})
        self.assertIn('PROBLEM: no device matches', self.pick('--device', 'nope')[2])

    def test_hold_passes_the_device_to_the_command_and_releases_it(self):
        self.pick('--label', 'first')
        held = self.run_script('device_pick.py', 'hold', '--', sys.executable, '-c',
                               'import os; print(os.environ["DEVICE_CLAIM"], os.environ["DEVICE_KIND"], os.environ["DEVICE_NAME"])')
        self.assertEqual((held.returncode, held.stdout.strip()), (0, 'IPAD-UDID ios-device iPadLuke'))
        self.assertEqual(self.pick()[1], 'IPAD-UDID')   # released when the command ended
        emulator = self.run_script('device_pick.py', 'hold', '--platform', 'android', '--form-factor', 'tablet', '--',
                                   sys.executable, '-c', 'import os; print(os.environ["DEVICE_CLAIM"], os.environ["DEVICE_SERIAL"])')
        self.assertEqual(emulator.stdout.strip(), 'Pixel_Tablet_API_35 emulator-5554')

    def test_list_shows_candidates_then_the_rest_with_reasons(self):
        self.pick('--label', 'busy')
        listing = json.loads(self.run_script('device_pick.py', 'list', '--json').stdout)
        by_id = {row['id']: row for row in listing}
        self.assertEqual([row['id'] for row in listing if row['candidate']],
                         ['IPAD-UDID', 'SIM-IPAD', 'SIM-IPHONE', 'Pixel_Tablet_API_35', 'Pixel_8_API_36'])
        self.assertEqual(by_id['R5CT1']['reason'], 'claimed by busy from ' + os.getcwd())
        self.assertEqual(by_id['R5CT1']['name'], 'R5CT1')   # a claimed device is never probed, so it keeps its serial as its name
        self.assertEqual(by_id['UNAUTH']['reason'], 'unauthorized')
        self.assertEqual(by_id['NODEV']['reason'], 'Developer Mode is off')
        self.assertNotIn('SIM-GONE', by_id)
        self.assertNotIn('WATCH', by_id)
        text = self.run_script('device_pick.py', 'list').stdout
        self.assertIn('android-emulator Pixel_Tablet_API_35 (API 35.0, tablet, running as emulator-5554) Pixel_Tablet_API_35', text)

    def test_no_tools_means_no_device_and_a_problem_line(self):
        self.env['PATH'] = str(self.root / 'empty')
        code, out, err = self.pick('--platform', 'android')
        self.assertEqual((code, out), (1, ''))
        self.assertIn('PROBLEM: no device found for --platform android', err)


class ParserTests(unittest.TestCase):
    def test_ios_devices_keep_physical_rows_with_a_reason_for_the_unusable(self):
        devices = {d['id']: d for d in dp.parse_ios_devices(DEVICECTL)}
        self.assertEqual(set(devices), {'IPAD-UDID', 'LOCKED-UDID', 'UNPAIRED', 'NODEV'})
        self.assertEqual(devices['IPAD-UDID']['os'], (18, 7))
        self.assertEqual((devices['LOCKED-UDID']['form_factor'], devices['LOCKED-UDID']['transport']), ('phone', 'network'))
        self.assertEqual(devices['UNPAIRED']['reason'], 'not paired')
        self.assertEqual(dp.parse_ios_devices(None), [])

    def test_simulators_come_from_ios_runtimes_only(self):
        sims = {d['id']: d for d in dp.parse_ios_simulators(SIMCTL)}
        self.assertEqual(set(sims), {'SIM-IPAD', 'SIM-IPHONE'})
        self.assertEqual((sims['SIM-IPAD']['state'], sims['SIM-IPAD']['os'], sims['SIM-IPAD']['form_factor']), ('booted', (27, 0), 'tablet'))

    def test_adb_and_avd_parsing(self):
        self.assertEqual(dp.parse_adb_devices(ADB_DEVICES), [('R5CT1', 'device'), ('UNAUTH', 'unauthorized'), ('emulator-5554', 'device')])
        self.assertTrue(dp.is_network_serial('192.168.1.9:5555'))
        self.assertTrue(dp.is_network_serial('adb-R5CT1-abc._adb-tls-connect._tcp'))
        self.assertFalse(dp.is_network_serial('R5CT1'))
        self.assertEqual(dp.parse_avd_list('INFO    | Storage: x\nPixel_8_API_36\n'), ['Pixel_8_API_36'])
        self.assertEqual(dp.parse_avd_name('Pixel_8_API_36\nOK\n'), 'Pixel_8_API_36')
        self.assertIsNone(dp.parse_avd_name('KO: unknown command\n'))
        tablet = dp.avd_device('T', dp.parse_avd_config(TABLET_CFG), 'emulator-5556')
        self.assertEqual((tablet['os'], tablet['form_factor'], tablet['state'], tablet['serial']), ((35, 0), 'tablet', 'running', 'emulator-5556'))
        phone = dp.avd_device('P', dp.parse_avd_config(PHONE_CFG))
        self.assertEqual((phone['os'], phone['form_factor'], phone['state']), ((36, 0), 'phone', 'stopped'))

    def test_smallest_width_prefers_the_override(self):
        self.assertEqual(dp.smallest_width_dp('Physical size: 1600x2560\nOverride size: 1080x1920\n', 'Physical density: 320\n'), 540)
        self.assertEqual(dp.smallest_width_dp('Physical size: 1600x2560\n', 'Physical density: 320\n'), 800)
        self.assertIsNone(dp.smallest_width_dp('', 'Physical density: 320\n'))


if __name__ == '__main__':
    unittest.main()
