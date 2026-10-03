import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises'; import os from 'node:os'; import path from 'node:path';
import {StateStore} from '../mcp-server/state_store.mjs';
async function tmp(){return fs.mkdtemp(path.join(os.tmpdir(),'subagent-state-'));}
test('state store persists transitions and terminal results',async()=>{
 const root=await tmp(); try{const s=new StateStore(root); await s.create({agent_id:'sa_one',state:'QUEUED',transition_history:[],pid:null}); await s.writePrompt('sa_one','brief'); await s.update('sa_one',{},'SPAWNING'); await s.update('sa_one',{pid:123,process_identity:{pid:123,start_ticks:'7'}},'RUNNING'); const r=await s.update('sa_one',{exit_code:0},'COMPLETED'); await s.writeResult('sa_one',{agent_id:'sa_one',state:'COMPLETED'},'done'); assert.equal((await s.get('sa_one')).state,'COMPLETED'); assert.equal((await s.readResult('sa_one')).state,'COMPLETED'); assert.equal(await s.readPrompt('sa_one'),'brief'); assert.equal(r.transition_history.length,3);}finally{await fs.rm(root,{recursive:true,force:true});}
});
test('restart reconciliation refuses PID reuse',async()=>{
 const root=await tmp(); try{const s=new StateStore(root); await s.create({agent_id:'sa_two',state:'RUNNING',transition_history:[],pid:42,process_identity:{pid:42,start_ticks:'100'}}); const rs=await s.reconcileNonterminal(async()=>({pid:42,start_ticks:'999'})); assert.equal(rs.find(x=>x.agent_id==='sa_two').state,'ORPHANED');}finally{await fs.rm(root,{recursive:true,force:true});}
});
