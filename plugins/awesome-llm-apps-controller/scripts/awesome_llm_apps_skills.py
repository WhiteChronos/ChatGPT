from __future__ import annotations
from pathlib import Path
import json, shutil, tempfile

KNOWN_RISKS={
 'advisor-orchestrator-worker':{'execution_class':'CREDENTIALLED','network_required':True,'credentials_required':True,'broad_filesystem_access':False,'explicit_user_request_required':True},
 'commit-archaeologist':{'execution_class':'LOCAL_READ_ONLY','network_required':False,'credentials_required':False,'broad_filesystem_access':False,'explicit_user_request_required':False},
 'dependency-doctor':{'execution_class':'LOCAL_READ_ONLY','network_required':False,'credentials_required':False,'broad_filesystem_access':False,'explicit_user_request_required':False},
 'first-reader':{'execution_class':'REFERENCE_ONLY','network_required':False,'credentials_required':False,'broad_filesystem_access':False,'explicit_user_request_required':False},
 'project-graveyard':{'execution_class':'LOCAL_READ_ONLY','network_required':False,'credentials_required':False,'broad_filesystem_access':True,'explicit_user_request_required':True},
 'scope-creep-detector':{'execution_class':'LOCAL_READ_ONLY','network_required':False,'credentials_required':False,'broad_filesystem_access':False,'explicit_user_request_required':False},
 'thinking-out-loud':{'execution_class':'REFERENCE_ONLY','network_required':False,'credentials_required':False,'broad_filesystem_access':False,'explicit_user_request_required':False},
}

SAFE_UNKNOWN_RISK={
 'execution_class':'REFERENCE_ONLY',
 'network_required':False,
 'credentials_required':False,
 'broad_filesystem_access':False,
 'explicit_user_request_required':True,
}

def risk_for_skill(name:str):
    # New upstream Skills remain discoverable but cannot inherit permissive
    # execution assumptions before WhiteChronos reviews their behavior.
    return dict(KNOWN_RISKS.get(name, SAFE_UNKNOWN_RISK))

def load_canonical_skills(root:Path):
    root=Path(root); reg=json.loads((root/'agent_skills'/'registry.json').read_text())
    skills=[]; inc=[]
    for item in reg.get('skills',[]):
        name=item.get('name'); path=item.get('path'); license_=item.get('license')
        if not license_: inc.append({'name':name,'kind':'license_metadata','detail':'empty_or_missing'})
        skill=root/path/'SKILL.md' if path else None
        if not path or not skill.exists(): inc.append({'name':name,'kind':'missing_skill_md'}); continue
        skills.append({**item,'risk':risk_for_skill(name)})
    skills.sort(key=lambda x:x['name']); inc.sort(key=lambda x:(str(x.get('name')),x['kind']))
    return {'version':reg.get('version',1),'skills':skills,'inconsistencies':inc}

def project_skills(root:Path,dest:Path,previous_manifest,matt_manifest):
    root=Path(root); dest=Path(dest); dest.mkdir(parents=True,exist_ok=True)
    loaded=load_canonical_skills(root)
    prev_names={x['name'] if isinstance(x,dict) else x for x in (previous_manifest or {}).get('managed_skills',[])}
    matt_names={x['name'] if isinstance(x,dict) else x for x in (matt_manifest or {}).get('skills',(matt_manifest or {}).get('managed_skills',[]))}
    desired={x['name'] for x in loaded['skills']}
    for item in loaded['skills']:
        name=item['name']; target=dest/name
        if name in matt_names: raise RuntimeError(f'collision with Matt-managed skill: {name}')
        if target.exists() and name not in prev_names: raise RuntimeError(f'collision with unmanaged skill: {name}')
    for stale in sorted(prev_names-desired):
        p=dest/stale
        if p.exists(): shutil.rmtree(p)
    managed=[]
    for item in loaded['skills']:
        name=item['name']; source=root/item['path']; target=dest/name
        tmp=Path(tempfile.mkdtemp(prefix=f'.{name}.',dir=dest))
        shutil.rmtree(tmp); shutil.copytree(source,tmp,symlinks=True)
        if target.exists(): shutil.rmtree(target)
        tmp.rename(target)
        managed.append({'name':name,'upstream_path':item['path'],**item['risk']})
    return {'source':'Shubhamsaboo/awesome-llm-apps','managed_skills':managed,'inconsistencies':loaded['inconsistencies']}
