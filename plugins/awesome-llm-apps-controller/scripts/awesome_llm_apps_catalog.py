from __future__ import annotations

import hashlib
import re
from typing import Any

EXECUTION_CLASSES = (
    'SELF_MODIFYING',
    'BACKGROUND_AUTONOMOUS',
    'MCP_OR_CONNECTOR',
    'CREDENTIALLED',
    'NETWORKED',
    'LOCAL_MUTATING',
    'LOCAL_READ_ONLY',
    'REFERENCE_ONLY',
)

_HIGH_STAKES_TERMS = {
    'insurance', 'claim', 'medical', 'medicine', 'healthcare', 'health care',
    'diagnosis', 'diagnostic', 'financial', 'finance', 'trading', 'investment',
    'legal', 'lawyer', 'clinical', 'patient', 'mortgage', 'credit', 'banking',
}
_BACKGROUND_TERMS = {'background', 'daemon', 'scheduler', 'scheduled', 'worker', 'monitoring', 'autonomous loop'}
_SELF_MODIFY_TERMS = {'self-modifying', 'self modifying', 'self-rewriting', 'self rewriting'}
_NETWORK_TERMS = {'api', 'http', 'webhook', 'browser', 'scrape', 'search', 'remote', 'cloud'}
_MUTATING_TERMS = {'write file', 'filesystem write', 'database write', 'deploy', 'provision', 'create resource'}


def _slug(value: str) -> str:
    value = value.strip().lower().replace('_', '-')
    value = re.sub(r'^https?://', '', value)
    value = re.sub(r'[^a-z0-9]+', '-', value).strip('-')
    return value or 'entry'


def normalize_id(source_type: str, key: str) -> str:
    source = _slug(source_type)
    if source_type == 'external_reference':
        digest = hashlib.sha256(key.encode('utf-8')).hexdigest()[:12]
        return f'{source}:{_slug(key)}-{digest}'
    return f'{source}:{_slug(key)}'


def _text(entry: dict[str, Any]) -> str:
    pieces: list[str] = []
    for key in ('title', 'upstream_path', 'description', 'subtype', 'category'):
        value = entry.get(key)
        if value:
            pieces.append(str(value))
    for key in ('manifest_paths', 'env_example_paths', 'mcp_related_paths', 'external_services', 'providers', 'frameworks'):
        value = entry.get(key) or []
        if isinstance(value, (list, tuple, set)):
            pieces.extend(str(item) for item in value)
        elif value:
            pieces.append(str(value))
    return ' '.join(pieces).lower()


def _bool(entry: dict[str, Any], key: str, inferred: bool) -> bool:
    if key in entry:
        return bool(entry[key])
    return inferred


def classify_execution(entry: dict[str, Any]) -> dict[str, Any]:
    text = _text(entry)
    env_paths = entry.get('env_example_paths') or []
    manifest_paths = entry.get('manifest_paths') or []
    mcp_paths = entry.get('mcp_related_paths') or []

    credentials_required = _bool(
        entry,
        'credentials_required',
        bool(env_paths)
        or any('.env' in str(p).lower() for p in manifest_paths)
        or any(term in text for term in ('api key', 'apikey', 'token', 'secret', 'credential', 'oauth')),
    )
    network_required = _bool(
        entry,
        'network_required',
        bool(entry.get('external_url'))
        or bool(entry.get('external_services'))
        or any(term in text for term in _NETWORK_TERMS),
    )
    background_capable = _bool(entry, 'background_capable', any(term in text for term in _BACKGROUND_TERMS))
    self_modifying = _bool(entry, 'self_modifying', any(term in text for term in _SELF_MODIFY_TERMS))
    high_stakes_domain = _bool(entry, 'high_stakes_domain', any(term in text for term in _HIGH_STAKES_TERMS))
    mcp_related = bool(mcp_paths) or 'mcp' in text or bool(entry.get('mcp_or_connector'))
    local_mutating = _bool(entry, 'local_mutating', any(term in text for term in _MUTATING_TERMS))
    local_read_only = _bool(entry, 'local_read_only', bool(entry.get('read_only')))

    if self_modifying:
        execution_class = 'SELF_MODIFYING'
    elif background_capable:
        execution_class = 'BACKGROUND_AUTONOMOUS'
    elif mcp_related:
        execution_class = 'MCP_OR_CONNECTOR'
    elif credentials_required:
        execution_class = 'CREDENTIALLED'
    elif network_required:
        execution_class = 'NETWORKED'
    elif local_mutating:
        execution_class = 'LOCAL_MUTATING'
    elif local_read_only:
        execution_class = 'LOCAL_READ_ONLY'
    else:
        execution_class = 'REFERENCE_ONLY'

    return {
        'credentials_required': credentials_required,
        'network_required': network_required,
        'background_capable': background_capable,
        'self_modifying': self_modifying,
        'high_stakes_domain': high_stakes_domain,
        'execution_class': execution_class,
    }


