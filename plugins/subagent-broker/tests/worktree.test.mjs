import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises'; import os from 'node:os'; import path from 'node:path'; import {spawn} from 'node:child_process';
import * as worktrees from '../mcp-server/worktree_manager.mjs';

const {discoverRepoRoot,resolveBase,createWorkspace,statusWorkspace,cleanupWorkspace}=worktrees;

function run(cmd,args,cwd){return new Promise((res,rej)=>{const p=spawn(cmd,args,{cwd,shell:false});let e='';p.stderr.on('data',d=>e+=d);p.on('close',c=>c?rej(new Error(e)):res());});}
async function repo(){const root=await fs.mkdtemp(path.join(os.tmpdir(),'subagent-git-'));await run('git',['init','-q'],root);await run('git',['config','user.email','test@example.com'],root);await run('git',['config','user.name','test'],root);await fs.mkdir(path.join(root,'plugins','subagent-broker'),{recursive:true});await fs.writeFile(path.join(root,'a.txt'),'a');await run('git',['add','.'],root);await run('git',['commit','-qm','init'],root);return root;}

test('read-only snapshot is detached',async()=>{const root=await repo();try{assert.equal(await discoverRepoRoot(path.join(root,'plugins','subagent-broker')),root);const base=await resolveBase(root,'HEAD');const ws=await createWorkspace({repoRoot:root,agentId:'sa_read',baseSha:base,mode:'read_only'});assert.equal(ws.branch,null);assert.equal((await statusWorkspace(ws)).dirty,false);await cleanupWorkspace(ws);}finally{await fs.rm(root,{recursive:true,force:true});}});
test('write workspace is isolated and dirty cleanup refuses',async()=>{const root=await repo();try{const base=await resolveBase(root,'HEAD');const ws=await createWorkspace({repoRoot:root,agentId:'sa_write',baseSha:base,mode:'worktree_write'});assert.equal(ws.branch,'subagent/sa_write');await fs.writeFile(path.join(ws.path,'dirty.txt'),'x');await assert.rejects(()=>cleanupWorkspace(ws,{purgeBranch:true}),/dirty worktree/i);}finally{await fs.rm(root,{recursive:true,force:true});}});

test('broker repository binding requires an explicit absolute git root',async()=>{
  assert.equal(typeof worktrees.resolveConfiguredRepoRoot,'function','security contract requires resolveConfiguredRepoRoot');
  const root=await repo();
  const nonRepo=await fs.mkdtemp(path.join(os.tmpdir(),'subagent-not-git-'));
  try{
    assert.equal(await worktrees.resolveConfiguredRepoRoot({SUBAGENT_BROKER_REPO_ROOT:root}),root);
    await assert.rejects(()=>worktrees.resolveConfiguredRepoRoot({}),/SUBAGENT_BROKER_REPO_ROOT.*required/i);
    await assert.rejects(()=>worktrees.resolveConfiguredRepoRoot({SUBAGENT_BROKER_REPO_ROOT:'relative/path'}),/absolute/i);
    await assert.rejects(()=>worktrees.resolveConfiguredRepoRoot({SUBAGENT_BROKER_REPO_ROOT:nonRepo}),/git repository/i);
  }finally{
    await fs.rm(root,{recursive:true,force:true});
    await fs.rm(nonRepo,{recursive:true,force:true});
  }
});

test('cleanup refuses tampered branch metadata before removing workspace',async()=>{
  const root=await repo();
  try{
    const base=await resolveBase(root,'HEAD');
    const ws=await createWorkspace({repoRoot:root,agentId:'sa_owned',baseSha:base,mode:'worktree_write'});
    const tampered={...ws,branch:'main'};
    await assert.rejects(()=>cleanupWorkspace(tampered,{purgeBranch:true}),/branch.*identity|branch.*mismatch|workspace.*ownership/i);
    const stat=await fs.stat(ws.path);
    assert.equal(stat.isDirectory(),true);
    await cleanupWorkspace(ws,{purgeBranch:true});
  }finally{
    await fs.rm(root,{recursive:true,force:true});
  }
});


test('cleanup refuses workspace metadata that targets another agent worktree',async()=>{
  const root=await repo();
  try{
    const base=await resolveBase(root,'HEAD');
    const a={...(await createWorkspace({repoRoot:root,agentId:'sa_agent_a',baseSha:base,mode:'worktree_write'})),agent_id:'sa_agent_a'};
    const b={...(await createWorkspace({repoRoot:root,agentId:'sa_agent_b',baseSha:base,mode:'worktree_write'})),agent_id:'sa_agent_b'};
    const forged={...a,path:b.path,branch:b.branch};
    await assert.rejects(()=>cleanupWorkspace(forged,{purgeBranch:true}),/agent.*identity|workspace.*ownership|worktree.*identity/i);
    const stat=await fs.stat(b.path);
    assert.equal(stat.isDirectory(),true);
  }finally{
    await fs.rm(root,{recursive:true,force:true});
  }
});


test('repository binding ignores inherited Git repository-selection variables',async()=>{
  const realRepo=await repo();
  const fakeRoot=await fs.mkdtemp(path.join(os.tmpdir(),'subagent-fake-root-'));
  const previous={GIT_DIR:process.env.GIT_DIR,GIT_WORK_TREE:process.env.GIT_WORK_TREE};
  try{
    process.env.GIT_DIR=path.join(realRepo,'.git');
    process.env.GIT_WORK_TREE=fakeRoot;
    await assert.rejects(
      ()=>worktrees.resolveConfiguredRepoRoot({SUBAGENT_BROKER_REPO_ROOT:fakeRoot}),
      /git repository/i
    );
  }finally{
    if(previous.GIT_DIR===undefined) delete process.env.GIT_DIR; else process.env.GIT_DIR=previous.GIT_DIR;
    if(previous.GIT_WORK_TREE===undefined) delete process.env.GIT_WORK_TREE; else process.env.GIT_WORK_TREE=previous.GIT_WORK_TREE;
    await fs.rm(realRepo,{recursive:true,force:true});
    await fs.rm(fakeRoot,{recursive:true,force:true});
  }
});
