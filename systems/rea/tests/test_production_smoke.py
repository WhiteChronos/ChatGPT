"""TDD: MCP remoto HTTPS e prova restrita de endpoint, nao certificacao de producao."""
import importlib.util
import io
import json
from pathlib import Path
from urllib.error import HTTPError
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('rea_production_smoke', ROOT / 'scripts/production_smoke.py')
EXPECTED = frozenset({'rea_bridge_status', 'rea_source_inspect', 'rea_project_inventory',
                      'rea_internal_analyze', 'rea_arena_compare',
                      'rea_repositories_top10', 'rea_verify_evidence'})


def load():
    module = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(module)
    return module


class Answer:
    def __init__(self, value): self.raw = json.dumps(value).encode('utf-8')
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self, size=-1): return self.raw if size < 0 else self.raw[:size]
    def getcode(self): return 200


def fake_live_server(request, timeout):
    assert 0 < timeout <= 20
    if not request.headers.get('Authorization'):
        raise HTTPError(request.full_url, 401, 'unauthorized', {}, io.BytesIO(b''))
    assert request.headers.get('Origin') == 'https://chatgpt.com'
    assert request.full_url == 'https://rea.example.invalid/mcp'
    payload = json.loads(request.data)
    method = payload['method']
    if method == 'initialize':
        value = {'serverInfo': {'name': 'rea-independent-engine'}}
    elif method == 'tools/list':
        value = {'tools': [{'name': name} for name in sorted(EXPECTED)]}
    elif method == 'tools/call':
        assert payload['params']['name'] == 'rea_bridge_status'
        value = {'isError': False, 'content': [{'type': 'text', 'text': json.dumps({'implementation': 'INDEPENDENT_REA_STATIC_ENGINE_NOT_UPSTREAM_REA'})}]}
    else: raise AssertionError(method)
    return Answer({'jsonrpc':'2.0', 'id': payload['id'], 'result': value})


def test_blocks_http_and_url_userinfo():
    probe = load().assess
    for u in ('http://rea.example.invalid/mcp', 'https://user:pass@rea.example.invalid/mcp',
              'https://rea.example.invalid/mcp?token=secret', 'https://rea.example.invalid/admin'):
        report = probe(u, 'k'*40, opener=fake_live_server)
        assert report['status'] == 'BLOCKED', u
        assert report['production_complete'] is False


def test_missing_token_blocks_without_any_network():
    def unexpected(*_args, **_kw): raise AssertionError('No requests expected')
    report = load().assess('https://rea.example.invalid/mcp', None, opener=unexpected)
    assert report['status'] == 'BLOCKED'


def test_remote_smoke_checks_real_rpc_tool_names_auth_and_origin():
    report = load().assess('https://rea.example.invalid/mcp', 'k'*40, opener=fake_live_server)
    assert report['status'] == 'ENDPOINT_SMOKE_PASS'
    assert report['checks']['tls_url'] == 'PASS'
    assert report['checks']['unauthorized_denied'] == 'PASS'
    assert report['checks']['tool_inventory'] == 'PASS'
    assert report['checks']['safe_tool_call'] == 'PASS'
    assert report['host_discovered'] is False
    assert report['production_complete'] is False
    assert 'k'*40 not in json.dumps(report)


def test_missing_tools_blocks():
    def missing(req, timeout):
        if req.headers.get('Authorization') and json.loads(req.data)['method'] == 'tools/list':
            return Answer({'jsonrpc':'2.0', 'id':2, 'result': {'tools':[{'name':'rea_bridge_status'}]}})
        return fake_live_server(req, timeout)
    report = load().assess('https://rea.example.invalid/mcp', 'k'*40, opener=missing)
    assert report['status'] == 'BLOCKED'
    assert report['checks']['tool_inventory'] == 'BLOCKED'


def test_redirect_is_rejected_without_exposing_token():
    def redirect(req,timeout):
        raise HTTPError(req.full_url, 302, 'redirect', {'Location':'http://untrusted.invalid'},io.BytesIO(b''))
    report = load().assess('https://rea.example.invalid/mcp', 'k'*40, opener=redirect)
    assert report['status'] == 'BLOCKED'
    assert 'k'*40 not in json.dumps(report)
