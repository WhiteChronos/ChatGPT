import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';

const identity=/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;
const sha=/^[a-f0-9]{40}$/i;
const digest=/^[a-f0-9]{64}$/i;
const text=x=>typeof x==='string'&&x.trim().length>0;
const repoUrl=(url,repo)=>url===`https://github.com/${repo}`;
const sameCommit=(a,b)=>text(a)&&text(b)&&a.toLowerCase()===b.toLowerCase();
function validObservationDate(value){
 if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?Z$/.test(value))return false;
 const date=new Date(value);
 return Number.isFinite(date.getTime())&&date.toISOString().slice(0,19)===value.slice(0,19);
}
function pinned(url,repo,commit){
 if(typeof url!=='string')return false;
 try{
  const parsed=new URL(url);
  if(parsed.protocol!=='https:'||parsed.username||parsed.password||parsed.search||parsed.hash)return false;
  return (parsed.hostname==='raw.githubusercontent.com'&&parsed.pathname.startsWith(`/${repo}/${commit}/`))||(parsed.hostname==='github.com'&&parsed.pathname.startsWith(`/${repo}/blob/${commit}/`));
 }catch{return false;}
}

export function validateRegistry(data){
 const errors=[];
 if(!data||data.schema!=='windows-diagnostics-hub/1'||!Array.isArray(data.tools))return ['Invalid registry schema/tools'];
 if(data.tools.length!==10)errors.push('Expected exactly 10 tools');
 const ids=new Set(),repos=new Set(),forks=new Set();
 for(const [i,t]of data.tools.entries()){
  if(!t||typeof t!=='object'){errors.push(`tool ${i}: invalid record`);continue;}
  const prefix=`tool ${i} (${t.id??'missing'})`;
  if(!text(t.id)||!/^[a-z0-9][a-z0-9-]*$/.test(t.id))errors.push(`${prefix}: invalid id`);
  if(ids.has(t.id))errors.push(`${prefix}: duplicate id`);ids.add(t.id);
  const u=t.upstream,f=t.fork;
  if(!u||!f){errors.push(`${prefix}: missing upstream/fork`);continue;}
  if(!identity.test(u.repository??''))errors.push(`${prefix}: invalid upstream identity`);
  const repoKey=text(u.repository)?u.repository.toLowerCase():null;
  if(repos.has(repoKey))errors.push(`${prefix}: duplicate repository`);repos.add(repoKey);
  if(!repoUrl(u.url,u.repository))errors.push(`${prefix}: upstream URL mismatch`);
  if(!sha.test(u.reviewedSha??''))errors.push(`${prefix}: invalid reviewed SHA`);
  if(!text(f.repository)||!identity.test(f.repository)||f.repository.split('/')[0]!=='WhiteChronos'||!repoUrl(f.url,f.repository))errors.push(`${prefix}: invalid fork destination`);
  const forkKey=text(f.repository)?f.repository.toLowerCase():null;
  if(forks.has(forkKey))errors.push(`${prefix}: duplicate fork`);forks.add(forkKey);
  if(f.parent!==u.repository)errors.push(`${prefix}: fork parent mismatch`);
  if(!sha.test(f.headSha??''))errors.push(`${prefix}: invalid fork head SHA`);
  if(!validObservationDate(f.verifiedAt))errors.push(`${prefix}: invalid fork observation date`);
  if(!Array.isArray(u.sources)||u.sources.length<2)errors.push(`${prefix}: missing source evidence`);
  else for(const s of u.sources){if(!s||!text(s.path)||!digest.test(s.sha256??'')||!pinned(s.url,u.repository,u.reviewedSha))errors.push(`${prefix}: source must be SHA-pinned and hashed`);}
  if(!text(t.license?.expression)||['UNKNOWN','NOASSERTION'].includes(t.license?.expression)||!pinned(t.license?.evidenceUrl,u.repository,u.reviewedSha)||!(Array.isArray(u.sources)&&u.sources.some(s=>s?.url===t.license?.evidenceUrl&&digest.test(s?.sha256??''))))errors.push(`${prefix}: missing licence evidence in hashed sources`);
  for(const field of ['role','risk','benchmark','rollback'])if(!text(t[field]))errors.push(`${prefix}: missing ${field}`);
  if(t.adoption!=='REFERENCE_ONLY'||t.states?.execution!=='NOT_RUN'||t.states?.installation!=='NOT_PERFORMED_BY_HUB'||t.states?.review!=='DOCUMENTARY_REVIEWED'||t.states?.fork!=='VERIFIED')errors.push(`${prefix}: invalid adoption/execution state`);
  if(!Array.isArray(t.skills)||t.skills.some(s=>!s||!text(s.path)||!s.path.endsWith('SKILL.md')||!pinned(s.url,u.repository,u.reviewedSha)))errors.push(`${prefix}: invalid skill reference`);
 }
 return errors;
}

export function planFor(data,id){
 const t=data.tools.find(t=>t.id===id||t.upstream.repository===id);if(!t)return null;
 return {id:t.id,role:t.role,upstream:t.upstream,fork:t.fork,license:t.license,
  forkDiffersFromReviewedCommit:!sameCommit(t.fork.headSha,t.upstream.reviewedSha),
  risk:t.risk,benchmark:t.benchmark,rollback:t.rollback,skills:t.skills,
  nextSteps:['Conferir tarefa, ferramenta já disponível e revisão do commit pretendido.','Revisar licença do binário, assinatura, dependências e sobrecarga.','Propor escopo, medição equivalente e rollback para aprovação aplicável.'],
  installationApproved:false,hostChanged:false,upstreamExecuted:false};
}

export async function runCLI(args){
 const [command,id,...extra]=args;
 if(!['catalog','validate','plan'].includes(command)||extra.length||((command==='plan')!==Boolean(id))){console.error('Use: hub.mjs catalog | validate | plan <id>. Execução e instalação não são suportadas.');return 2;}
 const data=JSON.parse(await fs.readFile(new URL('../registry.json',import.meta.url),'utf8'));
 const errors=validateRegistry(data);
 if(errors.length){console.error(JSON.stringify({status:'FAIL',errors},null,2));return 1;}
 if(command==='validate')console.log(JSON.stringify({status:'PASS',tools:data.tools.length,scope:'LOCAL_STRUCTURAL_VALIDATION_NOT_LIVE_FORK_OR_HOST_TEST',networkUsed:false,hostChanged:false},null,2));
 if(command==='catalog')console.log(JSON.stringify(data.tools.map(t=>({id:t.id,role:t.role,upstream:t.upstream.repository,fork:t.fork.url,license:t.license.expression,states:t.states,forkDiffersFromReviewedCommit:!sameCommit(t.fork.headSha,t.upstream.reviewedSha)})),null,2));
 if(command==='plan'){const result=planFor(data,id);if(!result){console.error('Ferramenta não encontrada.');return 2;}console.log(JSON.stringify(result,null,2));}
 return 0;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 try{process.exitCode=await runCLI(process.argv.slice(2));}catch(e){console.error(`Falha ao ler catálogo: ${e.message}`);process.exitCode=1;}
}
