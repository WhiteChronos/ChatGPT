import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {validateRegistry,planFor} from '../scripts/hub.mjs';
const registry=JSON.parse(await fs.readFile(new URL('../registry.json',import.meta.url),'utf8'));
const cli=fileURLToPath(new URL('../scripts/hub.mjs',import.meta.url));
test('catalogue contains ten verified fork relations and separate execution states',()=>{
 assert.deepEqual(validateRegistry(registry),[]);
 assert.equal(registry.tools.length,10);
 assert.ok(registry.tools.every(t=>t.states.execution==='NOT_RUN'));
});
test('duplicate identities are rejected',()=>{
 const bad=structuredClone(registry);bad.tools[1]=structuredClone(bad.tools[0]);
 assert.ok(validateRegistry(bad).some(e=>e.includes('duplicate')));
});
test('a mismatched parent cannot be labelled verified',()=>{
 const bad=structuredClone(registry);bad.tools[0].fork.parent='other/repository';
 assert.ok(validateRegistry(bad).some(e=>e.includes('parent')));
});
test('non-GitHub URLs and unpinned source files are rejected',()=>{
 const bad=structuredClone(registry);bad.tools[0].upstream.url='https://example.com/repository';
 bad.tools[0].upstream.sources[0].url='https://raw.githubusercontent.com/microsoft/perfview/main/README.md';
 assert.ok(validateRegistry(bad).length>=2);
});
test('source URL cannot escape the reviewed commit using dot segments',()=>{
 const bad=structuredClone(registry);const u=bad.tools[0].upstream;
 u.sources[0].url=`https://raw.githubusercontent.com/${u.repository}/${u.reviewedSha}/../main/README.md`;
 assert.ok(validateRegistry(bad).some(e=>e.includes('SHA-pinned')));
});
test('malformed identity types and skill paths return errors',()=>{
 const bad=structuredClone(registry);bad.tools[0].upstream.repository=42;bad.tools[0].fork.repository=42;bad.tools[0].skills=[{path:42}];
 assert.ok(validateRegistry(bad).length);
});
test('missing licence evidence, invalid SHA and executable adoption state are rejected',()=>{
 const bad=structuredClone(registry);bad.tools[0].license.evidenceUrl='';bad.tools[0].fork.headSha='main';bad.tools[0].states.execution='RUNNING';
 assert.ok(validateRegistry(bad).length>=3);
});
test('malformed JSON shapes return validation errors, not success',()=>{
 assert.ok(validateRegistry(null).length);assert.ok(validateRegistry({tools:[null]}).length);
 const bad=structuredClone(registry);bad.tools[0].upstream=null;assert.ok(validateRegistry(bad).length);
});
test('plan reports approval and drift without executable commands',()=>{
 const p=planFor(registry,registry.tools[0].id);
 assert.equal(p.hostChanged,false);assert.equal(p.upstreamExecuted,false);
 assert.equal(p.installationApproved,false);assert.ok(p.rollback);assert.ok(p.benchmark);
 assert.equal(planFor(registry,'not-a-tool'),null);
});
test('catalog, validate and plan work as real offline CLI processes',()=>{
 for(const args of [['catalog'],['validate'],['plan',registry.tools[0].id]]){
  const r=spawnSync(process.execPath,[cli,...args],{encoding:'utf8'});
  assert.equal(r.status,0,r.stderr);assert.ok(JSON.parse(r.stdout));
 }
});
test('CLI rejects execution and extra arguments',()=>{
 for(const args of [['run','perfview'],['install','psutil'],['validate','extra'],['plan','unknown']]){
  const r=spawnSync(process.execPath,[cli,...args],{encoding:'utf8'});assert.equal(r.status,2);
 }
});
test('skill entry point and linked system documentation exist in checkout',async()=>{
 const skill=await fs.readFile(new URL('../../../.agents/skills/windows-diagnostics-hub/SKILL.md',import.meta.url),'utf8');
 assert.match(skill,/name: windows-diagnostics-hub/);
 assert.match(skill,/description:/);
 const docs=await fs.readFile(new URL('../README.md',import.meta.url),'utf8');
 assert.match(docs,/Não é um otimizador/);
});
