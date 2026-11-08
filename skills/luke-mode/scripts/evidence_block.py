#!/usr/bin/env python3
"""Render the PR Evidence block from publish output and put it in a PR body.

Reads one or more JSON outputs of publish_evidence.py (any store) and the
current PR body, and prints the body with only the marked block replaced:

    <!-- luke-mode-evidence:start -->
    ...
    <!-- luke-mode-evidence:end -->

Files pair by name: `settings-before-dark.png` and `settings-after-dark.png`
form one Before | After row. Other images show alone, and videos show as links.
When the markers are absent, the block goes under the body's `## Evidence`
heading, or at the end. A session and a CI workflow share this renderer.

--allow-url-prefix makes the block hold only files under that URL, with safe
names and paths, and a head that is a full commit SHA. The dispatched block
workflow passes the project's public URL, so a caller can embed images from
the project's own store and nowhere else.
"""

import argparse
import json
import re
import sys
from pathlib import Path

VIDEO = {'.mp4', '.webm', '.mov'}
ROLES = ('before', 'after')
DEFAULT_MARKER = 'luke-mode-evidence'
SAFE_NAME = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*$')
SAFE_PATH = re.compile(r'^[A-Za-z0-9._~/-]+$')
FULL_SHA = re.compile(r'^[0-9a-f]{40}$')


class BlockError(Exception):
    pass


def markers(name):
    return f'<!-- {name}:start -->', f'<!-- {name}:end -->'


def split_role(filename):
    """Return (pair key, role) for a file name; role is before, after or None."""
    path = Path(filename)
    parts = path.stem.split('-')
    for role in ROLES:
        if role in parts:
            rest = [p for p in parts if p != role]
            return '-'.join(rest) + path.suffix.lower(), role
    return path.stem + path.suffix.lower(), None


def alt_text(filename):
    return Path(filename).stem.replace('-', ' ').replace('_', ' ')


def check_allowed(head, files, prefix):
    """Refuse anything but safe files under prefix, so the block embeds only those."""
    prefix = prefix.rstrip('/')
    if not re.match(r'^https://[A-Za-z0-9.-]+(?:/[A-Za-z0-9._~-]+)*$', prefix):
        raise BlockError(f'--allow-url-prefix must be a plain https URL, not {prefix!r}')
    if not isinstance(head, str) or not FULL_SHA.match(head):
        raise BlockError(f'head must be a full commit SHA, not {head!r}')
    for file in files:
        name, url = file.get('name'), file.get('url')
        if not isinstance(name, str) or not SAFE_NAME.match(name):
            raise BlockError(f'unsafe file name: {name!r}')
        if not isinstance(url, str) or not url.startswith(prefix + '/'):
            raise BlockError(f'{name}: URL is not under {prefix}/')
        path = url[len(prefix) + 1:]
        if not SAFE_PATH.match(path) or '..' in path.split('/') or not path.endswith('/' + name):
            raise BlockError(f'{name}: unsafe URL path {path!r}')


def collect(outputs, allow_prefix=None):
    heads = {out.get('head') for out in outputs}
    if None in heads:
        raise BlockError('publish output has no head commit; publish again with this version')
    if len(heads) != 1:
        raise BlockError(f'captures name different commits: {", ".join(sorted(map(str, heads)))}')
    files = [f for out in outputs for f in out['files']]
    if allow_prefix is not None:
        check_allowed(next(iter(heads)), files, allow_prefix)
    names = [f['name'] for f in files]
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        raise BlockError(f'duplicate file names: {", ".join(duplicates)}')
    return heads.pop(), files


def render(outputs, name=DEFAULT_MARKER, allow_prefix=None):
    head, files = collect(outputs, allow_prefix)
    groups, videos = {}, []
    for file in files:
        if Path(file['name']).suffix.lower() in VIDEO:
            videos.append(file)
            continue
        key, role = split_role(file['name'])
        groups.setdefault(key, {})[role] = file
    pairs = [g for g in groups.values() if set(g) == set(ROLES)]
    singles = [f for g in groups.values() if set(g) != set(ROLES) for f in g.values()]
    start, end = markers(name)
    lines = [start, f'Captures show commit {head}.', '']
    if pairs:
        lines += ['| Before | After |', '| --- | --- |']
        lines += [
            '| ' + ' | '.join(
                f"![{alt_text(g[role]['name'])}]({g[role]['url']})" for role in ROLES
            ) + ' |'
            for g in pairs
        ]
        lines.append('')
    for file in singles:
        lines += [f"![{alt_text(file['name'])}]({file['url']})", '']
    for file in videos:
        lines += [f"[{file['name']}]({file['url']})", '']
    lines.append(end)
    return '\n'.join(lines)


def apply(body, block, name=DEFAULT_MARKER):
    """Replace the marked block in body, or insert it when the markers are absent."""
    start, end = markers(name)
    has_start, has_end = start in body, end in body
    if has_start and has_end:
        before, rest = body.split(start, 1)
        if end not in rest:
            raise BlockError(f'{end} comes before {start}')
        after = rest.split(end, 1)[1]
        return before + block + after
    if has_start or has_end:
        raise BlockError(f'the body has only one of {start} and {end}')
    lines = body.split('\n')
    for index, line in enumerate(lines):
        if line.strip().lower() == '## evidence':
            rest = lines[index + 1:]
            while rest and not rest[0].strip():
                rest.pop(0)
            return '\n'.join(lines[:index + 1] + ['', block, ''] + rest)
    return body.rstrip('\n') + ('\n\n' if body.strip() else '') + block + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('outputs', nargs='+', type=Path,
                        help='JSON files printed by publish_evidence.py')
    parser.add_argument('--body', type=Path, help='current PR body (default: stdin)')
    parser.add_argument('--marker', default=DEFAULT_MARKER, help='marker name')
    parser.add_argument('--block-only', action='store_true',
                        help='print the block alone, for a job summary')
    parser.add_argument('--allow-url-prefix', metavar='URL',
                        help='refuse any file URL outside this prefix')
    args = parser.parse_args(argv)
    try:
        outputs = [json.loads(path.read_text()) for path in args.outputs]
        block = render(outputs, args.marker, args.allow_url_prefix)
        if args.block_only:
            sys.stdout.write(block + '\n')
            return 0
        body = args.body.read_text() if args.body else sys.stdin.read()
        sys.stdout.write(apply(body, block, args.marker))
    except (BlockError, OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print(f'evidence_block: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
