#!/usr/bin/env python3
"""Read-only release archive attestation for standalone MCE ZIPs.

Release integrity is not engineering validation, project approval or FAT/SAT.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath

MAX_MEMBERS = 512
MAX_MEMBER = 32 * 1024 * 1024
MAX_TOTAL = 160 * 1024 * 1024
HEX_SHA = re.compile(r'^[0-9a-fA-F]{64}$')
PREFIX = 'MCE_INDEPENDENTE/'


def assess_archive(filename: Path) -> dict:
    """Verify exact manifest coverage, paths and payload hashes without extraction."""
    report = {'product': 'MCE_INDEPENDENTE', 'status': 'BLOCKED',
              'checked_files': 0, 'archive_sha256': None, 'production_complete': False,
              'reason': 'Archive evidence has not been verified'}
    try:
        file = Path(filename)
        if not file.is_file() or file.is_symlink():
            raise ValueError('Archive unavailable or unsafe')
        digest = hashlib.sha256()
        with file.open('rb') as handle:
            for block in iter(lambda: handle.read(262144), b''):
                digest.update(block)
        report['archive_sha256'] = digest.hexdigest()
        with zipfile.ZipFile(file, 'r') as zipped:
            members = zipped.infolist()
            if not (2 <= len(members) <= MAX_MEMBERS):
                raise ValueError('Unexpected archive member count')
            by_name = {}
            total = 0
            for info in members:
                name = info.filename
                parts = PurePosixPath(name).parts
                if (not name.startswith(PREFIX) or name.endswith('/') or
                    '\\' in name or PurePosixPath(name).is_absolute() or
                    any(p in ('.', '..') for p in parts) or
                    len(parts) < 2 or info.is_dir()):
                    raise ValueError('Unsafe path or directory member')
                if name in by_name:
                    raise ValueError('Duplicate member name')
                mode = info.external_attr >> 16
                if stat.S_IFMT(mode) == stat.S_IFLNK:
                    raise ValueError('Symbolic-link member is forbidden')
                if info.file_size > MAX_MEMBER:
                    raise ValueError('Member exceeds size limit')
                total += info.file_size
                if total > MAX_TOTAL:
                    raise ValueError('Archive size budget exceeded')
                by_name[name] = info
            key = PREFIX + 'manifest.json'
            if key not in by_name or by_name[key].file_size > 1024 * 1024:
                raise ValueError('Missing or oversized SHA-256 manifest')
            manifest = json.loads(zipped.read(key).decode('utf-8'))
            if not isinstance(manifest, dict) or manifest.get('system') != 'MCE_INDEPENDENTE':
                raise ValueError('Unexpected release identity')
            files = manifest.get('files')
            if not isinstance(files, dict) or not files:
                raise ValueError('Missing file hashes')
            expected = {PREFIX + name for name in files}
            observed = set(by_name) - {key}
            if expected != observed:
                raise ValueError('Manifest does not exactly describe archive payload')
            for name, declared in files.items():
                if not isinstance(name, str) or not isinstance(declared, str) or not HEX_SHA.fullmatch(declared):
                    raise ValueError('Invalid file digest')
                actual = hashlib.sha256(zipped.read(PREFIX + name)).hexdigest()
                if actual.lower() != declared.lower():
                    raise ValueError('Archive member SHA-256 mismatch')
            report['checked_files'] = len(files)
            report['status'] = 'INTEGRITY_PASS'
            report['reason'] = 'Archive bytes match SHA-256 manifest; human engineering approval still required'
    except (OSError, ValueError, TypeError, KeyError, zipfile.BadZipFile, json.JSONDecodeError):
        report['reason'] = 'Release archive integrity verification failed'
    return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--zip', required=True, type=Path)
    args = p.parse_args()
    report = assess_archive(args.zip)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['status'] == 'INTEGRITY_PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
