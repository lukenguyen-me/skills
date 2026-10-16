#!/usr/bin/env python3
"""Claim a physical device, simulator, or emulator from the machine's shared device pool.

  device_claim.py claim DEVICE [DEVICE ...] [--label TEXT] [--minutes N | --pid PID] [--wait-minutes N]
  device_claim.py hold  DEVICE [DEVICE ...] [--label TEXT] [--wait-minutes N] -- COMMAND ...
  device_claim.py release DEVICE
  device_claim.py list
  device_claim.py exclude DEVICE [--note TEXT]
  device_claim.py include DEVICE

A DEVICE is the identifier the driver uses: a device or simulator UDID, an AVD name, or an adb serial. `claim` and `hold`
take the first free candidate in the order given and print it. `hold` keeps the claim while COMMAND runs and passes
the device to it in DEVICE_CLAIM. A claim ends when its process exits (`--pid`, `hold`), when its time runs out
(`--minutes`, default 60 for `claim`), or on `release`.

Claims live in DEVICE_CLAIMS_DIR, else ~/Library/Caches/device-claims (macOS) or ~/.cache/device-claims, so every
project and worktree on the machine sees the same pool. Projects may import this file and call claim_first,
live_claims, and release. Standard library only.

`exclude` keeps a device out of the pool for good, such as the owner's personal phone: `claim` and `hold` skip it.
The list lives in DEVICE_EXCLUDED_FILE, else ~/.config/device-claims/excluded.txt, one identifier per line with `#`
comments, outside the cache so a cache cleanup cannot drop it.
"""

import argparse
import contextlib
import datetime
import fcntl
import json
import os
import re
import subprocess
import sys
import time

POLL_SECONDS = 15


def claims_dir():
    configured = os.environ.get('DEVICE_CLAIMS_DIR')
    if configured:
        return configured
    if sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Caches/device-claims')
    return os.path.expanduser('~/.cache/device-claims')


def excluded_path():
    return os.environ.get('DEVICE_EXCLUDED_FILE') or os.path.expanduser('~/.config/device-claims/excluded.txt')


def excluded_devices(path=None):
    """The set of excluded device identifiers."""
    try:
        with open(path or excluded_path()) as handle:
            lines = handle.read().splitlines()
    except OSError:
        return set()
    return {line.split('#', 1)[0].strip() for line in lines} - {''}


def exclude(device, note='', path=None):
    """Add device to the excluded list. Returns False when it was already there."""
    path = path or excluded_path()
    if device in excluded_devices(path):
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a') as handle:
        handle.write(device + (f'   # {note}' if note else '') + '\n')
    return True


def include(device, path=None):
    """Remove device from the excluded list. Returns False when it was not there."""
    path = path or excluded_path()
    if device not in excluded_devices(path):
        return False
    with open(path) as handle:
        lines = handle.read().splitlines()
    kept = [line for line in lines if line.split('#', 1)[0].strip() != device]
    with open(path, 'w') as handle:
        handle.write(''.join(line + '\n' for line in kept))
    return True


def claim_path(directory, device):
    return os.path.join(directory, re.sub(r'[^A-Za-z0-9._-]', '_', device) + '.json')


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


def process_start(pid):
    """`ps -o lstart=` for pid, or None when it is not running. A reused PID has a different start time."""
    try:
        result = subprocess.run(['ps', '-o', 'lstart=', '-p', str(pid)], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = result.stdout.strip()
    return text if result.returncode == 0 and text else None


def is_live(record, now=None, start_of=process_start):
    """A claim with a pid lives while that process does; one with an expiry lives until then."""
    if record.get('pid'):
        recorded = record.get('pid_started')
        return bool(recorded) and start_of(record['pid']) == recorded
    expires = record.get('expires_utc')
    if expires:
        try:
            return (now or utc_now()) < datetime.datetime.fromisoformat(expires)
        except ValueError:
            return False
    return False


@contextlib.contextmanager
def pool_lock(directory):
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, '.lock'), 'a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def read_claim(path):
    try:
        with open(path) as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def live_claims(directory=None):
    """{device: record} for every live claim in the pool."""
    directory = directory or claims_dir()
    claims = {}
    try:
        names = sorted(os.listdir(directory))
    except OSError:
        return claims
    for name in names:
        if name.endswith('.json'):
            record = read_claim(os.path.join(directory, name))
            if record and record.get('device') and is_live(record):
                claims[record['device']] = record
    return claims


