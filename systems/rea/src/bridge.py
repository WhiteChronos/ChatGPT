#!/usr/bin/env python3
"""Independent read-only static reverse engineering MCP gateway.

Not the upstream morluto/rea product. No engineering matrix or Excel dependencies.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SERVER_NAME = 'rea-independent-engine'
VERSION = '0.2.0'
MAX_SOURCE_BYTES = 600_000
MAX_INPUT_BYTES = 8_000_000
MAX_LISTED_FILES = 250
BLOCKED_PARTS = {'.git', '.ssh', '.aws', '.env', '.env.local', 'secrets',
                 'credentials', '.npmrc', '.pypirc', '__pycache__', '.venv',
                 'node_modules', '.pytest_cache', '.mypy_cache', 'private'}
BLOCKED_SUFFIXES = {'.pem', '.key', '.p12', '.pfx', '.kdbx', '.sqlite', '.db', '.xlsx', '.xlsm'}
SOURCE_SUFFIXES = {'.py', '.js', '.jsx', '.ts', '.tsx', '.go', '.cs', '.java', '.md', '.json', '.yaml', '.yml'}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(262144), b''):
            h.update(chunk)
    return h.hexdigest()


def node_eligible(text: str) -> bool:
    m = re.search(r'v?(\d+)\.(\d+)\.(\d+)', text)
    if not m:
        return False
    major, minor, patch = map(int, m.groups())
    return (major == 22 and (minor, patch) >= (23, 4)) or \
           (major == 24 and (minor, patch) >= (22, 1)) or \
           (major >= 26 and (major, minor, patch) >= (26, 12, 1))


def native_runtime() -> dict:
    node_exe = shutil.which('node')
    node_version = 'MISSING'
    if node_exe:
        try:
            node_version = subprocess.run([node_exe, '--version'],
                capture_output=True, text=True, timeout=3, check=True).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            node_version = 'UNKNOWN'
    return {
        'native_status': 'AVAILABLE_UNVERIFIED' if shutil.which('rea') and node_eligible(node_version) else 'UNAVAILABLE',
        'node_version': node_version,
        'node_supported_for_current_upstream': node_eligible(node_version),
        'rea_command_detected': bool(shutil.which('rea')),
        'npm_command_detected': bool(shutil.which('npm')),
        'upstream_repo': 'https://github.com/morluto/rea',
        'official_package': 'rea-agents',
        'official_connection': 'npx rea-agents@latest setup --client codex',
                'implementation': 'INDEPENDENT_REA_STATIC_ENGINE_NOT_UPSTREAM_REA',
    }


TOOLS = [
    {'name': 'rea_bridge_status', 'description': 'Local REA runtime prerequisite check; not the upstream REA server.',
     'inputSchema': {'type': 'object', 'properties': {}, 'additionalProperties': False}},
    {'name': 'rea_source_inspect', 'description': 'Source metadata, definitions, imports and SHA-256 without source bodies.',
     'inputSchema': {'type': 'object', 'properties': {'file': {'type': 'string'}},
                     'required': ['file'], 'additionalProperties': False}},
    {'name': 'rea_project_inventory', 'description': 'Bounded, read-only SHA-256 inventory within authorized local root.',
     'inputSchema': {'type': 'object', 'properties': {'directory': {'type': 'string'},
                    'limit': {'type': 'integer', 'minimum': 1, 'maximum': MAX_LISTED_FILES}},
                     'additionalProperties': False}},
    {'name': 'rea_internal_analyze', 'description': 'Read-only Python and JavaScript import graph with evidence hashes.',
     'inputSchema': {'type': 'object', 'properties': {'directory': {'type': 'string'},
                    'limit': {'type': 'integer', 'minimum': 1, 'maximum': 100}},
                     'additionalProperties': False}},
    {'name': 'rea_arena_compare', 'description': 'Four-perspective policy comparison; not an empirical tournament.',
     'inputSchema': {'type': 'object', 'properties': {
            'objective': {'type': 'string', 'enum': ['source_analysis','native_binary','web_application']},
            'confidentiality': {'type': 'string', 'enum': ['high','normal']}},
            'additionalProperties': False}},
    {'name': 'rea_repositories_top10', 'description': 'Review user-supplied ranked GitHub catalog JSON in authorized root; no live scraping.',
     'inputSchema': {'type': 'object', 'properties': {'catalog': {'type': 'string'}},
                     'required': ['catalog'], 'additionalProperties': False}},
    {'name': 'rea_verify_evidence', 'description': 'Read-only file SHA-256 verification; no automatic approval.',
     'inputSchema': {'type': 'object', 'properties': {'file': {'type': 'string'},
                   'expected_sha256': {'type': 'string'}},
                   'required': ['file', 'expected_sha256'], 'additionalProperties': False}},
]
for _tool in TOOLS:
    _tool['annotations'] = {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}


class ReaBridge:
    def __init__(self, root: Path, application_root: Path):
        self.root = Path(root).resolve(strict=True)
        self.app_root = Path(application_root).resolve(strict=True)

    def _resolve(self, raw: str, *, allow_dir: bool = False, protected: bool = True) -> Path:
        if not isinstance(raw, str) or not raw or '\\' in raw:
            raise ValueError('Relative path required')
        rel = Path(raw)
        if rel.is_absolute() or any(x == '..' for x in rel.parts):
            raise ValueError('Path escapes permitted root')
        if protected and (any(x.lower() in BLOCKED_PARTS for x in rel.parts) or
                          rel.suffix.lower() in BLOCKED_SUFFIXES or
                          rel.name.lower().startswith('id_rsa')):
            raise ValueError('Sensitive path denied')
        point = self.root
        for x in rel.parts:
            point = point / x
            if point.is_symlink():
                raise ValueError('Symlink denied')
        resolved = point.resolve(strict=True)
        if not resolved.is_relative_to(self.root):
            raise ValueError('Path escapes permitted root')
        if allow_dir and not resolved.is_dir():
            raise ValueError('Directory required')
        if not allow_dir and not resolved.is_file():
            raise ValueError('File required')
        return resolved

    def _read_text(self, path: Path, size_limit: int = MAX_SOURCE_BYTES) -> str:
        if path.stat().st_size > size_limit:
            raise ValueError('Input exceeds safe size limit')
        return path.read_text(encoding='utf-8-sig')

    def _source_inspect(self, args: dict) -> dict:
        p = self._resolve(args['file'])
        if p.suffix.lower() not in SOURCE_SUFFIXES:
            raise ValueError('This file type is not supported by static inspection')
        raw = self._read_text(p)
        result = {'path': p.relative_to(self.root).as_posix(), 'sha256': sha256_file(p),
                  'size_bytes': p.stat().st_size, 'language': p.suffix.lower().lstrip('.'),
                  'imports': [], 'definitions': [], 'analysis_type': 'STATIC_METADATA_ONLY',
                  'automatic_decision_approval': False}
        if p.suffix.lower() == '.py':
            tree = ast.parse(raw, filename=p.name)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    result['definitions'].append({'name': node.name, 'line': node.lineno,
                                                  'kind': type(node).__name__})
                elif isinstance(node, ast.Import):
                    result['imports'].extend({'name': a.name, 'line': node.lineno} for a in node.names)
                elif isinstance(node, ast.ImportFrom):
                    result['imports'].append({'name': node.module or '', 'line': node.lineno})
        elif p.suffix.lower() in ('.js', '.jsx', '.ts', '.tsx'):
            for number, line in enumerate(raw.splitlines(), 1):
                m = re.match(r'\s*(?:export\s+)?(?:async\s+)?(?:function|class)\s+([A-Za-z_$][\w$]*)', line)
                if m:
                    result['definitions'].append({'name': m.group(1), 'line': number, 'kind': 'declaration'})
                # Lightweight identifier-only extraction, no code/text excerpts.
                imp = re.match(r'\s*import\s+.*?from\s+[\"\']([\w./@-]+)[\"\']', line)
                if imp:
                    result['imports'].append({'name': imp.group(1), 'line': number})
        elif p.suffix.lower() == '.md':
            for number, line in enumerate(raw.splitlines(), 1):
                m = re.match(r'^(#{1,4})\s+(.{1,100})$', line)
                if m:
                    result['definitions'].append({'name': m.group(2), 'line': number, 'kind': 'heading'})
        result['definitions'] = result['definitions'][:200]
        result['imports'] = result['imports'][:200]
        return result

    def _project_inventory(self, args: dict) -> dict:
        basedir = self._resolve(args.get('directory', '.'), allow_dir=True)
        limit = args.get('limit', MAX_LISTED_FILES)
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_LISTED_FILES:
            raise ValueError('Invalid inventory limit')
        found = []
        for current, dirs, files in os.walk(basedir, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d.lower() not in BLOCKED_PARTS and
                             not d.startswith('.') and not (Path(current) / d).is_symlink())
            for name in sorted(files):
                p = Path(current) / name
                if (name.startswith('.') or name.lower() in BLOCKED_PARTS or p.is_symlink() or
                    p.suffix.lower() in BLOCKED_SUFFIXES or not p.is_file() or
                    p.stat().st_size > MAX_SOURCE_BYTES):
                    continue
                if p.suffix.lower() not in SOURCE_SUFFIXES:
                    continue
                found.append({'path': p.relative_to(self.root).as_posix(),
                              'sha256': sha256_file(p), 'size_bytes': p.stat().st_size})
                if len(found) >= limit:
                    return {'files': found, 'total_files': len(found), 'truncated': True,
                            'result_status': 'PARTIAL_BOUND_LIMIT'}
        return {'files': found, 'total_files': len(found), 'truncated': False,
                'result_status': 'INVENTORY_COMPLETE_WITHIN_FILTERS'}

    def _call(self, name: str, args: dict) -> dict:
        schema = next((x['inputSchema'] for x in TOOLS if x['name'] == name), None)
        if schema is None:
            raise ValueError('Unknown tool')
        if not isinstance(args, dict):
            raise ValueError('Tool arguments must be an object')
        if set(args) - set(schema['properties']):
            raise ValueError('Unexpected tool argument')
        missing = set(schema.get('required', [])) - set(args)
        if missing:
            raise ValueError('Missing arguments: ' + ', '.join(sorted(missing)))
        if name == 'rea_bridge_status':
            return native_runtime()
        if name == 'rea_source_inspect':
            return self._source_inspect(args)
        if name == 'rea_project_inventory':
            return self._project_inventory(args)
        if name in ('rea_internal_analyze', 'rea_arena_compare', 'rea_verify_evidence', 'rea_repositories_top10'):
            from internal_engine import InternalEngine
            engine = InternalEngine(self)
            if name == 'rea_internal_analyze':
                return engine.analyze(args.get('directory', '.'), args.get('limit', 100))
            if name == 'rea_arena_compare':
                return engine.compare_approaches(args.get('objective', 'source_analysis'),
                                                args.get('confidentiality', 'high'))
            if name == 'rea_repositories_top10':
                return engine.repositories_top10(args['catalog'])
            return engine.verify_evidence(args['file'], args['expected_sha256'])
        raise ValueError('Unknown tool')

    def handle(self, message: dict):
        if not isinstance(message, dict) or message.get('jsonrpc') != '2.0':
            return {'jsonrpc': '2.0', 'id': message.get('id') if isinstance(message, dict) else None,
                    'error': {'code': -32600, 'message': 'Invalid request'}}
        method = message.get('method')
        if not isinstance(method, str):
            return {'jsonrpc': '2.0', 'id': message.get('id'),
                    'error': {'code': -32600, 'message': 'Invalid method'}}
        if method == 'notifications/initialized' or (method and method.startswith('notifications/')):
            return None
        ident = message.get('id')
        if method == 'initialize':
            req = message.get('params') or {}
            version = req.get('protocolVersion', '2025-03-26') if isinstance(req, dict) else '2025-03-26'
            return {'jsonrpc': '2.0', 'id': ident, 'result': {'protocolVersion': version,
                    'capabilities': {'tools': {'listChanged': False}},
                    'serverInfo': {'name': SERVER_NAME, 'version': VERSION},
                    'instructions': 'Read-only REA static analysis. Not the upstream rea-agents implementation; no runtime tracing.'}}
        if method == 'ping':
            return {'jsonrpc': '2.0', 'id': ident, 'result': {}}
        if method == 'tools/list':
            return {'jsonrpc': '2.0', 'id': ident, 'result': {'tools': TOOLS}}
        if method == 'tools/call':
            params = message.get('params') or {}
            try:
                if not isinstance(params, dict):
                    raise ValueError('Tool params must be an object')
                data = self._call(params.get('name'), params.get('arguments') or {})
                return {'jsonrpc': '2.0', 'id': ident, 'result': {
                    'content': [{'type': 'text', 'text': json.dumps(data, ensure_ascii=False)}],
                    'isError': False}}
            except (ValueError, KeyError, OSError, TypeError, SyntaxError,
                    subprocess.SubprocessError, UnicodeError, json.JSONDecodeError) as exc:
                # Only broad error class on caller-facing channel, to avoid leaking host paths.
                category = type(exc).__name__
                return {'jsonrpc': '2.0', 'id': ident, 'result': {
                    'content': [{'type': 'text', 'text': json.dumps({'status': 'BLOCKED',
                        'reason': str(exc)[:280] if category == 'ValueError' else category})}],
                    'isError': True}}
        return {'jsonrpc': '2.0', 'id': ident, 'error': {'code': -32601, 'message': 'Method not found'}}
