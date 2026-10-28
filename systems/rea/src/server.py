#!/usr/bin/env python3
"""MCP stdio and loopback HTTP transports for the independent REA static engine.

Web connection requires explicit operator-provided HTTPS proxy/secure tunnel.
Never expose this loopback server to the public Internet directly.
"""
from __future__ import annotations

import argparse
import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from bridge import ReaBridge

MAX_BODY = 131072


def create_server(root: Path, application_root: Path, host: str, port: int, token: str):
    if not isinstance(token, str) or len(token) < 24:
        raise ValueError('REA_MCP_TOKEN must contain at least 24 characters for HTTP use')
    if host not in ('127.0.0.1', 'localhost', '::1'):
        raise ValueError('Bind to loopback only; use a secure HTTPS tunnel for ChatGPT Web')
    bridge = ReaBridge(root, application_root)
    secret = 'Bearer ' + token

    class Handler(BaseHTTPRequestHandler):
        server_version = 'ReaIndependentMCP/0.1.0'
        sys_version = ''

        def log_message(self, *_args):
            return  # Do not log tokens, source names or request bodies.

        def _reply(self, status: int, obj=None):
            data = json.dumps(obj, ensure_ascii=False).encode('utf-8') if obj is not None else b''
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            if data:
                self.wfile.write(data)

        def do_POST(self):
            if self.path != '/mcp':
                return self._reply(404, {'error': 'not found'})
            got = self.headers.get('Authorization', '')
            if not hmac.compare_digest(got, secret):
                return self._reply(401, {'error': 'unauthorized'})
            origin = self.headers.get('Origin', '')
            if origin and origin not in ('https://chatgpt.com', 'http://127.0.0.1', 'http://localhost'):
                return self._reply(403, {'error': 'origin denied'})
            try:
                n = int(self.headers.get('Content-Length', '0'))
                if not 0 < n <= MAX_BODY:
                    return self._reply(413, {'error': 'invalid request size'})
                if self.headers.get('Content-Type', '').split(';')[0].lower() != 'application/json':
                    return self._reply(415, {'error': 'JSON content type required'})
                packet = json.loads(self.rfile.read(n))
                response = bridge.handle(packet)
                if response is None:
                    return self._reply(202)
                return self._reply(200, response)
            except (ValueError, UnicodeError, json.JSONDecodeError):
                return self._reply(400, {'error': 'invalid JSON-RPC request'})

        def do_GET(self):
            return self._reply(405, {'error': 'POST required'})

        def do_OPTIONS(self):
            return self._reply(405, {'error': 'POST required'})

    return ThreadingHTTPServer((host, port), Handler)


def run_stdio(root: Path, application_root: Path) -> None:
    bridge = ReaBridge(root, application_root)
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            result = bridge.handle(request)
        except (ValueError, UnicodeError, json.JSONDecodeError):
            result = {'jsonrpc': '2.0', 'id': None,
                      'error': {'code': -32700, 'message': 'Parse error'}}
        if result is not None:
            sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(',', ':')) + '\n')
            sys.stdout.flush()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--transport', choices=['stdio', 'http'], default='stdio')
    p.add_argument('--root', required=True, help='Explicit local authorized data root')
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8768)
    a = p.parse_args()
    app_root = Path(__file__).resolve().parents[1]
    if a.transport == 'stdio':
        run_stdio(Path(a.root), app_root)
    else:
        token = os.environ.get('REA_MCP_TOKEN', '')
        server = create_server(Path(a.root), app_root, a.host, a.port, token)
        print(f'REA read-only MCP local HTTP serving on {a.host}:{a.port}/mcp', file=sys.stderr)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == '__main__':
    main()
