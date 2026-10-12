#!/usr/bin/env python3
"""Publish PR evidence files to a hidden Git ref and print their GitHub URLs.

Files go to refs/evidence/<branch> on the remote. Clones fetch only branches
and tags, so the evidence never reaches anyone's checkout. Each publish adds a
commit on top of the previous one, so links from earlier publishes keep working.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ALLOWED = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4', '.webm', '.mov'}
GITHUB_REMOTE = re.compile(
    r'^(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)'
    r'(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$'
)
FALLBACK_IDENTITY = {
    'GIT_AUTHOR_NAME': 'luke-mode evidence',
    'GIT_AUTHOR_EMAIL': 'luke-mode-evidence@localhost',
    'GIT_COMMITTER_NAME': 'luke-mode evidence',
    'GIT_COMMITTER_EMAIL': 'luke-mode-evidence@localhost',
}


class EvidenceError(Exception):
    pass


def git(*args, stdin=None, env=None, check=True):
    result = subprocess.run(
        ['git', *args], input=stdin, capture_output=True, text=True, env=env,
    )
    if check and result.returncode != 0:
        raise EvidenceError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def evidence_ref(name):
    ref = f'refs/evidence/{name}'
    if subprocess.run(['git', 'check-ref-format', ref]).returncode != 0:
        raise EvidenceError(f'invalid evidence ref name: {name}')
    return ref


def web_base(remote, override):
    if override:
        return override.rstrip('/')
    url = git('remote', 'get-url', remote)
    match = GITHUB_REMOTE.match(url)
    if not match:
        raise EvidenceError(
            f'remote {remote} is not on github.com ({url}); '
            'pass --web-base for another host or report the local files instead'
        )
    return f"https://github.com/{match['repo']}"


def check_files(paths, max_mb):
    names = set()
    for path in paths:
        if not path.is_file():
            raise EvidenceError(f'not a file: {path}')
        if path.suffix.lower() not in ALLOWED:
            raise EvidenceError(f'unsupported type {path.suffix}: {path}')
        size_mb = path.stat().st_size / 1_000_000
        if size_mb > max_mb:
            raise EvidenceError(f'{path} is {size_mb:.1f} MB; shrink it below {max_mb} MB')
        if path.name in names:
            raise EvidenceError(f'duplicate file name: {path.name}')
        names.add(path.name)


def remote_tip(remote, ref):
    if not git('ls-remote', remote, ref):
        return None
    git('fetch', '--quiet', '--no-tags', remote, ref)
    return git('rev-parse', 'FETCH_HEAD')


def build_tree(parent, paths):
    entries = {}
    if parent:
        for line in git('ls-tree', parent).splitlines():
            meta, name = line.split('\t', 1)
            entries[name] = meta
    for path in paths:
        blob = git('hash-object', '-w', str(path))
        entries[path.name] = f'100644 blob {blob}'
    listing = ''.join(f'{meta}\t{name}\n' for name, meta in sorted(entries.items()))
    return git('mktree', stdin=listing)


def commit_env():
    env = dict(os.environ)
    if not git('config', 'user.email', check=False):
        env.update(FALLBACK_IDENTITY)
    return env


def publish(paths, remote, name, max_mb, base_override):
    check_files(paths, max_mb)
    git('rev-parse', '--git-dir')
    if not name:
        name = git('symbolic-ref', '--quiet', '--short', 'HEAD', check=False)
        if not name:
            raise EvidenceError('detached HEAD; pass --ref <name>')
    ref = evidence_ref(name)
    base = web_base(remote, base_override)
    parent = remote_tip(remote, ref)
    tree = build_tree(parent, paths)
    parent_args = ['-p', parent] if parent else []
    commit = git('commit-tree', tree, *parent_args, '-m', f'evidence: {name}', env=commit_env())
    git('push', '--quiet', remote, f'{commit}:{ref}')
    return {
        'ref': ref,
        'commit': commit,
        'files': [
            {'name': p.name, 'url': f'{base}/blob/{commit}/{p.name}?raw=true'}
            for p in paths
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--remote', default='origin')
    parser.add_argument('--ref', help='evidence ref name (default: current branch)')
    parser.add_argument('--max-mb', type=float, default=10)
    parser.add_argument('--web-base', help='repository web URL for a non-github.com host')
    args = parser.parse_args(argv)
    try:
        result = publish(args.files, args.remote, args.ref, args.max_mb, args.web_base)
    except EvidenceError as error:
        print(f'publish_evidence: {error}', file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
