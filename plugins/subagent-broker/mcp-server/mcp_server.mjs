#!/usr/bin/env node
import readline from 'node:readline';
import path from 'node:path';
import {StateStore} from './state_store.mjs';
import {CodexCliBackend} from './codex_cli_backend.mjs';
import {SubagentBroker} from './broker.mjs';
import {resolveConfiguredRepoRoot} from './worktree_manager.mjs';
import {validateSpawnArgs,validateStatusArgs,validateWaitArgs,validateResultArgs,validateFollowupArgs,validateListArgs,validateCancelArgs,validateCleanupArgs} from './protocol.mjs';

const TOOLS=[
 ['subagent_spawn','Spawn one independent Codex child.',false,false],['subagent_status','Read current child lifecycle state.',true,false],['subagent_wait','Wait until terminal state or timeout.',true,false],['subagent_result','Read terminal result metadata.',true,false],['subagent_followup','Resume a completed child session.',false,false],['subagent_list','List known children.',true,false],['subagent_cancel','Cancel a queued or running child.',false,true],['subagent_cleanup','Safely clean terminal child artifacts/worktree.',false,true]
];
function schema(name){
 const defs={
  subagent_spawn:{properties:{task:{type:'string'},role:{type:'string',enum:['implementer','reviewer','researcher','tester','security-reviewer']},workspace_mode:{type:'string',enum:['read_only','worktree_write']},base_ref:{type:['string','null']},timeout_seconds:{type:'integer',minimum:1,maximum:86400},priority:{type:'string',enum:['normal','high']}},required:['task','role','workspace_mode']},
  subagent_wait:{properties:{agent_id:{type:'string'},timeout_ms:{type:'integer',minimum:1000,maximum:600000}},required:['agent_id','timeout_ms']},
  subagent_followup:{properties:{agent_id:{type:'string'},message:{type:'string'}},required:['agent_id','message']},
  subagent_list:{properties:{state:{type:'string'}},required:[]},
  subagent_cleanup:{properties:{agent_id:{type:'string'},purge_metadata:{type:'boolean'}},required:['agent_id']},
 };
 return {type:'object',additionalProperties:false,...(defs[name]??{properties:{agent_id:{type:'string'}},required:['agent_id']})};
}
function response(id,result){process.stdout.write(JSON.stringify({jsonrpc:'2.0',id,result})+'\n');}
function errorResponse(id,code,message,data){process.stdout.write(JSON.stringify({jsonrpc:'2.0',id,error:{code,message,data}})+'\n');}
function toolResult(value,isError=false){return{content:[{type:'text',text:JSON.stringify(value)}],structuredContent:value,...(isError?{isError:true}:{})};}

const repoRoot=await resolveConfiguredRepoRoot(process.env);
const store=new StateStore(path.join(repoRoot,'.superpowers','subagents'));
const backend=new CodexCliBackend({codexPath:process.env.SUBAGENT_BROKER_CODEX_PATH||'codex',stateStore:store,parentEnv:process.env});
const broker=new SubagentBroker({repoRoot,stateStore:store,backend});await broker.start();
const validators={subagent_spawn:validateSpawnArgs,subagent_status:validateStatusArgs,subagent_wait:validateWaitArgs,subagent_result:validateResultArgs,subagent_followup:validateFollowupArgs,subagent_list:validateListArgs,subagent_cancel:validateCancelArgs,subagent_cleanup:validateCleanupArgs};
const handlers={subagent_spawn:a=>broker.spawn(a),subagent_status:a=>broker.status(a.agent_id),subagent_wait:a=>broker.wait(a.agent_id,a.timeout_ms),subagent_result:a=>broker.result(a.agent_id),subagent_followup:a=>broker.followup(a.agent_id,a.message),subagent_list:a=>broker.list(a),subagent_cancel:a=>broker.cancel(a.agent_id),subagent_cleanup:a=>broker.cleanup(a.agent_id,a)};

const rl=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
for await(const line of rl){if(!line.trim())continue;let req;try{req=JSON.parse(line);}catch{errorResponse(null,-32700,'Parse error');continue;}const{id,method,params={}}=req;try{
 if(method==='initialize'){response(id,{protocolVersion:params.protocolVersion||'2025-03-26',capabilities:{tools:{}},serverInfo:{name:'subagent-broker',version:'1.0.0'}});continue;}
 if(method==='ping'){response(id,{});continue;}
 if(method==='tools/list'){response(id,{tools:TOOLS.map(([name,description,readOnly,destructive])=>({name,description,inputSchema:schema(name),annotations:{readOnlyHint:readOnly,destructiveHint:destructive,idempotentHint:readOnly,openWorldHint:false}}))});continue;}
 if(method==='tools/call'){const name=params.name;if(!handlers[name]){response(id,toolResult({code:'UNKNOWN_TOOL',message:`unknown tool: ${name}`},true));continue;}try{const args=validators[name](params.arguments??{});response(id,toolResult(await handlers[name](args)));}catch(e){response(id,toolResult({code:e?.code||'BROKER_ERROR',message:String(e?.message??e),details:e?.details??null},true));}continue;}
 errorResponse(id,-32601,'Method not found');
 }catch(e){errorResponse(id,-32603,'Internal error',{message:String(e?.message??e)});}}

async function shutdown(){await broker.shutdown().catch(()=>{});process.exit(0);}process.on('SIGINT',shutdown);process.on('SIGTERM',shutdown);
