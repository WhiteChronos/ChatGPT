#!/usr/bin/env python3
"""Build public MCE code from exact Git bytes; never install or approve it."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import zipfile
from pathlib import Path, PurePosixPath


def _git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(['git', '-C', str(repo), *args],
                            capture_output=True, timeout=60, check=False)
    if result.returncode:
        raise ValueError('Required committed Git source is unavailable')
    return result.stdout


def build_release(repo: Path, expected_commit: str, output: Path) -> dict:
    if not re.fullmatch(r'[0-9a-f]{40}', expected_commit):
        raise ValueError('An exact lowercase 40-character Git SHA is required')
    repo, output = Path(repo).resolve(), Path(output).resolve()
    if output.is_relative_to(repo / 'systems' / 'mce'):
        raise ValueError('Package must remain outside product source')
    if output.exists():
        raise FileExistsError('Refusing to overwrite an existing package')
    commit = _git(repo, 'rev-parse', '--verify', expected_commit + '^{commit}').decode().strip()
    if commit != expected_commit:
        raise ValueError('Commit mismatch')
    spec = importlib.util.spec_from_file_location(
        'mce_package_integrity', Path(__file__).with_name('release_integrity.py'))
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    payload = {}
    total = 0
    raw = _git(repo, 'ls-tree', '-rz', expected_commit + ':systems/mce')
    for entry in raw.split(b'\0'):
        if not entry:
            continue
        metadata, encoded_name = entry.split(b'\t', 1)
        mode, kind, blob = metadata.decode('ascii').split()
        name = encoded_name.decode('utf-8')
        path = PurePosixPath(name)
        if (mode not in ('100644', '100755') or kind != 'blob' or
                path.is_absolute() or '..' in path.parts or '\\' in name or
                name == 'manifest.json' or name in payload):
            raise ValueError('Unsafe or reserved committed payload member')
        size = int(_git(repo, 'cat-file', '-s', blob))
        total += size
        if (size > verifier.MAX_MEMBER or total > verifier.MAX_TOTAL or
                len(payload) + 2 > verifier.MAX_MEMBERS):
            raise ValueError('Package exceeds integrity verifier limits')
        payload[name] = _git(repo, 'cat-file', 'blob', blob)
    if not payload:
        raise ValueError('Product has no committed payload')
    manifest = {'system': 'MCE_INDEPENDENTE', 'git_sha': commit,
                'files': {name: hashlib.sha256(data).hexdigest()
                          for name, data in sorted(payload.items())}}
    payload['manifest.json'] = (json.dumps(manifest, sort_keys=True,
                                          indent=2) + '\n').encode('utf-8')
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(payload.items()):
            item = zipfile.ZipInfo('MCE_INDEPENDENTE/' + name, (1980, 1, 1, 0, 0, 0))
            item.create_system = 3
            item.external_attr = 0o100644 << 16
            item.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(item, data)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checked = verifier.assess_archive(output, expected_sha256=digest,
                                      expected_git_sha=commit)
    if checked['status'] != 'INTEGRITY_PASS':
        raise ValueError('Candidate did not pass existing package integrity gate')
    return {'status': 'CANDIDATE_PACKAGE_VERIFIED', 'git_sha': commit,
            'sha256': digest, 'file_count': len(manifest['files']),
            'production_complete': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--expected-commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(build_release(args.repo, args.expected_commit, args.output), sort_keys=True))
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired):
        print(json.dumps({'status': 'BLOCKED', 'production_complete': False}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
