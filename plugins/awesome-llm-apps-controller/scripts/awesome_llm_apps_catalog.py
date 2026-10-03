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
