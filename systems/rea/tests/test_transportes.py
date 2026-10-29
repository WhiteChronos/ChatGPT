"""Independent engine regression for local MCP, Web and source confinement."""
from pathlib import Path
import hashlib
import json
import socket
import subprocess
import sys
import threading
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bridge import ReaBridge, node_eligible
from server import create_server


def rpc(method, params=None, ident=5):
    return {'jsonrpc':'2.0','id':ident,'method':method,'params':params or {}}


def tool(name, args=None):
    return rpc('tools/call',{'name':name,'arguments':args or {}})


def result(r):
    assert not r['result']['isError'], r
    return json.loads(r['result']['content'][0]['text'])


def test_stdio_tools_without_mce(tmp_path):
    requests=[rpc('initialize'),rpc('tools/list'),tool('rea_bridge_status')]
    p=subprocess.run([sys.executable,str(ROOT/'src/server.py'), '--root',str(tmp_path)],
        input='\n'.join(map(json.dumps,requests))+'\n',capture_output=True,text=True,timeout=9)
    assert p.returncode==0,p.stderr
    data=[json.loads(s) for s in p.stdout.splitlines()]
    assert len(data)==3
    assert data[0]['result']['serverInfo']['name']=='rea-independent-engine'
    assert all('mce' not in item['name'].lower() for item in data[1]['result']['tools'])
    assert result(data[2])['upstream_repo']=='https://github.com/morluto/rea'


def test_source_metadata_hash_no_body(tmp_path):
    p=tmp_path/'sample.py'
    p.write_text('import os\nPASSWORD="confidential-text"\ndef go(): return 1\n')
    response=result(ReaBridge(tmp_path,ROOT).handle(tool('rea_source_inspect',{'file':'sample.py'})))
    assert response['sha256']==hashlib.sha256(p.read_bytes()).hexdigest()
    assert any(x['name']=='go' for x in response['definitions'])
    assert 'confidential-text' not in json.dumps(response)


@pytest.mark.parametrize('raw',['../x.py','/etc/passwd','.env','.ssh/id_rsa','data/../data/a.py'])
def test_blocks_secret_or_parent_path(tmp_path,raw):
    r=ReaBridge(tmp_path,ROOT).handle(tool('rea_source_inspect',{'file':raw}))
    assert r['result']['isError'] is True


def test_denies_symlink(tmp_path):
    outside=tmp_path.parent/'rea-outside-private.py'
    outside.write_text('PASSWORD="SECRET"')
    try:
        (tmp_path/'linked.py').symlink_to(outside)
    except OSError as exc:
        if getattr(exc, 'winerror', None) == 1314:
            pytest.skip('Windows host does not grant symlink creation; exercised on Linux CI')
        raise
    assert ReaBridge(tmp_path,ROOT).handle(tool('rea_source_inspect',{'file':'linked.py'}))['result']['isError']


def test_http_token_and_origin(tmp_path):
    token='t'*42
    srv=create_server(tmp_path,ROOT,'127.0.0.1',0,token)
    worker=threading.Thread(target=srv.serve_forever,daemon=True)
    worker.start()
    url='http://127.0.0.1:'+str(srv.server_address[1])+'/mcp'
    body=json.dumps(rpc('initialize')).encode()
    try:
        with pytest.raises(HTTPError) as missing:
            urlopen(Request(url,body,{'Content-Type':'application/json'}),timeout=3)
        assert missing.value.code==401
        with urlopen(Request(url,body,{'Content-Type':'application/json','Authorization':'Bearer '+token}),timeout=3) as res:
            assert json.loads(res.read())['result']['serverInfo']['name']=='rea-independent-engine'
        with pytest.raises(HTTPError) as other_origin:
            urlopen(Request(url,body,{'Content-Type':'application/json','Authorization':'Bearer '+token,'Origin':'https://evil.invalid'}),timeout=3)
        assert other_origin.value.code==403
    finally:
        srv.shutdown();srv.server_close();worker.join(timeout=3)


def test_no_public_bind(tmp_path):
    with pytest.raises(ValueError):create_server(tmp_path,ROOT,'0.0.0.0',8768,'x'*40)
    with pytest.raises(ValueError):create_server(tmp_path,ROOT,'127.0.0.1',8768,'short')


def test_web_local_ui_and_auth(tmp_path):
    from fastapi.testclient import TestClient
    from web_app import create_app, assert_safe_bind
    with TestClient(create_app(tmp_path,ROOT,'k'*40)) as c:
        r=c.get('/')
        assert r.status_code==200 and 'REA Independente' in r.text
        assert 'MCE' not in r.text
        assert c.post('/api/tool/rea_bridge_status',json={}).status_code==401
        ok=c.post('/api/tool/rea_bridge_status',json={},headers={'Authorization':'Bearer '+'k'*40})
        assert ok.status_code==200
        assert ok.json()['implementation']=='INDEPENDENT_REA_STATIC_ENGINE_NOT_UPSTREAM_REA'
    with pytest.raises(ValueError):assert_safe_bind('0.0.0.0')


def test_config_does_not_register_mce(tmp_path):
    import tomllib
    sys.path.insert(0,str(ROOT/'scripts'))
    from create_mcp_config import generate_config
    s=generate_config(ROOT,tmp_path,sys.executable)
    parsed=tomllib.loads(s)
    assert 'rea_internal' in parsed['mcp_servers']
    assert not any('mce' in k.lower() for k in parsed['mcp_servers'])