def claim_first(candidates, label='', pid=None, minutes=None, directory=None, excluded_file=None):
    """Claim the first free candidate that is not excluded.
    Returns (device, None), or (None, {device: holder record}) when all are taken."""
    directory = directory or claims_dir()
    skipped = excluded_devices(excluded_file)
    holders = {}
    with pool_lock(directory):
        for device in candidates:
            if device in skipped:
                continue
            path = claim_path(directory, device)
            current = read_claim(path)
            if current and is_live(current):
                holders[device] = current
                continue
            now = utc_now()
            record = {'device': device, 'label': label, 'cwd': os.getcwd(),
                      'claimed_utc': now.isoformat(timespec='seconds')}
            if pid:
                record.update(pid=pid, pid_started=process_start(pid))
            else:
                expires = now + datetime.timedelta(minutes=minutes or 60)
                record['expires_utc'] = expires.isoformat(timespec='seconds')
            with open(path, 'w') as handle:
                json.dump(record, handle, indent=2)
                handle.write('\n')
            return device, None
    return None, holders


def release(device, directory=None):
    """Remove the claim on device. Returns the removed record, or None when there was none."""
    directory = directory or claims_dir()
    with pool_lock(directory):
        path = claim_path(directory, device)
        record = read_claim(path)
        with contextlib.suppress(FileNotFoundError):
            os.remove(path)
    return record


def describe(record):
    if record.get('pid'):
        until = f"pid {record['pid']}"
    else:
        until = f"until {record.get('expires_utc')}"
    return f"{record['device']}: {record.get('label') or '(no label)'}, {until}, from {record.get('cwd')}"


def claim_with_wait(candidates, wait_minutes, **kwargs):
    deadline = time.time() + wait_minutes * 60
    while True:
        device, holders = claim_first(candidates, **kwargs)
        if device or time.time() >= deadline:
            return device, holders
        time.sleep(POLL_SECONDS)


def report_taken(holders):
    if not holders:
        print(f'PROBLEM: every candidate device is excluded in {excluded_path()}', file=sys.stderr)
        return
    print('PROBLEM: every candidate device is claimed or excluded:', file=sys.stderr)
    for record in holders.values():
        print('  ' + describe(record), file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)

    p = sub.add_parser('claim', help='claim the first free device and print it')
    p.add_argument('devices', nargs='+')
    p.add_argument('--label', default='')
    owner = p.add_mutually_exclusive_group()
    owner.add_argument('--minutes', type=float, help='claim lifetime (default 60)')
    owner.add_argument('--pid', type=int, help='claim until this process exits')
    p.add_argument('--wait-minutes', type=float, default=0)

    p = sub.add_parser('hold', help='claim the first free device while a command runs')
    p.add_argument('devices', nargs='+')
    p.add_argument('--label', default='')
    p.add_argument('--wait-minutes', type=float, default=0)

    p = sub.add_parser('release', help='end the claim on a device')
    p.add_argument('device')

    sub.add_parser('list', help='print live claims and excluded devices')

    p = sub.add_parser('exclude', help='keep a device out of the pool for good')
    p.add_argument('device')
    p.add_argument('--note', default='')

    p = sub.add_parser('include', help='return an excluded device to the pool')
    p.add_argument('device')

    argv = list(sys.argv[1:] if argv is None else argv)
    rest = argv[argv.index('--') + 1:] if '--' in argv else []
    args = parser.parse_args(argv[:argv.index('--')] if '--' in argv else argv)
    if args.command == 'hold' and not rest:
        parser.error('hold needs `-- COMMAND ...` after the devices')

    if args.command == 'list':
        for record in live_claims().values():
            print(describe(record))
        for device in sorted(excluded_devices()):
            print(f'{device}: excluded')
        return 0
    if args.command == 'exclude':
        added = exclude(args.device, args.note)
        print(f'excluded {args.device}' if added else f'{args.device} was already excluded')
        return 0
    if args.command == 'include':
        removed = include(args.device)
        print(f'included {args.device}' if removed else f'{args.device} was not excluded')
        return 0
    if args.command == 'release':
        record = release(args.device)
        print(f'released {describe(record)}' if record else f'{args.device} had no claim')
        return 0
    if args.command == 'claim':
        device, holders = claim_with_wait(args.devices, args.wait_minutes, label=args.label,
                                          pid=args.pid, minutes=args.minutes)
        if not device:
            report_taken(holders)
            return 1
        print(device)
        return 0

    device, holders = claim_with_wait(args.devices, args.wait_minutes, label=args.label, pid=os.getpid())
    if not device:
        report_taken(holders)
        return 1
    try:
        return subprocess.run(rest, env=dict(os.environ, DEVICE_CLAIM=device)).returncode
    finally:
        release(device)


if __name__ == '__main__':
    sys.exit(main())
