#!/usr/bin/env python3
"""Pick and claim a device for an automated run from the machine's device pool, in Luke's order.

  device_pick.py pick [FILTERS] [--label TEXT] [--minutes N | --pid PID] [--wait-minutes N] [--json]
  device_pick.py hold [FILTERS] [--label TEXT] [--wait-minutes N] -- COMMAND ...
  device_pick.py list [FILTERS] [--json]

  FILTERS: [--platform ios|android|any] [--form-factor phone|tablet|any] [--min-ios X.Y] [--min-sdk N] [--device ID|NAME]

The order is Android device, iOS device, iOS simulator, Android emulator: a physical device runs the app on its own
hardware, and an Android emulator costs the Mac more than an iOS simulator. `--platform` keeps that order within one
platform when the task names it. Within a tier: a USB device before a network one, a booted simulator or a running
emulator before a stopped one, then the newest OS, then the name.

A device is passed over, never waited for, when it is claimed by another run, on the pool's skip list, locked
(iOS), unauthorized or offline (adb), or below `--min-ios` / `--min-sdk`; the next candidate is taken instead. Every
candidate claimed or excluded is a failure with a `PROBLEM:` line, unless `--wait-minutes N` is set. `--device`
takes one device by identifier or name and claims that one only; the skip list still wins.

`pick` claims the device (see device_claim.py: `--pid` or `--minutes`, default 60) and prints its identifier, or with
`--json` one object: platform, kind, id, name, os, form_factor, state, serial. `hold` keeps the claim while COMMAND
runs, with DEVICE_CLAIM (the identifier), DEVICE_PLATFORM, DEVICE_KIND, DEVICE_NAME, and DEVICE_SERIAL (the adb
serial, empty for a stopped AVD) in its environment. `list` prints every device the tools report, in order, with the
reason each one is not a candidate. Standard library only; projects may import this file and call `pick_device`.

Identifiers are what the drivers take: a UDID for an iOS device or simulator, an adb serial for an Android device, an
AVD name for an emulator. The tools are `xcrun devicectl` and `xcrun simctl` (macOS), `adb` and `emulator` (on PATH
or under ANDROID_HOME, ANDROID_SDK_ROOT, or ~/Library/Android/sdk), and the AVD files under ANDROID_AVD_HOME or
~/.android/avd. A missing tool leaves its platform out.
"""

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

TIERS = ['android-device', 'ios-device', 'ios-simulator', 'android-emulator']
PLATFORM_OF = {'android-device': 'android', 'ios-device': 'ios', 'ios-simulator': 'ios', 'android-emulator': 'android'}
TABLET_MIN_WIDTH_DP = 600
POLL_SECONDS = 15
HERE = os.path.dirname(os.path.realpath(__file__))


# ---------------------------------------------------------------- the pool

