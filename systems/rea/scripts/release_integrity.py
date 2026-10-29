#!/usr/bin/env python3
"""Independent REA release ZIP evidence verifier; does not certify operations.

A manifest inside a ZIP proves self-consistency, not publisher authenticity.
Pass an externally authorized SHA-256 and source commit to pin actual release.
Never extract, execute or modify archive content as part of verification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path

PRODUCT = 'REA_INDEPENDENTE'
PREFIX = 'REA_INDEPENDENTE/'
SHA256 = re.compile(r'^[0-9a-fA-F]{64}$')
SHA1 = re.compile(r'^[0-9a-fA-F]{40}$')
MAX_MEMBERS = 512
MAX_MEMBER_BYTES = 32 * 1024 * 1024
MAX_TOTAL_BYTES = 160 * 1024 * 1024


def _path_ok(name: str) -> bool:
    if (not isinstance(name, str) or not name.startswith(PREFIX)
            or '\\' in name or '\x00' in name or name.endswith('/')):
        return False
    parts = name.split('/')
    return len(parts) >= 2 and all(p not in ('', '.', '..') for p in parts)


def assess_archive(filename: Path, *, expected_sha256: str | None = None,
                   expected_git_sha: str | None = None) -> dict:
    """Check identity, exact manifest coverage, safe ZIP entries and optional pins."""
    report = {'product': PRODUCT, 'status': 'BLOCKED', 'checked_files': 0,
              'archive_sha256': None, 'source_git_sha': None,
              'trusted_digest_match': False, 'trusted_commit_match': False,
              'production_complete': False,
              'reason': 'Release archive not verified'}
    try:
        file = Path(filename)
        if not file.is_file() or file.is_symlink():
            raise ValueError('Not a regular archive')
        hash_of_archive = hashlib.sha256()
        with file.open('rb') as src:
            for block in iter(lambda: src.read(262144), b''):
                hash_of_archive.update(block)
        report['archive_sha256'] = hash_of_archive.hexdigest()
        if expected_sha256 is not None:
            if not isinstance(expected_sha256, str) or not SHA256.fullmatch(expected_sha256):
                raise ValueError('Malformed trusted expected SHA-256')
            if report['archive_sha256'].lower() != expected_sha256.lower():
                raise ValueError('Trusted release digest mismatch')
            report['trusted_digest_match'] = True
        with zipfile.ZipFile(file, 'r') as archive:
            infos = archive.infolist()
            if not 2 <= len(infos) <= MAX_MEMBERS:
                raise ValueError('Unexpected ZIP member count')
            observed = {}
            casefold_seen = set()
            total = 0
            for info in infos:
                name = info.filename
                if not _path_ok(name) or info.is_dir():
                    raise ValueError('Unsafe archive member name')
                if name.casefold() in casefold_seen:
                    raise ValueError('Duplicate or case-colliding archive name')
                casefold_seen.add(name.casefold())
                if stat.S_IFMT(info.external_attr >> 16) == stat.S_IFLNK:
                    raise ValueError('Symbolic link entry forbidden')
                if info.file_size > MAX_MEMBER_BYTES:
                    raise ValueError('Oversized member')
                total += info.file_size
                if total > MAX_TOTAL_BYTES:
                    raise ValueError('Uncompressed ZIP budget exceeded')
                observed[name] = info
            manifest_path = PREFIX + 'manifest.json'
            if manifest_path not in observed or observed[manifest_path].file_size > 1024 * 1024:
                raise ValueError('Missing or oversized manifest')
            manifest = json.loads(archive.read(manifest_path).decode('utf-8'))
            if not isinstance(manifest, dict) or manifest.get('system') != PRODUCT:
                raise ValueError('Product identity mismatch')
            declared_files = manifest.get('files')
            if not isinstance(declared_files, dict) or not declared_files:
                raise ValueError('Missing payload file hashes')
            expected_paths = {PREFIX + name for name in declared_files}
            if set(observed) - {manifest_path} != expected_paths:
                raise ValueError('Missing or unmanifested payload files')
            for relpath, declared_sha in declared_files.items():
                if (not isinstance(relpath, str) or not _path_ok(PREFIX + relpath)
                        or not isinstance(declared_sha, str) or not SHA256.fullmatch(declared_sha)):
                    raise ValueError('Invalid payload entry or hash')
                actual_sha = hashlib.sha256(archive.read(PREFIX + relpath)).hexdigest()
                if actual_sha.lower() != declared_sha.lower():
                    raise ValueError('Payload digest mismatch')
            claimed = manifest.get('git_sha')
            if claimed is not None and (not isinstance(claimed, str) or not SHA1.fullmatch(claimed)):
                raise ValueError('Invalid source commit field')
            report['source_git_sha'] = claimed
            if expected_git_sha is not None:
                if not isinstance(expected_git_sha, str) or not SHA1.fullmatch(expected_git_sha):
                    raise ValueError('Malformed external source commit')
                if claimed is None or claimed.lower() != expected_git_sha.lower():
                    raise ValueError('External source commit differs')
                report['trusted_commit_match'] = True
            report['checked_files'] = len(declared_files)
            report['status'] = 'INTEGRITY_PASS'
            report['reason'] = 'Self-consistency verified; external signatures and runtime acceptance remain separate'
    except (OSError, ValueError, TypeError, KeyError, zipfile.BadZipFile,
            zipfile.LargeZipFile, json.JSONDecodeError, UnicodeError):
        report['reason'] = 'REA standalone release integrity verification failed'
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', required=True, type=Path)
    parser.add_argument('--expected-sha256', help='SHA-256 from separate trusted channel')
    parser.add_argument('--expected-git-sha', help='Source commit expected by authorized release')
    args = parser.parse_args()
    result = assess_archive(args.zip, expected_sha256=args.expected_sha256,
                            expected_git_sha=args.expected_git_sha)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['status'] == 'INTEGRITY_PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
