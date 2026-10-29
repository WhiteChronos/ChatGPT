#!/usr/bin/env python3
"""Safe, authenticated, read-only HTTPS smoke for an ALREADY AUTHORIZED REA MCP host.

This does not deploy services, install the official REA, discover ChatGPT host
plugins or certify PRODUCTION_COMPLETE. Token is read only from an environment
variable, never a command-line argument or a JSON report.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

EXPECTED = frozenset({'rea_bridge_status', 'rea_source_inspect', 'rea_project_inventory',
                      'rea_internal_analyze', 'rea_arena_compare',
                      'rea_repositories_top10', 'rea_verify_evidence'})


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _safe_https_url(url: str) -> tuple[bool, str]:
    try:
        p = urlsplit(url)
        valid = (p.scheme == 'https' and bool(p.hostname) and p.path == '/mcp' and
                 p.username is None and p.password is None and not p.query and not p.fragment and
                 p.hostname not in ('localhost', '127.0.0.1', '::1') and
                 (p.port is None or 1 <= p.port <= 65535))
        return bool(valid), (p.hostname or 'UNCONFIGURED') if valid else 'UNCONFIGURED'
    except (TypeError, ValueError, AttributeError):
        return False, 'UNCONFIGURED'


def assess(url: str | None, token: str | None, *, opener=None) -> dict:
    """Return only constrained endpoint evidence, never secrets or source code."""
    url_ok, hostname = _safe_https_url(url or '')
    checks = {'tls_url': 'PASS' if url_ok else 'BLOCKED',
              'authentication_configured': 'PASS' if isinstance(token, str) and len(token) >= 24 else 'BLOCKED',
              'unauthorized_denied': 'NOT_TESTED', 'initialize': 'NOT_TESTED',
              'tool_inventory': 'NOT_TESTED', 'safe_tool_call': 'NOT_TESTED'}
    result = {'product': 'REA_INDEPENDENTE',
              'checked_at_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'endpoint_host': hostname, 'status': 'BLOCKED', 'checks': checks,
              'host_discovered': False, 'production_complete': False,
              'note': 'Passing endpoint checks is NOT ChatGPT Web tool discovery or operational acceptance.'}
    if checks['tls_url'] != 'PASS' or checks['authentication_configured'] != 'PASS':
        return result
    if opener is None:
        # Python's HTTPSHandler uses certificate verification by default.
        # Redirects are disabled to prevent authorization forwarding to new hosts.
        opener = build_opener(NoRedirect).open

    def request(payload: dict, *, authenticated: bool) -> dict:
        body = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        headers = {'Content-Type': 'application/json', 'Origin': 'https://chatgpt.com'}
        if authenticated:
            headers['Authorization'] = 'Bearer ' + token
        req = Request(url, data=body, headers=headers, method='POST')
        with opener(req, timeout=8) as response:
            if response.getcode() != 200:
                raise ValueError('Endpoint did not return HTTP 200')
            raw = response.read(131073)
            if len(raw) > 131072:
                raise ValueError('Endpoint response exceeds bounded size')
            obj = json.loads(raw)
            if not isinstance(obj, dict) or obj.get('jsonrpc') != '2.0' or obj.get('id') != payload['id']:
                raise ValueError('Unexpected JSON-RPC envelope')
            if not isinstance(obj.get('result'), dict) or 'error' in obj:
                raise ValueError('JSON-RPC returned an error')
            return obj['result']

    try:
        request({'jsonrpc':'2.0','id':91,'method':'initialize','params':{}},authenticated=False)
        # A rejecting HTTPError is the required safe failure mode.
        checks['unauthorized_denied'] = 'BLOCKED'
        return result
    except HTTPError as e:
        checks['unauthorized_denied'] = 'PASS' if e.code in (401,403) else 'BLOCKED'
        if checks['unauthorized_denied'] != 'PASS':
            return result
    except (URLError, OSError, ValueError, TypeError, json.JSONDecodeError):
        checks['unauthorized_denied'] = 'BLOCKED'
        return result

    try:
        info = request({'jsonrpc':'2.0','id':1,'method':'initialize','params':{}},authenticated=True)
        if info.get('serverInfo', {}).get('name') != 'rea-independent-engine':
            raise ValueError('Unexpected REA server identity')
        checks['initialize'] = 'PASS'
        catalog = request({'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},authenticated=True)
        names = {x['name'] for x in catalog.get('tools', [])}
        if not EXPECTED.issubset(names):
            checks['tool_inventory'] = 'BLOCKED'
            return result
        checks['tool_inventory'] = 'PASS'
        output = request({'jsonrpc':'2.0','id':3,'method':'tools/call',
                          'params': {'name': 'rea_bridge_status', 'arguments':{}}},authenticated=True)
        if output.get('isError') is not False:
            checks['safe_tool_call'] = 'BLOCKED'
            return result
        checks['safe_tool_call'] = 'PASS'
        result['status'] = 'ENDPOINT_SMOKE_PASS'
    except (HTTPError, URLError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        # No local path, remote error body or Authorization header is exposed.
        if checks['initialize'] != 'PASS': checks['initialize'] = 'BLOCKED'
        elif checks['tool_inventory'] != 'PASS': checks['tool_inventory'] = 'BLOCKED'
        else: checks['safe_tool_call'] = 'BLOCKED'
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', help='Operator-approved HTTPS MCP URL ending in /mcp')
    args = parser.parse_args()
    report = assess(args.url, os.environ.get('REA_MCP_TOKEN'))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['status'] == 'ENDPOINT_SMOKE_PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
