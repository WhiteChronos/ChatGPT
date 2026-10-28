#!/usr/bin/env python3
"""Bounded, independent static analysis for standalone REA gateway.

This is NOT upstream morluto/rea, a decompiler, a dynamic tracer or proof of exploitability. It reads authorized source metadata only and never
returns code bodies, literals, credentials or extracted file content.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

SOURCE_CODE = {'.py', '.js', '.jsx', '.ts', '.tsx'}
JS_EXTENSIONS = ('.ts', '.tsx', '.js', '.jsx')
MAX_FILES = 100
MAX_TOTAL_BYTES = 8_000_000


class InternalEngine:
    def __init__(self, bridge):
        self.bridge = bridge

    @staticmethod
    def _digest(path: Path) -> str:
        h = hashlib.sha256()
        with path.open('rb') as reader:
            for block in iter(lambda: reader.read(262144), b''):
                h.update(block)
        return h.hexdigest()

    def verify_evidence(self, file: str, expected_sha256: str) -> dict:
        if not isinstance(expected_sha256, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', expected_sha256):
            raise ValueError('A valid 64-character SHA-256 digest is required')
        path = self.bridge._resolve(file)
        if path.stat().st_size > MAX_TOTAL_BYTES:
            raise ValueError('File too large for bounded evidence check')
        observed = self._digest(path)
        return {'file': path.relative_to(self.bridge.root).as_posix(),
                'expected_sha256': expected_sha256.lower(),
                'observed_sha256': observed,
                'integrity': 'MATCH' if observed == expected_sha256.lower() else 'MISMATCH',
                'observation': 'BYTE_HASH_ONLY_NO_SEMANTIC_APPROVAL',
                'automatic_decision_approval': False}

    @staticmethod
    def _resolve_target(file: str, name: str, *, python: bool, level: int = 0) -> list[str]:
        """Return lexical import target candidates; no filesystem reads or path traversal."""
        if not isinstance(name, str) or not name:
            return []
        current = PurePosixPath(file)
        if python:
            parents = current.parent.parts
            if level:
                parent = parents[:max(0, len(parents) - (level - 1))]
                prefix = '/'.join(parent)
                module = (prefix + '/' if prefix else '') + name.replace('.', '/')
            else:
                module = name.replace('.', '/')
            candidates = [module + '.py', module + '/__init__.py']
        else:
            if not name.startswith('.'):
                return []
            pieces = list(current.parent.parts)
            for piece in name.replace('\\', '/').split('/'):
                if piece == '..':
                    if not pieces:
                        return []
                    pieces.pop()
                elif piece not in ('', '.'):
                    pieces.append(piece)
            module = '/'.join(pieces)
            candidates = [module] if PurePosixPath(module).suffix in JS_EXTENSIONS else []
            candidates.extend(module + e for e in JS_EXTENSIONS)
            candidates.extend(module + '/index' + e for e in JS_EXTENSIONS)
        return candidates

    @staticmethod
    def _candidate(rule_id: str, severity: str, path: str, line: int, sha: str) -> dict:
        return {'rule_id': rule_id, 'severity': severity, 'file': path,
                'line': line, 'source_sha256': sha,
                'classification': 'REVIEW_REQUIRED_NOT_CONFIRMED',
                'automatic_decision_approval': False}

    def _inspect_python(self, path: str, data: str, sha: str):
        refs, symbols, findings = [], [], []
        try:
            parsed = ast.parse(data)
        except SyntaxError:
            findings.append(self._candidate('PY_PARSE_UNAVAILABLE', 'LOW', path, 0, sha))
            return refs, symbols, findings
        for node in ast.walk(parsed):
            line = getattr(node, 'lineno', 0)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbols.append({'name': node.name, 'line': line, 'kind': type(node).__name__})
            elif isinstance(node, ast.Import):
                refs.extend((name.name, 0, line) for name in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    refs.append((node.module, node.level, line))
                elif node.level:
                    refs.extend((n.name, node.level, line) for n in node.names if n.name != '*')
            elif isinstance(node, ast.Call):
                f = node.func
                if isinstance(f, ast.Name) and f.id in ('eval', 'exec'):
                    findings.append(self._candidate('PY_DYNAMIC_EXECUTION', 'HIGH', path, line, sha))
                if isinstance(f, ast.Attribute) and f.attr in ('run', 'Popen', 'call', 'check_output'):
                    for kw in node.keywords:
                        if kw.arg == 'shell' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            findings.append(self._candidate('PY_SUBPROCESS_SHELL', 'HIGH', path, line, sha))
                if isinstance(f, ast.Attribute) and f.attr == 'loads' and isinstance(f.value, ast.Name) and f.value.id == 'pickle':
                    findings.append(self._candidate('PY_PICKLE_LOADS', 'MEDIUM', path, line, sha))
        return refs, symbols[:200], findings[:150]

    def _inspect_js(self, path: str, data: str, sha: str):
        refs, symbols, findings = [], [], []
        for line_no, line in enumerate(data.splitlines(), 1):
            m = re.search(r'\b(?:import|export)\s+.*?\bfrom\s*["\']([^"\']+)["\']', line)
            if m:
                refs.append((m.group(1), 0, line_no))
            for found in re.finditer(r'\brequire\s*\(\s*["\']([^"\']+)["\']\s*\)', line):
                refs.append((found.group(1), 0, line_no))
            declaration = re.match(r'\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function|class)\s+([\w$]+)', line)
            if declaration:
                symbols.append({'name': declaration.group(1), 'line': line_no, 'kind': 'declaration'})
            if re.search(r'\beval\s*\(|\bnew\s+Function\s*\(', line):
                findings.append(self._candidate('JS_DYNAMIC_EVAL', 'HIGH', path, line_no, sha))
            if re.search(r'\bchild_process\b', line):
                findings.append(self._candidate('JS_CHILD_PROCESS', 'MEDIUM', path, line_no, sha))
        return refs[:200], symbols[:200], findings[:150]

    def analyze(self, directory: str = '.', limit: int = MAX_FILES) -> dict:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_FILES:
            raise ValueError('Invalid analysis limit (1..100)')
        inventory = self.bridge._project_inventory({'directory': directory, 'limit': limit})
        all_files = [f for f in inventory['files'] if PurePosixPath(f['path']).suffix.lower() in SOURCE_CODE]
        indexed = {f['path'] for f in all_files}
        nodes, edges, findings, pending_edges = [], [], [], []
        consumed = 0
        truncated = inventory['truncated']
        byte_limit_reached = False
        for entry in all_files:
            raw_file = entry['path']
            file = self.bridge._resolve(raw_file)
            size = file.stat().st_size
            if consumed + size > MAX_TOTAL_BYTES:
                byte_limit_reached = True
                truncated = True
                break
            data = self.bridge._read_text(file)
            consumed += size
            sha = self._digest(file)
            if file.suffix.lower() == '.py':
                refs, symbols, flags = self._inspect_python(raw_file, data, sha)
            else:
                refs, symbols, flags = self._inspect_js(raw_file, data, sha)
            nodes.append({'file': raw_file, 'sha256': sha, 'language': file.suffix.lower().lstrip('.'),
                          'size_bytes': size, 'symbols': symbols})
            findings.extend(flags)
            for name, level, at_line in refs:
                possible = self._resolve_target(raw_file, name,
                       python=file.suffix.lower() == '.py', level=level)
                for target in possible:
                    if target in indexed:
                        pending_edges.append({'source': raw_file, 'target': target,
                                              'kind': 'STATIC_IMPORT', 'line': at_line,
                                              'source_sha256': sha})
                        break
        actual = {n['file'] for n in nodes}
        edges = [e for e in pending_edges if e['target'] in actual]
        edges.sort(key=lambda e: (e['source'], e['target'], e['line']))
        findings.sort(key=lambda x: (x['file'], x['line'], x['rule_id']))
        status = 'PARTIAL_BYTE_BUDGET' if byte_limit_reached else ('PARTIAL_LIMIT' if truncated else 'COMPLETE_WITHIN_SCOPE')
        return {
            'engine': 'REA_INDEPENDENT_STATIC_ANALYZER_V1',
            'upstream_rea_executed': False,
            'analysis_kind': 'STATIC_SOURCE_GRAPH_AND_CANDIDATE_RULES',
            'coverage': {'status': status, 'files_analyzed': len(nodes),
                         'bytes_read': consumed, 'truncated': bool(truncated),
                         'selection': 'ROOT_FILTERED_SOURCE_FILES_ONLY',
                         'dynamic_execution_observed': False},
            'graph': {'nodes': nodes, 'edges': edges},
            'findings': findings[:200],
            'limitations': ['Imports are lexical references, not proven runtime execution.',
                            'Static risk flags require review; they are not confirmed vulnerabilities.',
                            'No native disassembly, decompilation, browser instrumentation or live tracing.',
                            'Findings require independent human validation.'],
            'automatic_decision_approval': False}

    def repositories_top10(self, catalog: str) -> dict:
        """Review only a user-provided, previously curated JSON; no live GitHub claim."""
        file = self.bridge._resolve(catalog)
        if file.suffix.lower() != '.json' or file.stat().st_size > 200_000:
            raise ValueError('A small JSON catalog is required')
        data = json.loads(file.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or not isinstance(data.get('reviewed'), list):
            raise ValueError('Expected reviewed array in catalog')
        raw = data['reviewed']
        if len(raw) > 100 or any(not isinstance(x, dict) for x in raw):
            raise ValueError('At most 100 repository records allowed')
        output = []
        for row in raw:
            repo = row.get('repo')
            score = row.get('score_editorial')
            license_id = row.get('license') or 'NAO_IDENTIFICADA'
            if not isinstance(repo, str) or not repo or not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 100:
                raise ValueError('Invalid curated repository record')
            output.append({'repo': repo, 'url': row.get('url'), 'head': row.get('head'),
                           'license': license_id, 'score_editorial': score,
                           'requires_license_review': license_id in ('AGPL-3.0', 'GPL-3.0', 'NAO_IDENTIFICADA')})
        output.sort(key=lambda x: (-x['score_editorial'], x['repo']))
        return {
            'catalog_date': data.get('captured_at'),
            'catalog_file': file.relative_to(self.bridge.root).as_posix(),
            'catalog_sha256': self._digest(file),
            'reviewed_candidates': len(output),
            'evaluation': 'USER_CURATED_SNAPSHOT_NOT_LIVE_TOURNAMENT',
            'finalists': output[:10], 'automatically_installed': False,
            'external_calls_performed': False,
            'limitations': ['Scores are provided by the catalog owner, not measured by this tool.',
                            'GitHub metadata and license status are not refreshed by this operation.']}

    def compare_approaches(self, objective: str = 'source_analysis', confidentiality: str = 'high') -> dict:
        if objective not in ('source_analysis', 'native_binary', 'web_application'):
            raise ValueError('Unknown objective')
        if confidentiality not in ('high', 'normal'):
            raise ValueError('Unknown confidentiality')
        weights = {'correctness': 30, 'completeness': 25, 'robustness': 20,
                   'specificity': 15, 'clarity': 10}
        # Scores are explicit heuristic strategy review, NOT observed model benchmark results.
        from bridge import native_runtime
        native = native_runtime()
        native_ready = False  # host discovery and execution proof are separate gates.
        cards = [
          {'id': 'OFFICIAL_NATIVE_REA', 'eligible': native_ready,
           'marks': [90,95,90,75,75],
           'blocker': 'REA_MCP_NOT_LIVE_VERIFIED',
           'review': 'Most complete downstream option; requires compatible runtime and validated host discovery.'},
          {'id': 'INTERNAL_STATIC_REVIEW', 'eligible': objective == 'source_analysis',
           'marks': [90,65,95,95,90], 'blocker': None if objective == 'source_analysis' else 'TARGET_NOT_SUPPORTED_BY_STATIC_ENGINE',
           'review': 'Bounded local source analysis with SHA-256 and manual validation.'},
          {'id': 'EXTERNAL_CLOUD_ANALYSIS', 'eligible': False,
           'marks': [65,75,60,55,65],
           'blocker': 'CONFIDENTIAL_DATA_EXTERNAL_PROCESSING_NOT_AUTHORIZED' if confidentiality == 'high' else 'CLOUD_TRANSFER_REQUIRES_EXPLICIT_AUTHORIZATION',
           'review': 'External data transfer and unpredictable operating costs require separate authorization.'},
          {'id': 'UNCONTROLLED_FORK_MERGE', 'eligible': False,
           'marks': [35,85,25,45,35], 'blocker': 'UNREVIEWED_CODE_AND_LICENSES',
           'review': 'Uncontrolled copy of upstream project is not reproducible or safe.'}
        ]
        for c in cards:
            c['weighted_score'] = sum(v*w for v,w in zip(c.pop('marks'), weights.values()))/100
        eligible = [c for c in cards if c['eligible']]
        selected = max(eligible, key=lambda c: c['weighted_score']) if eligible else None
        return {
            'method': 'ARENA_FOUR_PERSPECTIVE_POLICY_REVIEW',
            'independent_agents_executed': False,
            'empirical_product_benchmark': False,
            'objective': objective, 'confidentiality': confidentiality,
            'rubric': weights, 'strategies': cards,
            'selected': {'id': selected['id'], 'score': selected['weighted_score']} if selected else None,
            'gate': 'OFFICIAL_REA_MCP_REQUIRED' if not selected else 'STATIC_MANUAL_REVIEW_ONLY',
            'native_rea_status': native['native_status'],
            'superpowers_gates': ['TDD_RED_GREEN', 'REVIEW', 'VERIFICATION'],
            'automatic_decision_approval': False}
