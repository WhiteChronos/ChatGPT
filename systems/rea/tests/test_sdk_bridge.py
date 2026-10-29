"""TDD: safe, isolated REA tools exposed through the official MCP SDK."""
from __future__ import annotations
import asyncio
import importlib.util
import sys
import types
import socket
import subprocess
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
EXPECTED = {
    'rea_bridge_status', 'rea_source_inspect', 'rea_project_inventory',
    'rea_internal_analyze', 'rea_arena_compare', 'rea_repositories_top10',
    'rea_verify_evidence',
}


class FakeToolError(Exception):
    pass


class FakeMCPServer:
    def __init__(self, name, **kwargs):
        self.name = name
        self.handlers = {}
        self.annotations = {}
        self.run_settings = None

    def tool(self, **kwargs):
        def register(fn):
            self.handlers[fn.__name__] = fn
            self.annotations[fn.__name__] = kwargs.get("annotations")
            return fn
        return register

    def run(self, **kwargs):
        self.run_settings = kwargs


@pytest.fixture
def shim_sdk(monkeypatch):
    mcp = types.ModuleType('mcp')
    server = types.ModuleType('mcp.server')
    mcpserver = types.ModuleType('mcp.server.mcpserver')
    errors = types.ModuleType('mcp.server.mcpserver.exceptions')
    types_module = types.ModuleType('mcp.types')
    class FakeToolAnnotations:
        def __init__(self, **kwargs):
            for name, value in kwargs.items():
                setattr(self, name, value)
    types_module.ToolAnnotations = FakeToolAnnotations
    server.MCPServer = FakeMCPServer
    errors.ToolError = FakeToolError
    for key, module in [('mcp',mcp),('mcp.server',server),('mcp.server.mcpserver',mcpserver),
                        ('mcp.server.mcpserver.exceptions',errors),('mcp.types',types_module)]:
        monkeypatch.setitem(sys.modules,key,module)
    return FakeMCPServer


def _load_new_adapter():
    target = SRC / 'sdk_server.py'
    spec = importlib.util.spec_from_file_location('sdk_server_isolated_test', target)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_official_adapter_exports_all_seven_readonly_tools_without_other_product(tmp_path, shim_sdk):
    (tmp_path/'source.py').write_text('import os\ndef sample(): return 1\n')
    app = _load_new_adapter().build_server(tmp_path)
    assert set(app.handlers) == EXPECTED
    assert app.name == 'rea-independent-engine'
    assert all(a.read_only_hint and not a.destructive_hint and not a.open_world_hint
               for a in app.annotations.values())
    result = app.handlers['rea_source_inspect']('source.py')
    assert result['definitions'][0]['name'] == 'sample'
    assert app.handlers['rea_project_inventory']()['files'][0]['path'] == 'source.py'
    assert 'native_status' in app.handlers['rea_bridge_status']()


def test_sdk_adapter_denies_escapes_without_host_path_leak(tmp_path, shim_sdk):
    _ = (tmp_path/'source.py').write_text('value=1')
    app = _load_new_adapter().build_server(tmp_path)
    with pytest.raises(FakeToolError) as ex:
        app.handlers['rea_source_inspect']('../secrets.py')
    assert 'secrets.py' not in str(ex.value)
    assert str(tmp_path) not in str(ex.value)


def test_sdk_cli_denies_public_http_bind(tmp_path, shim_sdk, monkeypatch):
    module = _load_new_adapter()
    with pytest.raises(ValueError):
        module.assert_safe_bind('0.0.0.0')
    with pytest.raises(ValueError):
        module.assert_safe_bind('::')
    assert module.assert_safe_bind('127.0.0.1') == '127.0.0.1'
    app = module.build_server(tmp_path)
    module.serve(app, transport='streamable-http', host='127.0.0.1', port=8768)
    assert app.run_settings == {'transport': 'streamable-http', 'host':'127.0.0.1',
                                'port': 8768, 'stateless_http':True, 'json_response':True}


def test_mcp_sdk_client_inprocess(tmp_path):
    """CI with official SDK: protocol negotiation + discovery + safe call."""
    mcp = pytest.importorskip('mcp', reason='Official MCP Python SDK required in CI')
    from mcp import Client
    module = _load_new_adapter()
    (tmp_path/'source.py').write_text('import pathlib\ndef sample(): return 1\n')
    async def run():
        async with Client(module.build_server(tmp_path)) as client:
            assert {t.name for t in (await client.list_tools()).tools} == EXPECTED
            meta = await client.call_tool('rea_source_inspect', {'file':'source.py'})
            assert not meta.is_error
            assert 'source.py' in str(meta.content)
            denied = await client.call_tool('rea_source_inspect', {'file':'../secret.py'})
            assert denied.is_error
    asyncio.run(run())


def test_mcp_sdk_client_stdio(tmp_path):
    """CI with official SDK: spawn real subprocess over MCP stdio."""
    mcp = pytest.importorskip('mcp', reason='Official MCP Python SDK required in CI')
    from mcp import Client, StdioServerParameters
    async def run():
        proc = StdioServerParameters(command=sys.executable, args=[str(SRC/'sdk_server.py'),
            '--root',str(tmp_path),'--transport','stdio'])
        async with Client(proc) as client:
            assert {t.name for t in (await client.list_tools()).tools} == EXPECTED
            result = await client.call_tool('rea_bridge_status', {})
            assert not result.is_error
    asyncio.run(run())


def test_mcp_sdk_client_streamable_http(tmp_path):
    """CI with official SDK: actual HTTP transport, not a hand-rolled JSON-RPC mock."""
    mcp = pytest.importorskip('mcp', reason='Official MCP Python SDK required in CI')
    from mcp import Client
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',0))
        port = probe.getsockname()[1]
    proc = subprocess.Popen([sys.executable,str(SRC/'sdk_server.py'), '--root',str(tmp_path),
             '--transport','streamable-http','--port',str(port)],
             stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    try:
        for _ in range(80):
            if proc.poll() is not None:
                raise AssertionError('Official MCP HTTP process stopped: ' + str(proc.returncode))
            with socket.socket() as sock:
                sock.settimeout(0.3)
                if sock.connect_ex(('127.0.0.1',port)) == 0:
                    break
            time.sleep(0.15)
        else:
            raise AssertionError('MCP HTTP server did not bind on loopback')
        async def run():
            async with Client(f'http://127.0.0.1:{port}/mcp') as client:
                assert {t.name for t in (await client.list_tools()).tools} == EXPECTED
                result = await client.call_tool('rea_bridge_status', {})
                assert not result.is_error
        asyncio.run(run())
        # DNS rebinding protection is mandatory for private local servers.
        for header, expected_code in (({'Host':'evil.example.invalid'},421),
                                      ({'Origin':'https://evil.example.invalid'},403)):
            with pytest.raises(HTTPError) as denied:
                urlopen(Request(f'http://127.0.0.1:{port}/mcp',headers=header),timeout=3)
            assert denied.value.code == expected_code
    finally:
        proc.terminate()
        try:
            proc.communicate(timeout=8)
        except subprocess.TimeoutExpired:
            proc.kill(); proc.communicate(timeout=3)
