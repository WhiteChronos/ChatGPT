#!/usr/bin/env python3
"""Loopback-only authenticated Web UI and read-only MCP gateway for REA Independent.

Not a hosted Internet service. Do not expose directly or use as a substitute
for the official upstream REA. A production remote MCP endpoint requires
approved HTTPS reverse proxy, managed authentication and a runtime smoke test.
"""
from __future__ import annotations

import argparse
import hmac
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response

from bridge import ReaBridge, TOOLS

MAX_BODY = 131072
LOCAL_HOSTS = ('127.0.0.1', 'localhost', '::1')


def assert_safe_bind(host: str) -> str:
    if host not in LOCAL_HOSTS:
        raise ValueError('Refusing public bind: REA Independent Web must be loopback-only')
    return host


def _allowed_origin(origin: str) -> bool:
    if not origin:
        return True
    try:
        parsed = urlsplit(origin)
        return (parsed.scheme == 'http' and parsed.hostname in LOCAL_HOSTS and
                parsed.username is None and parsed.password is None and
                parsed.path in ('', '/') and not parsed.query and not parsed.fragment)
    except ValueError:
        return False


def create_app(root: Path, app_root: Path, token: str) -> FastAPI:
    if not isinstance(token, str) or len(token) < 24:
        raise ValueError('REA_MCP_TOKEN must contain at least 24 characters')
    bridge = ReaBridge(root, app_root)
    asset_dir = Path(__file__).resolve().parent / 'assets'
    app = FastAPI(title='REA Independent Web', version='2.0.0', docs_url=None, redoc_url=None,
                  openapi_url=None)
    bearer = 'Bearer ' + token

    @app.middleware('http')
    async def security_headers(request: Request, next_handler):
        response = await next_handler(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = (
            "default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self' data:; base-uri 'none'; "
            "form-action 'self'; frame-ancestors 'none'")
        return response

    def authorize(request: Request):
        if not hmac.compare_digest(request.headers.get('authorization', ''), bearer):
            return JSONResponse({'error': 'Unauthorized'}, status_code=401)
        if not _allowed_origin(request.headers.get('origin', '')):
            return JSONResponse({'error': 'Cross-origin requests denied'}, status_code=403)
        return None

    async def parse_request(request: Request):
        typ = request.headers.get('content-type', '').split(';')[0].lower().strip()
        if typ != 'application/json':
            return None, JSONResponse({'error': 'application/json required'}, status_code=415)
        if int(request.headers.get('content-length', 0) or 0) > MAX_BODY:
            return None, JSONResponse({'error': 'Request too large'}, status_code=413)
        buf = await request.body()
        if len(buf) > MAX_BODY:
            return None, JSONResponse({'error': 'Request too large'}, status_code=413)
        try:
            value = json.loads(buf)
        except (ValueError, UnicodeDecodeError):
            return None, JSONResponse({'error': 'Invalid JSON'}, status_code=400)
        if not isinstance(value, dict):
            return None, JSONResponse({'error': 'Object required'}, status_code=400)
        return value, None

    @app.get('/')
    def index():
        return FileResponse(asset_dir / 'index.html', media_type='text/html')

    @app.get('/assets/app.js')
    def ui_js():
        return FileResponse(asset_dir / 'app.js', media_type='text/javascript')

    @app.get('/assets/app.css')
    def ui_css():
        return FileResponse(asset_dir / 'app.css', media_type='text/css')

    @app.get('/api/health')
    def health():
        return {'service': 'REA Independent', 'transport': 'WEB_LOCAL',
                'upstream_rea': 'NOT_ASSUMED_AVAILABLE', 'mode': 'READ_ONLY'}

    @app.post('/api/tool/{name}')
    async def tool(request: Request, name: str):
        deny = authorize(request)
        if deny:
            return deny
        args, problem = await parse_request(request)
        if problem:
            return problem
        if name not in {t['name'] for t in TOOLS}:
            return JSONResponse({'error': 'Unknown tool'}, status_code=404)
        try:
            output = bridge._call(name, args)
            return JSONResponse(output)
        except (ValueError, KeyError, OSError, SyntaxError, TypeError):
            # Never return local filesystem paths, source snippets or exception bodies.
            return JSONResponse({'error': 'Request denied by read-only analysis policy'}, status_code=422)

    @app.post('/mcp')
    async def mcp(request: Request):
        deny = authorize(request)
        if deny:
            return deny
        msg, problem = await parse_request(request)
        if problem:
            return problem
        reply = bridge.handle(msg)
        if reply is None:
            return Response(status_code=202)
        return JSONResponse(reply)

    @app.get('/mcp')
    def mcp_get_disabled():
        return JSONResponse({'error': 'POST required'}, status_code=405)

    return app


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True, help='Explicit authorized local analysis root')
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8769)
    args = p.parse_args()
    assert_safe_bind(args.host)
    root = Path(args.root).resolve(strict=True)
    app_root = Path(__file__).resolve().parents[1]
    token = os.environ.get('REA_MCP_TOKEN', '')
    app = create_app(root, app_root, token)
    uvicorn.run(app, host=args.host, port=args.port, access_log=False, server_header=False)


if __name__ == '__main__':
    main()
