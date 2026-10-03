from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any

CANONICAL_RISKS: dict[str, dict[str, Any]] = {
    'advisor-orchestrator-worker': {
        'execution_class': 'CREDENTIALLED',
        'network_required': True,
        'credentials_required': True,
        'broad_filesystem_access': False,
        'explicit_user_request_required': True,
    },
    'commit-archaeologist': {
        'execution_class': 'LOCAL_READ_ONLY',
        'network_required': False,
        'credentials_required': False,
        'broad_filesystem_access': False,
        'explicit_user_request_required': False,
    },
    'dependency-doctor': {
        'execution_class': 'LOCAL_READ_ONLY',
        'network_required': False,
        'credentials_required': False,
        'broad_filesystem_access': False,
        'explicit_user_request_required': False,
        'optional_network_checks': True,
    },
    'first-reader': {
        'execution_class': 'REFERENCE_ONLY',
        'network_required': False,
        'credentials_required': False,
        'broad_filesystem_access': False,
        'explicit_user_request_required': False,
    },
    'project-graveyard': {
        'execution_class': 'LOCAL_READ_ONLY',
        'network_required': False,
        'credentials_required': False,
        'broad_filesystem_access': True,
        'explicit_user_request_required': True,
    },
    'scope-creep-detector': {
        'execution_class': 'LOCAL_READ_ONLY',
        'network_required': False,
        'credentials_required': False,
        'broad_filesystem_access': False,
        'explicit_user_request_required': False,
    },
    'thinking-out-loud': {
        'execution_class': 'REFERENCE_ONLY',
        'network_required': False,
        'credentials_required': False,
        'broad_filesystem_access': False,
        'explicit_user_request_required': False,
    },
}


def risk_for_skill(name: str) -> dict[str, Any]:
    if name not in CANONICAL_RISKS:
        return {
            'execution_class': 'REFERENCE_ONLY',
            'network_required': False,
            'credentials_required': False,
            'broad_filesystem_access': False,
            'explicit_user_request_required': True,
        }
    return dict(CANONICAL_RISKS[name])


def load_canonical_skills(root: Path) -> list[dict[str, Any]]:
    root = Path(root)
    registry_path = root / 'agent_skills' / 'registry.json'
    if not registry_path.is_file():
        return []
    data = json.loads(registry_path.read_text(encoding='utf-8'))
    result: list[dict[str, Any]] = []
    for raw in data.get('skills', []):
        item = dict(raw)
        name = str(item.get('name') or '').strip()
        upstream_path = str(item.get('path') or '').strip('/ ')
        inconsistencies: list[str] = []
        if not name or not upstream_path:
            inconsistencies.append('invalid_registry_entry')
        skill_md = root / upstream_path / 'SKILL.md' if upstream_path else root / '__missing__'
        if not skill_md.is_file():
            inconsistencies.append('missing_skill_md')
        if item.get('license') != 'Apache-2.0':
            inconsistencies.append('invalid_registry_license')
        item['name'] = name
        item['path'] = upstream_path
        item['inconsistencies'] = inconsistencies
        result.append(item)
    return sorted(result, key=lambda x: (x.get('name') or '', x.get('path') or ''))


def _managed_names(manifest: dict[str, Any] | None) -> set[str]:
    names: set[str] = set()
    if not manifest:
        return names
    for item in manifest.get('skills', []):
        if isinstance(item, str):
            names.add(item)
        elif isinstance(item, dict) and item.get('name'):
            names.add(str(item['name']))
    return names


def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f'.{path.name}.', suffix='.tmp', dir=path.parent)
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def project_skills(
    root: Path,
    dest: Path,
    previous_manifest: dict[str, Any] | None,
    matt_manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    root = Path(root)
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    previous_names = _managed_names(previous_manifest)
    matt_names = _managed_names(matt_manifest)
    loaded = load_canonical_skills(root)

    inconsistencies: list[dict[str, str]] = []
    installable: list[dict[str, Any]] = []
    for item in loaded:
        name = item['name']
        for reason in item.get('inconsistencies', []):
            inconsistencies.append({'name': name, 'reason': reason, 'upstream_path': item.get('path', '')})
        if 'missing_skill_md' in item.get('inconsistencies', []) or 'invalid_registry_entry' in item.get('inconsistencies', []):
            continue
        installable.append(item)

    current_names = {item['name'] for item in installable}
    for item in installable:
        name = item['name']
        target = dest / name
        if name in matt_names:
            raise RuntimeError(f'Matt Pocock controller owns destination skill: {name}')
        if target.exists() and name not in previous_names:
            raise RuntimeError(f'unmanaged destination collision for skill: {name}')

    for stale in sorted(previous_names - current_names):
        target = dest / stale
        if target.exists():
            shutil.rmtree(target)

    manifest_skills: list[dict[str, Any]] = []
    for item in installable:
        name = item['name']
        source = root / item['path']
        target = dest / name
        stage_parent = Path(tempfile.mkdtemp(prefix=f'.awesome-{name}-', dir=dest))
        stage = stage_parent / name
        try:
            shutil.copytree(source, stage, symlinks=True)
            if target.exists():
                shutil.rmtree(target)
            os.replace(stage, target)
        finally:
            shutil.rmtree(stage_parent, ignore_errors=True)
        record = {
            'name': name,
            'upstream_path': item['path'],
            'registry_license': item.get('license'),
            **risk_for_skill(name),
        }
        manifest_skills.append(record)

    manifest = {
        'schema_version': 1,
        'source': 'https://github.com/Shubhamsaboo/awesome-llm-apps',
        'upstream_commit': os.environ.get('AWESOME_LLM_APPS_UPSTREAM_COMMIT'),
        'skills': sorted(manifest_skills, key=lambda x: x['name']),
        'inconsistencies': sorted(inconsistencies, key=lambda x: (x['name'], x['reason'])),
    }
    _atomic_write_json(dest / '.awesome-llm-apps-managed.json', manifest)
    return manifest