from pathlib import Path
from collections import Counter
import json

MANDATORY_ROOTS = (
    'starter_ai_agents',
    'advanced_ai_agents',
    'always_on_agents',
    'voice_ai_agents',
    'mcp_ai_agents',
    'generative_ui_agents',
    'rag_tutorials',
    'advanced_llm_apps',
    'ai_agent_framework_crash_course',
    'agent_skills',
)
_DENY_TOP_LEVEL = {'.git', '.github', 'docs', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build'}
_MANIFEST_NAMES = {
    'requirements.txt', 'pyproject.toml', 'package.json', 'package-lock.json',
    'pnpm-lock.yaml', 'yarn.lock', 'poetry.lock', 'environment.yml', 'setup.py',
    'setup.cfg', 'Pipfile', 'Pipfile.lock', 'uv.lock',
}
_CODE_SUFFIXES = {'.py', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.go', '.rs', '.java', '.sh'}
_RECOGNIZED_HEADING_TERMS = (
    'agent', 'app', 'rag', 'memory', 'voice', 'multi-agent', 'multi agent',
    'framework', 'mcp', 'generative ui', 'autonomous', 'skill',
)
_IGNORED_HEADING_TERMS = ('sponsor', 'translation', 'documentation', 'docs', 'social', 'badge', 'contributor', 'community')


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_license_name(name: str) -> bool:
    upper = name.upper()
    return upper == 'LICENSE' or upper.startswith('LICENSE.') or upper == 'NOTICE' or upper.startswith('NOTICE.')


def _nearest_license_paths(directory: Path, root: Path) -> tuple[list[str], str]:
    current = directory
    while True:
        found = sorted(
            (_rel(p, root) for p in current.iterdir() if p.is_file() and _is_license_name(p.name)),
            key=str.lower,
        ) if current.exists() else []
        if found:
            status = 'VERIFIED_ROOT_LICENSE' if current == root else 'VERIFIED_SUBPROJECT_LICENSE'
            return found, status
        if current == root:
            break
        if root not in current.parents:
            break
        current = current.parent
    return [], 'VERIFIED_ROOT_LICENSE'


def _looks_like_mcp(path: Path) -> bool:
    s = path.as_posix().lower()
    return 'mcp' in s or path.name.lower() in {'mcp.json', '.mcp.json'}


def _qualifying_directory(directory: Path) -> bool:
    try:
        children = list(directory.iterdir())
    except OSError:
        return False
    if any(p.is_file() and p.name.lower().startswith('readme') for p in children):
        return True
    if any(p.is_file() and p.name in _MANIFEST_NAMES for p in children):
        return True
    if any(p.is_file() and (p.name.lower().startswith('dockerfile') or 'compose' in p.name.lower()) for p in children):
        return True
    if any(p.is_file() and p.suffix.lower() in _CODE_SUFFIXES and p.name not in {'__init__.py'} for p in children):
        return True
    return False


def _category_for(rel_dir: str) -> str:
    top = rel_dir.split('/', 1)[0]
    if top == 'agent_skills':
        return 'skill'
    if top == 'rag_tutorials':
        return 'rag_app'
    if 'agent' in top:
        return 'agent_app'
    if 'llm' in top or 'app' in top:
        return 'llm_app'
    return 'component'


def _subtype_for(rel_dir: str) -> str:
    lower = rel_dir.lower()
    if 'multi_agent' in lower or 'multi-agent' in lower:
        return 'multi_agent'
    if 'voice' in lower:
        return 'voice_agent'
    if 'mcp' in lower:
        return 'mcp_app'
    if 'rag' in lower:
        return 'rag_app'
    return 'application'


def _title_for(directory: Path) -> str:
    readmes = sorted(p for p in directory.iterdir() if p.is_file() and p.name.lower().startswith('readme'))
    for readme in readmes:
        try:
            for line in readme.read_text(encoding='utf-8', errors='replace').splitlines():
                m = re.match(r'^#\s+(.+?)\s*$', line)
                if m:
                    return re.sub(r'[*_\x60]', '', m.group(1)).strip()
        except OSError:
            pass
    return directory.name.replace('_', ' ').replace('-', ' ').title()


def _empty_entry(*, source_type: str, key: str, commit: str) -> dict[str, Any]:
    return {
        'id': normalize_id(source_type, key),
        'source_type': source_type,
        'upstream_path': key if source_type == 'upstream_internal' else None,
        'external_url': None,
        'license_status': 'VERIFIED_ROOT_LICENSE' if source_type == 'upstream_internal' else 'UNVERIFIED',
        'category': 'component',
        'subtype': 'application',
        'title': key,
        'readme_path': None,
        'skill_paths': [],
        'manifest_paths': [],
        'env_example_paths': [],
        'docker_paths': [],
        'mcp_related_paths': [],
        'languages': [],
        'frameworks': [],
        'providers': [],
        'external_services': [],
        'network_required': False,
        'credentials_required': False,
        'background_capable': False,
        'self_modifying': False,
        'high_stakes_domain': False,
        'execution_class': 'REFERENCE_ONLY',
        'upstream_commit': commit,
    }


def extract_external_references(readme_text: str, commit: str) -> list[dict[str, Any]]:
    current_heading = ''
    out: list[dict[str, Any]] = []
    link_re = re.compile(r'^\s*[-*+]\s+\[([^\]]+)\]\((https?://[^)]+)\)')
    for raw in readme_text.splitlines():
        heading = re.match(r'^#{2,4}\s+(.+?)\s*$', raw)
        if heading:
            current_heading = re.sub(r'[^a-z0-9 -]+', ' ', heading.group(1).lower())
            continue
        m = link_re.match(raw)
        if not m:
            continue
        if any(term in current_heading for term in _IGNORED_HEADING_TERMS):
            continue
        if not any(term in current_heading for term in _RECOGNIZED_HEADING_TERMS):
            continue
        title, url = m.group(1).strip(), m.group(2).strip()
        if 'github.com/shubhamsaboo/awesome-llm-apps' in url.lower():
            continue
        entry = _empty_entry(source_type='external_reference', key=url, commit=commit)
        entry.update({
            'external_url': url,
            'category': 'agent_app',
            'subtype': 'external_reference',
            'title': title,
            'license_status': 'UNVERIFIED',
            'network_required': False,
            'credentials_required': False,
            'background_capable': False,
            'self_modifying': False,
            'high_stakes_domain': classify_execution({'title': title})['high_stakes_domain'],
            'execution_class': 'REFERENCE_ONLY',
        })
        out.append(entry)
    dedup = {e['id']: e for e in out}
    return [dedup[k] for k in sorted(dedup)]


def _load_registry(root: Path) -> dict[str, dict[str, Any]]:
    path = root / 'agent_skills' / 'registry.json'
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for skill in data.get('skills', []):
        p = str(skill.get('path') or '').strip('/ ')
        if p:
            result[p] = skill
    return result


def scan_internal_entries(root: Path, commit: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    root = root.resolve()
    registry = _load_registry(root)
    qualifying: list[Path] = []
    for top in sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: p.name.lower()):
        if top.name in _DENY_TOP_LEVEL or top.name.startswith('.'):
            continue
        for directory, dirs, _files in __import__('os').walk(top):
            dirs[:] = sorted(d for d in dirs if d not in _DENY_TOP_LEVEL and not d.startswith('.'))
            d = Path(directory)
            if _qualifying_directory(d):
                qualifying.append(d)
    for rel_dir in registry:
        directory = root / rel_dir
        if directory.is_dir():
            qualifying.append(directory)
    qualifying = sorted(set(qualifying), key=lambda p: (_rel(p, root).count('/'), _rel(p, root)))
    by_path: dict[str, dict[str, Any]] = {}
    for directory in qualifying:
        rel_dir = _rel(directory, root)
        entry = _empty_entry(source_type='upstream_internal', key=rel_dir, commit=commit)
        entry['category'] = _category_for(rel_dir)
        entry['subtype'] = 'canonical_skill' if rel_dir in registry else _subtype_for(rel_dir)
        entry['title'] = str(registry.get(rel_dir, {}).get('name') or _title_for(directory))
        readmes = sorted((p for p in directory.iterdir() if p.is_file() and p.name.lower().startswith('readme')), key=lambda p: p.name.lower())
        entry['readme_path'] = _rel(readmes[0], root) if readmes else None
        license_paths, license_status = _nearest_license_paths(directory, root)
        entry['license_paths'] = license_paths
        entry['license_status'] = license_status
        by_path[rel_dir] = entry

    qualifying_paths = sorted((Path(p) for p in by_path), key=lambda p: len(p.parts), reverse=True)
    components: list[dict[str, Any]] = []
    for file in sorted((p for p in root.rglob('*') if p.is_file()), key=lambda p: _rel(p, root)):
        rel_file = _rel(file, root)
        parts = Path(rel_file)
        owner_rel = None
        for candidate in qualifying_paths:
            try:
                parts.parent.relative_to(candidate)
                owner_rel = candidate.as_posix()
                break
            except ValueError:
                continue
        if not owner_rel:
            continue
        entry = by_path[owner_rel]
        name_lower = file.name.lower()
        if file.name == 'SKILL.md':
            if owner_rel not in registry or rel_file != f'{owner_rel}/SKILL.md':
                if rel_file not in entry['skill_paths']:
                    entry['skill_paths'].append(rel_file)
                components.append({
                    'path': rel_file,
                    'owner_id': entry['id'],
                    'category': 'skill',
                    'subtype': 'project_internal_skill',
                })
        if file.name in _MANIFEST_NAMES:
            entry['manifest_paths'].append(rel_file)
        if '.env' in name_lower and ('example' in name_lower or 'sample' in name_lower or 'template' in name_lower):
            entry['env_example_paths'].append(rel_file)
        if name_lower.startswith('dockerfile') or 'compose' in name_lower:
            entry['docker_paths'].append(rel_file)
        if _looks_like_mcp(file):
            entry['mcp_related_paths'].append(rel_file)

    for entry in by_path.values():
        for key in ('skill_paths','manifest_paths','env_example_paths','docker_paths','mcp_related_paths'):
            entry[key] = sorted(set(entry[key]))
        entry.update(classify_execution(entry))
    return sorted(by_path.values(), key=lambda e: e['id']), sorted(components, key=lambda c: c['path'])


def build_catalog(root: Path, commit: str) -> dict[str, Any]:
    root = Path(root).resolve()
    entries, components = scan_internal_entries(root, commit)
    readme = root / 'README.md'
    if readme.exists():
        entries.extend(extract_external_references(readme.read_text(encoding='utf-8', errors='replace'), commit))
    entries = sorted(entries, key=lambda e: e['id'])
    missing = [name for name in MANDATORY_ROOTS if not (root / name).is_dir()]
    return {
        'schema_version': 1,
        'upstream_commit': commit,
        'missing_mandatory_roots': missing,
        'entries': entries,
        'components': components,
    }


def build_summary(catalog: dict[str, Any]) -> dict[str, Any]:
    entries = list(catalog.get('entries') or [])
    by_category = Counter(str(e.get('category') or 'unknown') for e in entries)
    by_source = Counter(str(e.get('source_type') or 'unknown') for e in entries)
    by_execution = Counter(str(e.get('execution_class') or 'unknown') for e in entries)
    return {
        'schema_version': int(catalog.get('schema_version', 1)),
        'upstream_commit': catalog.get('upstream_commit'),
        'total_entries': len(entries),
        'by_category': dict(sorted(by_category.items())),
        'by_source_type': dict(sorted(by_source.items())),
        'by_execution_class': dict(sorted(by_execution.items())),
        'missing_mandatory_roots': list(catalog.get('missing_mandatory_roots') or []),
    }
