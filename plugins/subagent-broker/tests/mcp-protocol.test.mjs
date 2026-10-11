import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process'; import path from 'node:path'; import {fileURLToPath} from 'node:url';

const plugin=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const repo=path.resolve(plugin,'../..');

function waitForExit(child,timeoutMs=3000){
  return Promise.race([
    new Promise(resolve=>child.on('close',code=>resolve(code))),
    new Promise((_,reject)=>setTimeout(()=>reject(new Error('child exit timeout')),timeoutMs)),
  ]);
}

test('MCP initializes silently and exposes exactly eight tools with explicit repository binding',async()=>{
  const child=spawn(process.execPath,['mcp-server/mcp_server.mjs'],{
    cwd:plugin,
    stdio:['pipe','pipe','pipe'],
    env:{
      ...process.env,
      SUBAGENT_BROKER_REPO_ROOT:repo,
      SUBAGENT_BROKER_CODEX_PATH:path.join(plugin,'tests','fake-codex.mjs')
    }
  });
  let stdout='';
  child.stdout.setEncoding('utf8');
  child.stdout.on('data',d=>stdout+=d);
  child.stdin.write(JSON.stringify({jsonrpc:'2.0',id:1,method:'initialize',params:{protocolVersion:'2025-03-26'}})+'\n');
  child.stdin.write(JSON.stringify({jsonrpc:'2.0',method:'notifications/initialized',params:{}})+'\n');
  child.stdin.write(JSON.stringify({jsonrpc:'2.0',id:2,method:'tools/list',params:{}})+'\n');
  const responses=()=>stdout.split('\n').slice(0,-1).filter(Boolean).map(JSON.parse);
  try{
    const deadline=Date.now()+3000;
    while(!responses().some(x=>x.id===2)&&Date.now()<deadline)await new Promise(r=>setTimeout(r,20));
    assert.ok(responses().some(x=>x.id===2),'tools/list response missing');
  }finally{
    const exited=waitForExit(child);
    child.kill('SIGTERM');
    await exited;
  }
  const messages=responses();
  assert.deepEqual(messages.map(x=>x.id),[1,2],'notifications/initialized must not produce a response');
  assert.ok(messages.every(x=>!x.error),'handshake must not produce JSON-RPC errors');
  assert.deepEqual(messages[0],{jsonrpc:'2.0',id:1,result:{protocolVersion:'2025-03-26',capabilities:{tools:{}},serverInfo:{name:'subagent-broker',version:'1.0.0'}}});
  const resp=messages.find(x=>x.id===2);
  assert.deepEqual(resp.result.tools.map(t=>t.name),['subagent_spawn','subagent_status','subagent_wait','subagent_result','subagent_followup','subagent_list','subagent_cancel','subagent_cleanup']);
});

test('MCP fails closed when repository binding is missing',async()=>{
  const env={...process.env,SUBAGENT_BROKER_CODEX_PATH:path.join(plugin,'tests','fake-codex.mjs')};
  delete env.SUBAGENT_BROKER_REPO_ROOT;
  const child=spawn(process.execPath,['mcp-server/mcp_server.mjs'],{cwd:plugin,stdio:['ignore','pipe','pipe'],env});
  let stderr='';
  child.stderr.setEncoding('utf8');
  child.stderr.on('data',d=>stderr+=d);
  const code=await waitForExit(child);
  assert.notEqual(code,0);
  assert.match(stderr,/SUBAGENT_BROKER_REPO_ROOT.*required/i);
});
