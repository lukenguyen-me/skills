#!/usr/bin/env python3
"""Publish PR evidence files to the project's store and print their URLs.

The project file docs/agents/evidence.md picks the store:

- git-ref (the default when the file is absent): files go to the hidden ref
  refs/evidence/<branch>. Clones fetch only branches and tags, so the evidence
  never reaches anyone's checkout. Each publish adds a commit on top of the
  previous one, so links from earlier publishes keep working.
- r2: files go to a Cloudflare R2 bucket under
  <prefix>/<branch>/<head sha>/<random>/<name>, signed with SigV4 from the
  standard library. The random part makes each URL unguessable, and every
  publish writes new keys, so earlier links keep working.
- none: the project has no visual surface; publishing is refused.

--check reports the configured store and whether each credential variable is
set, never its value.
"""

import argparse
import datetime
import hashlib
import hmac
import json
import os
import re
import secrets
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ALLOWED = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4', '.webm', '.mov'}
CONTENT_TYPES = {
    '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
    '.gif': 'image/gif', '.webp': 'image/webp', '.mp4': 'video/mp4',
    '.webm': 'video/webm', '.mov': 'video/quicktime',
}
SAFE_NAME = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*$')
GITHUB_REMOTE = re.compile(
    r'^(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)'
    r'(?P<repo>[^/]+/[^/]+?)(?:\.git)?/?$'
)
REPO_TAIL = re.compile(r'(?P<repo>[^/:]+/[^/]+?)(?:\.git)?/?$')
FALLBACK_IDENTITY = {
    'GIT_AUTHOR_NAME': 'luke-mode evidence',
    'GIT_AUTHOR_EMAIL': 'luke-mode-evidence@localhost',
    'GIT_COMMITTER_NAME': 'luke-mode evidence',
    'GIT_COMMITTER_EMAIL': 'luke-mode-evidence@localhost',
}
CONFIG_PATH = Path('docs/agents/evidence.md')
STORES = ('git-ref', 'r2', 'none')
R2_DEFAULTS = {
    'account-id-var': 'R2_ACCOUNT_ID',
    'access-key-id-var': 'R2_ACCESS_KEY_ID',
    'secret-access-key-var': 'R2_SECRET_ACCESS_KEY',
    'upload-host': '<account id>.r2.cloudflarestorage.com',
}
R2_REQUIRED = ('bucket', 'public-url')
CREDENTIAL_KEYS = ('account-id-var', 'access-key-id-var', 'secret-access-key-var')


class EvidenceError(Exception):
    pass


def git(*args, stdin=None, env=None, check=True):
    result = subprocess.run(
        ['git', *args], input=stdin, capture_output=True, text=True, env=env,
    )
    if check and result.returncode != 0:
        raise EvidenceError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


# --- project config -------------------------------------------------------