def claims_module():
    spec = importlib.util.spec_from_file_location('device_claim', os.path.join(HERE, 'device_claim.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------- tools

def sh(args, timeout=60):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return subprocess.CompletedProcess(args, 1, '', '')


def android_sdk():
    for name in ('ANDROID_HOME', 'ANDROID_SDK_ROOT'):
        if os.environ.get(name):
            return os.environ[name]
    return os.path.expanduser('~/Library/Android/sdk')


def tool_path(name, subdir):
    found = shutil.which(name)
    if found:
        return found
    candidate = os.path.join(android_sdk(), subdir, name)
    return candidate if os.path.isfile(candidate) else None


def avd_home():
    if os.environ.get('ANDROID_AVD_HOME'):
        return os.environ['ANDROID_AVD_HOME']
    return os.path.join(os.environ.get('ANDROID_USER_HOME') or os.path.expanduser('~/.android'), 'avd')


def devicectl_json(*args, timeout=60):
    """The `result` of `xcrun devicectl <args> --json-output <file>`, or None when it failed."""
    handle, path = tempfile.mkstemp(prefix='device-pick-', suffix='.json')
    os.close(handle)
    try:
        if sh(['xcrun', 'devicectl', *args, '--json-output', path, '--quiet'], timeout=timeout).returncode != 0:
            return None
        with open(path) as stream:
            return json.load(stream).get('result')
    except (OSError, ValueError):
        return None
    finally:
        os.remove(path)


# ---------------------------------------------------------------- parsers (pure)

def version_tuple(text):
    return tuple(int(n) for n in re.findall(r'\d+', text or ''))


def version_text(version):
    return '.'.join(str(n) for n in version) if version else '?'


def parse_ios_devices(result):
    """Paired physical devices in Developer Mode from `devicectl list devices`; other rows carry a `reason`."""
    devices = []
    for row in (result or {}).get('devices', []):
        hardware = row.get('hardwareProperties') or {}
        properties = row.get('deviceProperties') or {}
        connection = row.get('connectionProperties') or {}
        if hardware.get('reality') != 'physical':
            continue
        device = {'kind': 'ios-device', 'platform': 'ios', 'id': hardware.get('udid') or row.get('identifier'),
                  'name': properties.get('name') or '', 'model': hardware.get('marketingName') or hardware.get('productType') or '',
                  'os': version_tuple(properties.get('osVersionNumber')), 'form_factor': form_factor_of_apple(hardware.get('deviceType')),
                  'transport': 'usb' if connection.get('transportType') == 'wired' else 'network', 'state': 'connected', 'serial': ''}
        if connection.get('pairingState') != 'paired':
            device['reason'] = 'not paired'
        elif properties.get('developerModeStatus') != 'enabled':
            device['reason'] = 'Developer Mode is off'
        devices.append(device)
    return devices


def form_factor_of_apple(device_type):
    text = (device_type or '').lower()
    return 'tablet' if 'ipad' in text else 'phone' if 'iphone' in text else 'other'


def parse_ios_simulators(listing):
    """Available iOS simulators from `simctl list devices available --json`."""
    simulators = []
    for runtime, rows in (listing or {}).get('devices', {}).items():
        match = re.search(r'\.iOS-(\d+(?:-\d+)*)$', runtime)
        if not match:
            continue
        version = tuple(int(n) for n in match.group(1).split('-'))
        for row in rows:
            if not row.get('isAvailable', True):
                continue
            name = row.get('name') or ''
            simulators.append({'kind': 'ios-simulator', 'platform': 'ios', 'id': row['udid'], 'name': name, 'model': name,
                               'os': version, 'form_factor': form_factor_of_apple(row.get('deviceTypeIdentifier') or name),
                               'transport': 'local', 'state': 'booted' if row.get('state') == 'Booted' else 'stopped', 'serial': ''})
    return simulators


def parse_adb_devices(text):
    """[(serial, state)] from `adb devices`."""
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and not line.startswith(('List of', '*')):
            rows.append((parts[0], parts[1]))
    return rows


def is_emulator_serial(serial):
    return serial.startswith('emulator-')


def is_network_serial(serial):
    """A Wi-Fi or mDNS adb serial: `192.168.1.9:5555`, `localhost:5555`, `adb-XXXX._adb-tls-connect._tcp`."""
    return ':' in serial or '_adb-tls' in serial or serial.startswith('adb-')


def parse_wm_pair(text, label):
    found = {}
    for line in text.splitlines():
        match = re.match(rf'\s*(Physical|Override) {label}:\s*(\d+)(?:x(\d+))?', line)
        if match:
            found[match.group(1)] = (int(match.group(2)), int(match.group(3) or match.group(2)))
    return found.get('Override') or found.get('Physical')


def smallest_width_dp(size_text, density_text):
    """Smallest width in dp from `wm size` and `wm density` (an override beats the physical value); None when unreadable."""
    size, density = parse_wm_pair(size_text, 'size'), parse_wm_pair(density_text, 'density')
    if not size or not density or density[0] <= 0:
        return None
    return min(size) * 160 // density[0]


def parse_avd_list(text):
    """AVD names from `emulator -list-avds`, without the `INFO |` lines the emulator may print."""
    return [line.strip() for line in text.splitlines() if re.fullmatch(r'[\w.\-]+', line.strip())]


def parse_avd_config(text):
    config = {}
    for line in text.splitlines():
        key, sep, value = line.partition('=')
        if sep and key.strip() and not key.lstrip().startswith('#'):
            config[key.strip()] = value.strip()
    return config


def parse_avd_name(output):
    """The AVD name from `adb -s <serial> emu avd name` (first line; None on `KO`)."""
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[0] if lines and not lines[0].startswith('KO') else None


def avd_device(name, config, serial=''):
    match = re.search(r'android-(\d+)(?:\.(\d+))?', config.get('image.sysdir.1', ''))
    api = (int(match.group(1)), int(match.group(2) or 0)) if match else ()
    tablet = any('tablet' in config.get(key, '').lower() for key in ('tag.ids', 'tag.id', 'hw.device.name'))
    return {'kind': 'android-emulator', 'platform': 'android', 'id': name, 'name': name, 'model': config.get('hw.device.name', ''),
            'os': api, 'form_factor': 'tablet' if tablet else 'phone', 'transport': 'local',
            'state': 'running' if serial else 'stopped', 'serial': serial}


# ---------------------------------------------------------------- discovery (tools)

def discover_ios_devices():
    if not shutil.which('xcrun'):
        return []
    return parse_ios_devices(devicectl_json('list', 'devices'))


def ios_device_unlocked(udid):
    """False when the device asks for its passcode now: a locked device cannot run UI tests."""
    result = devicectl_json('device', 'info', 'lockState', '--device', udid, timeout=30)
    return bool(result) and not result.get('passcodeRequired', True)


def discover_ios_simulators():
    if not shutil.which('xcrun'):
        return []
    try:
        return parse_ios_simulators(json.loads(sh(['xcrun', 'simctl', 'list', 'devices', 'available', '--json']).stdout))
    except ValueError:
        return []


def adb(serial, *args, timeout=15):
    return sh([tool_path('adb', 'platform-tools'), '-s', serial, *args], timeout=timeout).stdout


def discover_android():
    """Physical adb devices and AVDs. A running emulator's AVD carries its serial."""
    adb_path = tool_path('adb', 'platform-tools')
    rows = parse_adb_devices(sh([adb_path, 'devices']).stdout) if adb_path else []
    devices, running = [], {}
    for serial, state in rows:
        if is_emulator_serial(serial):
            name = parse_avd_name(adb(serial, 'emu', 'avd', 'name'))
            if name:
                running[name] = serial
            continue
        device = {'kind': 'android-device', 'platform': 'android', 'id': serial, 'name': serial, 'model': '', 'os': (),
                  'form_factor': 'unknown', 'transport': 'network' if is_network_serial(serial) else 'usb',
                  'state': state, 'serial': serial}
        if state != 'device':
            device['reason'] = state   # unauthorized, offline
        devices.append(device)
    emulator = tool_path('emulator', 'emulator')
    names = parse_avd_list(sh([emulator, '-list-avds'], timeout=30).stdout) if emulator else []
    for name in names:
        devices.append(avd_device(name, read_avd_config(name), running.get(name, '')))
    return devices


def read_avd_config(name):
    home = avd_home()
    directory = os.path.join(home, name + '.avd')
    try:
        with open(os.path.join(home, name + '.ini')) as handle:
            directory = parse_avd_config(handle.read()).get('path') or directory
    except OSError:
        pass
    try:
        with open(os.path.join(directory, 'config.ini')) as handle:
            return parse_avd_config(handle.read())
    except OSError:
        return {}


def probe_android_device(device):
    """Fill in API, model, and form factor from the device itself; only for a device that may be picked."""
    api = adb(device['id'], 'shell', 'getprop', 'ro.build.version.sdk').strip()
    device['os'] = (int(api),) if api.isdigit() else ()
    device['model'] = adb(device['id'], 'shell', 'getprop', 'ro.product.model').strip()
    device['name'] = device['model'] or device['id']
    width = smallest_width_dp(adb(device['id'], 'shell', 'wm', 'size'), adb(device['id'], 'shell', 'wm', 'density'))
    device['form_factor'] = 'unknown' if width is None else 'tablet' if width >= TABLET_MIN_WIDTH_DP else 'phone'


def probe_ios_device(device):
    if not ios_device_unlocked(device['id']):
        device['reason'] = 'locked or unreachable; unlock it and keep it awake'


PROBES = {'android-device': probe_android_device, 'ios-device': probe_ios_device}


def discover():
    return discover_ios_devices() + discover_ios_simulators() + discover_android()


# ---------------------------------------------------------------- ranking (pure)

def rank_key(device):
    return (TIERS.index(device['kind']), device['transport'] == 'network', device['state'] not in ('booted', 'running'),
            tuple(-n for n in device['os']), device['name'], device['id'])


def is_claimed(device, claimed):
    return device['id'] in claimed or (device['serial'] and device['serial'] in claimed)


def reason_against(device, filters, claimed, excluded):
    """Why the device is not a candidate under `filters` (platform, form_factor, min_ios, min_sdk), or None."""
    if device['id'] in excluded:
        return 'on the pool\'s skip list'
    if filters.get('platform', 'any') not in ('any', device['platform']):
        return f"not {filters['platform']}"
    if device.get('reason'):
        return device['reason']
    if is_claimed(device, claimed):
        holder = claimed.get(device['id']) or claimed.get(device['serial']) or {}
        return f"claimed by {holder.get('label') or '(no label)'} from {holder.get('cwd')}"
    return None


def reason_against_probed(device, filters):
    """The filters that need the probed details: form factor and minimum OS."""
    wanted = filters.get('form_factor', 'any')
    if wanted != 'any' and device['form_factor'] != wanted:
        return f"a {device['form_factor']}, not a {wanted}"
    minimum = filters.get('min_ios') if device['platform'] == 'ios' else filters.get('min_sdk')
    if minimum and device['os'] < minimum:
        return f"{os_label(device)} is below the minimum {version_text(minimum)}"
    return device.get('reason')


def os_label(device):
    return ('iOS ' if device['platform'] == 'ios' else 'API ') + version_text(device['os'])


def rank(devices, filters, claimed, excluded, probes=None):
    """(candidates in order, [(device, reason)] for the rest). `probes` fills in details for a device that may be picked."""
    probes = PROBES if probes is None else probes
    candidates, skipped = [], []
    for device in sorted(devices, key=rank_key):
        reason = reason_against(device, filters, claimed, excluded)
        if reason is None and device['kind'] in probes:
            probes[device['kind']](device)
            reason = reason_against_probed(device, filters)
        elif reason is None:
            reason = reason_against_probed(device, filters)
        if reason:
            skipped.append((device, reason))
        else:
            candidates.append(device)
    return sorted(candidates, key=rank_key), skipped


def match_requested(requested, devices):
    wanted = requested.strip().lower()
    return [d for d in devices if wanted in (d['id'].lower(), d['name'].lower())]


# ---------------------------------------------------------------- picking

def pick_device(filters, label='', pid=None, minutes=None, requested=None, discover_devices=None, pool=None, probes=None):
    """Claim the first free candidate. Returns (device, skipped, holders): device is None when nothing was free."""
    pool = pool or claims_module()
    devices = (discover_devices or discover)()
    if requested:
        devices = match_requested(requested, devices)
        if not devices:
            return None, [], {}
    candidates, skipped = rank(devices, filters, pool.live_claims(), pool.excluded_devices(), probes)
    by_id = {d['id']: d for d in candidates}
    chosen, holders = pool.claim_first(list(by_id), label=label, pid=pid, minutes=minutes)
    return (by_id[chosen] if chosen else None), skipped, (holders or {})


def pick_with_wait(wait_minutes, **kwargs):
    deadline = time.time() + wait_minutes * 60
    while True:
        device, skipped, holders = pick_device(**kwargs)
        if device or time.time() >= deadline:
            return device, skipped, holders
        time.sleep(POLL_SECONDS)


def describe(device):
    state = device['state'] + (f" as {device['serial']}" if device['serial'] and device['kind'] == 'android-emulator' else '')
    return f"{device['kind']} {device['name']} ({os_label(device)}, {device['form_factor']}, {state}) {device['id']}"


def public(device):
    return {key: device[key] for key in ('platform', 'kind', 'id', 'name', 'model', 'form_factor', 'state', 'serial')} | {
        'os': version_text(device['os'])}


def report_skipped(skipped):
    for device, reason in skipped:
        print(f'passed over: {describe(device)}: {reason}', file=sys.stderr)


def report_none(skipped, requested, filters):
    if requested:
        print(f'PROBLEM: no device matches {requested!r}' + (' as a candidate' if skipped else ''), file=sys.stderr)
    elif skipped:
        print('PROBLEM: every device is claimed, excluded, or outside the filters (see the passed over lines)', file=sys.stderr)
    else:
        print(f"PROBLEM: no device found for --platform {filters.get('platform', 'any')}; is the tool installed and a device "
              'connected, a simulator or AVD created?', file=sys.stderr)


def add_filters(parser):
    parser.add_argument('--platform', choices=['ios', 'android', 'any'], default='any')
    parser.add_argument('--form-factor', choices=['phone', 'tablet', 'any'], default='any')
    parser.add_argument('--min-ios', type=version_tuple, default=(), help='lowest iOS version, such as 17.0')
    parser.add_argument('--min-sdk', type=version_tuple, default=(), help='lowest Android API level, such as 29')
    parser.add_argument('--device', help='one device by identifier or name, instead of the order')


def filters_of(args):
    return {'platform': args.platform, 'form_factor': args.form_factor, 'min_ios': args.min_ios, 'min_sdk': args.min_sdk}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)

    p = sub.add_parser('pick', help='claim the first free device in order and print its identifier')
    add_filters(p)
    p.add_argument('--label', default='')
    owner = p.add_mutually_exclusive_group()
    owner.add_argument('--minutes', type=float, help='claim lifetime (default 60)')
    owner.add_argument('--pid', type=int, help='claim until this process exits')
    p.add_argument('--wait-minutes', type=float, default=0)
    p.add_argument('--json', action='store_true')

    p = sub.add_parser('hold', help='claim the first free device while a command runs')
    add_filters(p)
    p.add_argument('--label', default='')
    p.add_argument('--wait-minutes', type=float, default=0)

    p = sub.add_parser('list', help='print every device in order, with why each one is not a candidate')
    add_filters(p)
    p.add_argument('--json', action='store_true')

    argv = list(sys.argv[1:] if argv is None else argv)
    rest = argv[argv.index('--') + 1:] if '--' in argv else []
    args = parser.parse_args(argv[:argv.index('--')] if '--' in argv else argv)
    if args.command == 'hold' and not rest:
        parser.error('hold needs `-- COMMAND ...`')
    filters = filters_of(args)
    pool = claims_module()

    if args.command == 'list':
        devices = match_requested(args.device, discover()) if args.device else discover()
        candidates, skipped = rank(devices, filters, pool.live_claims(), pool.excluded_devices())
        if args.json:
            print(json.dumps([public(d) | {'candidate': True} for d in candidates] +
                             [public(d) | {'candidate': False, 'reason': reason} for d, reason in skipped], indent=2))
            return 0
        for device in candidates:
            print(describe(device))
        for device, reason in skipped:
            print(f'{describe(device)}: {reason}')
        if not devices:
            print('no device found')
        return 0

    if args.command == 'pick':
        device, skipped, holders = pick_with_wait(args.wait_minutes, filters=filters, label=args.label, pid=args.pid,
                                                  minutes=args.minutes, requested=args.device, pool=pool)
        report_skipped(skipped)
        if not device:
            report_none(skipped, args.device, filters)
            return 1
        print(f'picked {describe(device)}', file=sys.stderr)
        print(json.dumps(public(device)) if args.json else device['id'])
        return 0

    device, skipped, holders = pick_with_wait(args.wait_minutes, filters=filters, label=args.label, pid=os.getpid(),
                                              requested=args.device, pool=pool)
    report_skipped(skipped)
    if not device:
        report_none(skipped, args.device, filters)
        return 1
    print(f'picked {describe(device)}', file=sys.stderr)
    env = dict(os.environ, DEVICE_CLAIM=device['id'], DEVICE_PLATFORM=device['platform'], DEVICE_KIND=device['kind'],
               DEVICE_NAME=device['name'], DEVICE_SERIAL=device['serial'])
    try:
        return subprocess.run(rest, env=env).returncode
    finally:
        pool.release(device['id'])


if __name__ == '__main__':
    sys.exit(main())
