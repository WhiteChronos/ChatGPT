from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
from typing import Any

EXCLUDED_DIRS = {
    '.git', 'node_modules', '.venv', 'venv', '__pycache__', '.pytest_cache',
    '.next', 'dist', 'build',
}
MEDIA_EXTENSIONS = {
    '.gif', '.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.mp4', '.mov',
    '.avi', '.webm', '.mkv', '.mp3', '.wav', '.flac',
}
LARGE_MEDIA_BYTES = 10 * 1024 * 1024


def _git_blob_sha(data: bytes) -> str:
    header = f'blob {len(data)}\0'.encode('ascii')
    return hashlib.sha1(header + data).hexdigest()


def _file_sha(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except (OSError, MemoryError):
        return None
    return _git_blob_sha(data)


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def _record(path: str, *, action: str, size: int, reason: str | None = None,
            git_sha: str | None = None, link_target: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {
        'path': path,
        'action': action,
        'size': int(size),
        'git_sha': git_sha,
        'upstream_commit': os.environ.get('AWESOME_LLM_APPS_UPSTREAM_COMMIT'),
    }
    if reason is not None:
        item['reason'] = reason
    if link_target is not None:
        item['link_target'] = link_target
    return item


def plan_mirror(root: Path) -> list[dict[str, Any]]:
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError(f'upstream root is not a directory: {root}')
    plan: list[dict[str, Any]] = []

    def walk(directory: Path, rel_prefix: Path, inherited_reason: str | None = None) -> None:
        with os.scandir(directory) as scan:
            entries = sorted(list(scan), key=lambda e: e.name)
        for entry in entries:
            path = Path(entry.path)
            rel = (rel_prefix / entry.name).as_posix()
            st = os.lstat(path)

            if inherited_reason is not None:
                if entry.is_dir(follow_symlinks=False):
                    walk(path, rel_prefix / entry.name, inherited_reason)
                elif entry.is_symlink():
                    target = os.readlink(path)
                    plan.append(_record(rel, action='exclude', size=len(target.encode('utf-8')), reason=inherited_reason, git_sha=_git_blob_sha(target.encode('utf-8'))))
                else:
                    plan.append(_record(rel, action='exclude', size=st.st_size, reason=inherited_reason, git_sha=_file_sha(path)))
                continue

            if entry.is_symlink():
                target = os.readlink(path)
                resolved = (path.parent / target).resolve(strict=False)
                data = target.encode('utf-8')
                if not _inside(root, resolved):
                    plan.append(_record(rel, action='exclude', size=len(data), reason='unsafe_symlink', git_sha=_git_blob_sha(data), link_target=target))
                else:
                    plan.append(_record(rel, action='symlink', size=len(data), git_sha=_git_blob_sha(data), link_target=target))
                continue

            if entry.is_dir(follow_symlinks=False):
                if entry.name in EXCLUDED_DIRS:
                    walk(path, rel_prefix / entry.name, f'excluded_directory:{entry.name}')
                else:
                    walk(path, rel_prefix / entry.name)
                continue

            suffix = path.suffix.lower()
            if suffix in MEDIA_EXTENSIONS and st.st_size > LARGE_MEDIA_BYTES:
                plan.append(_record(rel, action='exclude', size=st.st_size, reason='large_demo_media', git_sha=_file_sha(path)))
            else:
                plan.append(_record(rel, action='include', size=st.st_size, git_sha=_file_sha(path)))

    walk(root, Path('.'))
    for item in plan:
        if item['path'].startswith('./'):
            item['path'] = item['path'][2:]
    return sorted(plan, key=lambda item: item['path'])


def copy_mirror(root: Path, dest: Path, plan: list[dict[str, Any]]) -> dict[str, Any]:
    root = Path(root).resolve()
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    included: list[str] = []
    symlinks: list[str] = []
    excluded: list[dict[str, Any]] = []

    for item in sorted(plan, key=lambda x: x['path']):
        rel = Path(item['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError(f'unsafe mirror path: {item["path"]}')
        source = root / rel
        target = dest / rel
        action = item['action']
        if action == 'exclude':
            excluded.append(dict(item))
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if action == 'symlink':
            link_target = item.get('link_target')
            if not isinstance(link_target, str):
                raise ValueError(f'missing link target: {item["path"]}')
            target.unlink(missing_ok=True)
            os.symlink(link_target, target)
            symlinks.append(item['path'])
        elif action == 'include':
            shutil.copy2(source, target, follow_symlinks=False)
            included.append(item['path'])
        else:
            raise ValueError(f'unknown mirror action: {action}')

    return {
        'included': included,
        'symlinks': symlinks,
        'excluded': excluded,
        'included_count': len(included),
        'symlink_count': len(symlinks),
        'excluded_count': len(excluded),
    }