def read_config(path):
    """Read the Key | Value table of the project's evidence file."""
    config = {}
    for line in path.read_text().splitlines():
        cells = [c.strip().strip('`').strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 2 or not line.lstrip().startswith('|'):
            continue
        key, value = cells[0].lower(), cells[1]
        if key in ('key', '') or set(key) <= set('-: '):
            continue
        config[key] = value
    store = config.get('store', '')
    if store not in STORES:
        raise EvidenceError(f'{path}: store must be one of {", ".join(STORES)}, not {store!r}')
    if store == 'r2':
        for key, value in R2_DEFAULTS.items():
            config.setdefault(key, value)
        missing = [key for key in R2_REQUIRED if not config.get(key)]
        if missing:
            raise EvidenceError(f'{path}: r2 store needs {", ".join(missing)}')
    return config


def load_config(explicit):
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise EvidenceError(f'no evidence config at {path}')
        return path, read_config(path)
    root = git('rev-parse', '--show-toplevel', check=False)
    path = Path(root or '.') / CONFIG_PATH
    if path.is_file():
        return path, read_config(path)
    return None, {'store': 'git-ref'}


# --- shared checks ----------------------------------------------------------

def check_files(paths, max_mb, safe_names=False):
    names = set()
    for path in paths:
        if not path.is_file():
            raise EvidenceError(f'not a file: {path}')
        if path.suffix.lower() not in ALLOWED:
            raise EvidenceError(f'unsupported type {path.suffix}: {path}')
        if safe_names and not SAFE_NAME.match(path.name):
            raise EvidenceError(
                f'rename {path.name}: use letters, digits, dot, dash and underscore only'
            )
        size_mb = path.stat().st_size / 1_000_000
        if size_mb > max_mb:
            raise EvidenceError(f'{path} is {size_mb:.1f} MB; shrink it below {max_mb} MB')
        if path.name in names:
            raise EvidenceError(f'duplicate file name: {path.name}')
        names.add(path.name)


def check_head(commit):
    """Refuse a dirty tree, or a HEAD that is not the captured commit."""
    head = git('rev-parse', 'HEAD')
    if commit is None:
        return head
    if git('status', '--porcelain'):
        raise EvidenceError(
            f'the working tree has uncommitted changes, so the captures may not show '
            f'{head[:12]}; commit or stash them and capture again'
        )
    wanted = git('rev-parse', '--verify', '--quiet', f'{commit}^{{commit}}', check=False)
    if wanted != head:
        raise EvidenceError(
            f'HEAD is {head}, but the captures show {commit}; '
            'check out the captured commit or capture again'
        )
    return head


def branch_name(name):
    if not name:
        name = git('symbolic-ref', '--quiet', '--short', 'HEAD', check=False)
        if not name:
            raise EvidenceError('detached HEAD; pass --ref <name>')
    if subprocess.run(['git', 'check-ref-format', f'refs/evidence/{name}']).returncode != 0:
        raise EvidenceError(f'invalid evidence ref name: {name}')
    return name


# --- git-ref store ----------------------------------------------------------

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


def publish_git_ref(paths, remote, name, head, base_override):
    ref = f'refs/evidence/{name}'
    base = web_base(remote, base_override)
    parent = remote_tip(remote, ref)
    tree = build_tree(parent, paths)
    parent_args = ['-p', parent] if parent else []
    commit = git('commit-tree', tree, *parent_args, '-m', f'evidence: {name}', env=commit_env())
    git('push', '--quiet', remote, f'{commit}:{ref}')
    return {
        'store': 'git-ref',
        'head': head,
        'ref': ref,
        'commit': commit,
        'files': [
            {'name': p.name, 'url': f'{base}/blob/{commit}/{p.name}?raw=true'}
            for p in paths
        ],
    }


# --- r2 store ---------------------------------------------------------------

def _hmac(key, text):
    return hmac.new(key, text.encode(), hashlib.sha256).digest()


def sigv4_headers(method, url, headers, payload_hash, key_id, secret, region, service, now):
    """Return headers with a SigV4 Authorization header for one request."""
    parts = urllib.parse.urlsplit(url)
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    day = amz_date[:8]
    signed = {k.lower(): ' '.join(str(v).split()) for k, v in headers.items()}
    signed['host'] = parts.netloc
    signed['x-amz-date'] = amz_date
    signed['x-amz-content-sha256'] = payload_hash
    names = sorted(signed)
    query = '&'.join(
        f"{urllib.parse.quote(k, safe='-_.~')}={urllib.parse.quote(v, safe='-_.~')}"
        for k, v in sorted(urllib.parse.parse_qsl(parts.query, keep_blank_values=True))
    )
    canonical = '\n'.join([
        method,
        parts.path or '/',
        query,
        ''.join(f'{n}:{signed[n]}\n' for n in names),
        ';'.join(names),
        payload_hash,
    ])
    scope = f'{day}/{region}/{service}/aws4_request'
    to_sign = '\n'.join([
        'AWS4-HMAC-SHA256', amz_date, scope,
        hashlib.sha256(canonical.encode()).hexdigest(),
    ])
    key = _hmac(('AWS4' + secret).encode(), day)
    for part in (region, service, 'aws4_request'):
        key = _hmac(key, part)
    signature = hmac.new(key, to_sign.encode(), hashlib.sha256).hexdigest()
    signed['authorization'] = (
        f'AWS4-HMAC-SHA256 Credential={key_id}/{scope}, '
        f"SignedHeaders={';'.join(names)}, Signature={signature}"
    )
    return signed


def credential_status(config):
    return {config[key]: bool(os.environ.get(config[key])) for key in CREDENTIAL_KEYS}


def credentials(config):
    missing = [name for name, present in credential_status(config).items() if not present]
    if missing:
        raise EvidenceError(f'missing credential variables: {", ".join(missing)}')
    return tuple(os.environ[config[key]] for key in CREDENTIAL_KEYS)


def upload_endpoint(config, account_id, override):
    if override:
        return override.rstrip('/')
    host = config['upload-host'].replace('<account id>', account_id)
    return f'https://{host}'


def key_prefix(config, remote):
    prefix = config.get('key-prefix')
    if not prefix:
        url = git('remote', 'get-url', remote)
        match = GITHUB_REMOTE.match(url) or REPO_TAIL.search(url)
        if not match:
            raise EvidenceError(f'cannot read <owner>/<repo> from {remote}; set key-prefix')
        prefix = match['repo']
    return prefix.strip('/')


def object_key(prefix, branch, head, token, name):
    return '/'.join([prefix, branch, head, token, name])


def put_object(endpoint, bucket, key, path, creds, now):
    _, key_id, secret = creds
    body = path.read_bytes()
    url = f"{endpoint}/{bucket}/{urllib.parse.quote(key, safe='/-_.~')}"
    headers = sigv4_headers(
        'PUT', url,
        {
            'content-type': CONTENT_TYPES[path.suffix.lower()],
            'content-length': str(len(body)),
            'cache-control': 'public, max-age=31536000, immutable',
        },
        hashlib.sha256(body).hexdigest(), key_id, secret, 'auto', 's3', now,
    )
    headers.pop('host')
    request = urllib.request.Request(url, data=body, method='PUT', headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response.read()
    except urllib.error.HTTPError as error:
        code = re.search(r'<Code>([^<]+)</Code>', error.read().decode(errors='replace'))
        detail = f' ({code[1]})' if code else ''
        raise EvidenceError(f'upload of {path.name} failed: HTTP {error.code}{detail}') from None
    except urllib.error.URLError as error:
        raise EvidenceError(f'upload of {path.name} failed: {error.reason}') from None


def publish_r2(paths, config, remote, branch, head, endpoint_override):
    creds = credentials(config)
    endpoint = upload_endpoint(config, creds[0], endpoint_override)
    prefix = key_prefix(config, remote)
    token = secrets.token_hex(16)
    base = config['public-url'].rstrip('/')
    now = datetime.datetime.now(datetime.timezone.utc)
    files = []
    for path in paths:
        key = object_key(prefix, branch, head, token, path.name)
        put_object(endpoint, config['bucket'], key, path, creds, now)
        files.append({'name': path.name, 'url': f"{base}/{urllib.parse.quote(key, safe='/-_.~')}"})
    return {
        'store': 'r2',
        'head': head,
        'key': object_key(prefix, branch, head, token, ''),
        'files': files,
    }


# --- entry points -----------------------------------------------------------

def scrub(text, config):
    """Remove credential values from text before it is printed."""
    for key in CREDENTIAL_KEYS:
        value = os.environ.get(config.get(key, ''), '')
        if len(value) >= 4:
            text = text.replace(value, '***')
    return text


def check(config_path, config):
    store = config['store']
    report = {'store': store, 'config': str(config_path) if config_path else None}
    if store == 'r2':
        report['bucket'] = config['bucket']
        report['public_url'] = config['public-url']
        report['variables'] = {
            name: 'present' if present else 'missing'
            for name, present in credential_status(config).items()
        }
        report['upload_host'] = config['upload-host'].replace(
            '<account id>', f"<{config['account-id-var']}>"
        )
    return report


def publish(args, config):
    store = args.store or config['store']
    if store == 'none':
        raise EvidenceError('the project sets store: none; name each capture as a gap')
    if store == 'r2' and config.get('store') != 'r2':
        raise EvidenceError(f'--store r2 needs an r2 section in {CONFIG_PATH}')
    if store == 'r2' and not args.commit:
        raise EvidenceError('pass --commit <sha>: the commit the captures show')
    check_files(args.files, args.max_mb, safe_names=store == 'r2')
    git('rev-parse', '--git-dir')
    head = check_head(args.commit)
    branch = branch_name(args.ref)
    if store == 'r2':
        return publish_r2(args.files, config, args.remote, branch, head, args.endpoint)
    return publish_git_ref(args.files, args.remote, branch, head, args.web_base)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('files', nargs='*', type=Path)
    parser.add_argument('--check', action='store_true',
                        help='report the store and which credential variables are set')
    parser.add_argument('--store', choices=STORES, help='override the configured store')
    parser.add_argument('--config', help=f'evidence config (default: <repo>/{CONFIG_PATH})')
    parser.add_argument('--commit', help='the commit the captures show; required for r2')
    parser.add_argument('--remote', default='origin')
    parser.add_argument('--ref', help='branch name for the evidence (default: current branch)')
    parser.add_argument('--max-mb', type=float, default=10)
    parser.add_argument('--web-base', help='repository web URL for a non-github.com host')
    parser.add_argument('--endpoint', help='upload endpoint URL instead of the upload-host')
    args = parser.parse_args(argv)
    config = {}
    try:
        config_path, config = load_config(args.config)
        if args.check:
            result = check(config_path, config)
        elif not args.files:
            parser.error('name at least one file, or pass --check')
        else:
            result = publish(args, config)
    except EvidenceError as error:
        print(scrub(f'publish_evidence: {error}', config), file=sys.stderr)
        return 1
    print(scrub(json.dumps(result, indent=2), config))
    return 0


if __name__ == '__main__':
    sys.exit(main())
