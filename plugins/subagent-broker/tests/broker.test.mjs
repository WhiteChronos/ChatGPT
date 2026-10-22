import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises'; import os from 'node:os'; import path from 'node:path';
import {StateStore} from '../mcp-server/state_store.mjs'; import {SubagentBroker} from '../mcp-server/broker.mjs';
import {removeTree} from './test_helpers.mjs';
function deferred(){let resolve;const completion=new Promise(r=>resolve=r);return{completion,resolve};}
function fixture(){const runs=[];const backend={async probe(){return{resume:true};},async spawn(spec){const d=deferred();const h={pid:100+runs.length,process_identity:{pid:100+runs.length,start_ticks:String(runs.length+1)},session_id:'s'+runs.length,completion:d.completion,...spec};runs.push({h,d});return h;},async followup(h){const d=deferred();const n={...h,pid:h.pid+100,completion:d.completion};runs.push({h:n,d});return n;},async cancel(){}};const ws={async resolveBase(){return'a'.repeat(40);},async createWorkspace({agentId,mode,baseSha}){return{repo_root:'/repo',path:'/tmp/'+agentId,mode,base_sha:baseSha,branch:mode==='worktree_write'?'subagent/'+agentId:null};},async statusWorkspace(){return{dirty:false,porcelain:'',commits:[],diff_stat:''};},async cleanupWorkspace(){}};return{backend,ws,runs};}

test('cancel of completed resumed child is idempotent and preserves result',async()=>{
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'subagent-broker-terminal-'));
  const store=new StateStore(root);
  const {backend,ws,runs}=fixture();
  let backendCancels=0;
  backend.cancel=async()=>{backendCancels++;throw new Error('must not cancel a completed process');};
  const broker=new SubagentBroker({repoRoot:'/repo',stateStore:store,backend,workspaceManager:ws,roleLoader:async()=>'role',idFactory:()=> 'sa_terminal'});
  try {
    await broker.spawn({task:'smoke',role:'researcher',workspace_mode:'read_only'});
    runs[0].d.resolve({exit_code:0,session_id:'same-session',final_text:'first'});
    assert.equal((await broker.wait('sa_terminal',1000)).state,'COMPLETED');
    await broker.followup('sa_terminal','continue');
    runs[1].d.resolve({exit_code:0,session_id:'same-session',final_text:'second'});
    assert.equal((await broker.wait('sa_terminal',1000)).state,'COMPLETED');
    const before=await broker.result('sa_terminal');
    for(let i=0;i<2;i++)assert.equal((await broker.cancel('sa_terminal')).state,'COMPLETED');
    assert.equal(backendCancels,0);
    assert.deepEqual(await broker.result('sa_terminal'),before);
  } finally {await broker.shutdown();await removeTree(root);}
});
test('broker default role loader resolves bundled roles on the host platform',async()=>{const root=await fs.mkdtemp(path.join(os.tmpdir(),'subagent-broker-role-'));try{const store=new StateStore(root);const{backend,ws,runs}=fixture();const broker=new SubagentBroker({repoRoot:root,stateStore:store,backend,workspaceManager:ws,idFactory:()=> 'sa_role'});const spawned=await broker.spawn({task:'inspect runtime',role:'researcher',workspace_mode:'read_only'});assert.equal(spawned.state,'RUNNING');assert.match(runs[0].h.prompt,/Task:\ninspect runtime$/);await broker.shutdown();}finally{await removeTree(root);}});
test('broker runs three and queues fourth',async()=>{const root=await fs.mkdtemp(path.join(os.tmpdir(),'subagent-broker-'));try{const store=new StateStore(root);const{backend,ws,runs}=fixture();let n=0;const broker=new SubagentBroker({repoRoot:'/repo',stateStore:store,backend,workspaceManager:ws,roleLoader:async()=>'role',idFactory:()=> 'sa_'+(++n)});const a=[];for(let i=0;i<4;i++)a.push(await broker.spawn({task:'x',role:'reviewer',workspace_mode:'read_only'}));assert.deepEqual(a.map(x=>x.state),['RUNNING','RUNNING','RUNNING','QUEUED']);runs[0].d.resolve({exit_code:0,session_id:'s0',final_text:'ok'});assert.equal((await broker.wait('sa_1',1000)).state,'COMPLETED');const deadline=Date.now()+1000;let state;do{state=(await broker.status('sa_4')).state;if(state==='RUNNING')break;await new Promise(r=>setTimeout(r,20));}while(Date.now()<deadline);assert.equal(state,'RUNNING');await broker.shutdown();}finally{await removeTree(root);}});

test('broker finalizes successful dirty write workspaces with a parent-side commit',async()=>{const root=await fs.mkdtemp(path.join(os.tmpdir(),'subagent-broker-commit-'));try{const store=new StateStore(root);const{backend,ws,runs}=fixture();let committed=0;ws.statusWorkspace=async()=>committed?{dirty:false,porcelain:'',commits:['b'.repeat(40)],diff_stat:' result.txt | 1 +'}:{dirty:true,porcelain:'?? result.txt',commits:[],diff_stat:''};ws.commitWorkspaceChanges=async(_workspace,{message})=>{assert.match(message,/sa_commit/);committed+=1;return ws.statusWorkspace();};const broker=new SubagentBroker({repoRoot:'/repo',stateStore:store,backend,workspaceManager:ws,roleLoader:async()=>'role',idFactory:()=> 'sa_commit'});await broker.spawn({task:'write result',role:'implementer',workspace_mode:'worktree_write'});runs[0].d.resolve({exit_code:0,session_id:'s0',final_text:'done'});assert.equal((await broker.wait('sa_commit',1000)).state,'COMPLETED');const result=await broker.result('sa_commit');assert.equal(committed,1);assert.deepEqual(result.commits,['b'.repeat(40)]);await broker.shutdown();}finally{await removeTree(root);}});
