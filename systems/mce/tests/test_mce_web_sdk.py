import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'mce_status', 'mce_read_skill', 'mce_inspect_model', 'mce_initialize',
            'mce_understand', 'mce_approval_request', 'mce_apply'}


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.mark.anyio
async def test_official_sdk_stdio_discovery_status_and_denied_path(tmp_path):
    server = ROOT / 'scripts/mce_sdk_server.py'
    assert server.is_file(), 'MCE official SDK server missing'
    from mcp import Client, StdioServerParameters
    root = tmp_path / 'authorized'
    (root / 'inbox').mkdir(parents=True)
    (root / 'projects').mkdir()
    approvals = tmp_path / 'approvals'
    approvals.mkdir()
    proc = StdioServerParameters(command=sys.executable,
        args=[str(server), '--root', str(root), '--approvals', str(approvals)])
    async with Client(proc) as client:
        tools = (await client.list_tools()).tools
        assert {item.name for item in tools} == EXPECTED
        assert all(not item.annotations.read_only_hint for item in tools if item.name in {'mce_initialize','mce_understand','mce_apply'})
        assert not (await client.call_tool('mce_status', {})).is_error
        assert not (await client.call_tool('mce_read_skill', {'skill':'engenharia-mce-projeto'})).is_error
        denied = await client.call_tool('mce_inspect_model', {'filename':'../outside.xlsx'})
        assert denied.is_error
        assert str(root) not in str(denied.content)
