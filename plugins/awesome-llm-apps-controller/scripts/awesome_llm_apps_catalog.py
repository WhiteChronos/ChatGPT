from __future__ import annotations
from pathlib import Path
from collections import Counter
import hashlib, json, re, subprocess

MANDATORY_ROOTS = {
    'starter_ai_agents','advanced_ai_agents','always_on_agents','voice_ai_agents',
    'mcp_ai_agents','generative_ui_agents','rag_tutorials','advanced_llm_apps',
    'ai_agent_framework_crash_course','agent_skills'
}
MANIFEST_NAMES={'requirements.txt','pyproject.toml','package.json','environment.yml','Pipfile'}
ENV_NAMES={'.env.example','.env.sample','env.example','example.env'}
DOCKER_NAMES={'Dockerfile','docker-compose.yml','docker-compose.yaml'}
CODE_EXT={'.py','.js','.ts','.tsx','.jsx','.sh','.mjs','.cjs'}
HIGH_STAKES=('medical','health','mental','therapy','insurance','legal','finance','financial','investment','trading','fraud')



def snapshot_statistics(root:Path)->dict:
    root=Path(root)
    proc=subprocess.run(
        ['git','ls-tree','-r','-t','HEAD'], cwd=root, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    rows=[line for line in proc.stdout.splitlines() if line.strip()]
    tree_entries=len(rows)
    blobs=[]
    for line in rows:
        meta, _, rel=line.partition('\t')
        parts=meta.split()
        if len(parts)>=2 and parts[1]=='blob':
            blobs.append(rel)
    registry=root/'agent_skills'/'registry.json'
    canonical=0
    if registry.exists():
        try:
            canonical=len(json.loads(registry.read_text()).get('skills',[]))
        except (OSError,json.JSONDecodeError):
            canonical=0
    def is_name(path,name): return Path(path).name.lower()==name.lower()
    return {
        'tree_entries':tree_entries,
        'blobs':len(blobs),
        'skill_md':sum(is_name(x,'SKILL.md') for x in blobs),
        'canonical_skills':canonical,
        'readmes':sum(is_name(x,'README.md') for x in blobs),
        'dependency_manifests':sum(Path(x).name in MANIFEST_NAMES for x in blobs),
        'env_examples':sum(Path(x).name in ENV_NAMES for x in blobs),
        'dockerfiles':sum(is_name(x,'Dockerfile') for x in blobs),
        'compose_files':sum(Path(x).name.lower() in {'docker-compose.yml','docker-compose.yaml'} for x in blobs),
        'mcp_related':sum(('mcp' in x.lower()) and Path(x).suffix.lower() in {'.json','.yaml','.yml','.py','.ts','.js','.md'} for x in blobs),
        'code_files':sum(Path(x).suffix.lower() in CODE_EXT for x in blobs),
    }

def _slug(s:str)->str:
    s=s.strip().lower().replace('_','-').replace('/','-')
    s=re.sub(r'[^a-z0-9-]+','-',s)
    return re.sub(r'-+','-',s).strip('-')

def normalize_id(source_type:str,key:str)->str:
    prefix=_slug(source_type)
    if source_type=='external_reference':
        digest=hashlib.sha256(key.encode()).hexdigest()[:12]
        return f'{prefix}:{_slug(key)[:80]}-{digest}'
    return f'{prefix}:{_slug(key)}'

def classify_execution(entry:dict)->dict:
    text=' '.join(str(entry.get(k,'')) for k in ('title','upstream_path','subtype')).lower()
    self_mod=bool(entry.get('self_modifying')) or any(x in text for x in ('self-improv','self_evolv','self-evolv'))
    background=bool(entry.get('background_capable')) or any(x in text for x in ('always_on','always-on','scheduler','watcher','release_radar'))
    mcp=bool(entry.get('mcp_related_paths')) or 'mcp' in text
    creds=bool(entry.get('credentials_required')) or bool(entry.get('env_example_paths')) or any('.env' in str(x) for x in entry.get('manifest_paths',[]))
    network=bool(entry.get('network_required')) or creds or mcp or entry.get('source_type')=='external_reference'
    mut=bool(entry.get('local_mutating'))
    high=bool(entry.get('high_stakes_domain')) or any(k in text for k in HIGH_STAKES)
    if self_mod: cls='SELF_MODIFYING'
    elif background: cls='BACKGROUND_AUTONOMOUS'
    elif mcp: cls='MCP_OR_CONNECTOR'
    elif creds: cls='CREDENTIALLED'
    elif network: cls='NETWORKED'
    elif mut: cls='LOCAL_MUTATING'
    elif entry.get('source_type')=='external_reference': cls='REFERENCE_ONLY'
    elif entry.get('category') in ('documentation','reference'): cls='REFERENCE_ONLY'
    else: cls='LOCAL_READ_ONLY'
    return {
        'network_required':network,'credentials_required':creds,
        'background_capable':background,'self_modifying':self_mod,
        'high_stakes_domain':high,'execution_class':cls,
    }

def _title_from_readme(path:Path)->str:
    try:
        for line in path.read_text(errors='ignore').splitlines():
            if line.startswith('# '): return line[2:].strip()
    except OSError: pass
    return path.parent.name.replace('_',' ').replace('-',' ').title()

def _nearest_license(root:Path, d:Path):
    cur=d
    while True:
        for child in sorted(cur.iterdir()) if cur.exists() else []:
            if child.is_file() and (child.name=='LICENSE' or child.name.startswith('LICENSE.') or child.name=='NOTICE' or child.name.startswith('NOTICE.')):
                return child.relative_to(root).as_posix()
        if cur==root: break
        if root not in cur.parents: break
        cur=cur.parent
    return 'LICENSE' if (root/'LICENSE').exists() else None

def _qualifying_dirs(root:Path):
    result=[]
    for d in [p for p in root.rglob('*') if p.is_dir()]:
        rel=d.relative_to(root)
        if not rel.parts: continue
        if any(part in {'.git','.github','node_modules','.venv','venv','__pycache__','.next','dist','build'} for part in rel.parts): continue
        names={p.name for p in d.iterdir() if p.is_file()}
        has_readme='README.md' in names
        has_manifest=bool(names & MANIFEST_NAMES)
        has_docker=bool(names & DOCKER_NAMES)
        has_skill='SKILL.md' in names
        has_code=any(p.is_file() and p.suffix.lower() in CODE_EXT for p in d.iterdir())
        if has_readme or has_manifest or has_docker or has_skill or has_code:
            top=rel.parts[0]
            if top in MANDATORY_ROOTS or top not in {'docs','plugins','registry','vendor'}:
                result.append(d)
    return sorted(result,key=lambda p:p.relative_to(root).as_posix())

def _attach_files(root:Path,d:Path):
    rel=d.relative_to(root).as_posix()
    files=[p for p in d.iterdir() if p.is_file()]
    def rp(p): return p.relative_to(root).as_posix()
    manifests=[rp(p) for p in files if p.name in MANIFEST_NAMES]
    envs=[rp(p) for p in files if p.name in ENV_NAMES]
    docker=[rp(p) for p in files if p.name in DOCKER_NAMES]
    skills=[rp(p) for p in files if p.name=='SKILL.md']
    mcp=[rp(p) for p in files if 'mcp' in p.name.lower() or 'mcp' in rel.lower()]
    langs=sorted({p.suffix.lstrip('.').lower() for p in files if p.suffix.lower() in CODE_EXT})
    return manifests,envs,docker,skills,mcp,langs

def extract_external_references(readme_text:str,commit:str):
    entries=[]; heading=''
    allowed_heading=re.compile(r'(agent|app|rag|mcp|voice|framework|generative|multi-agent|browser)',re.I)
    deny=re.compile(r'(sponsor|translation|thanks|star|unwind|badge)',re.I)
    link_re=re.compile(r'^\s*[*-]\s+\[([^\]]+)\]\((https?://[^)]+)\)')
    for line in readme_text.splitlines():
        if line.startswith('#'):
            heading=line.lstrip('#').strip()
            continue
        m=link_re.match(line)
        if not m or deny.search(heading) or not allowed_heading.search(heading): continue
        title,url=m.groups()
        if 'github.com/Shubhamsaboo/awesome-llm-apps' in url: continue
        base={
            'id':normalize_id('external_reference',url),'source_type':'external_reference',
            'upstream_path':None,'external_url':url,'license_status':'UNVERIFIED',
            'category':'agent_app','subtype':'external_reference','title':title,
            'readme_path':'README.md','skill_paths':[],'manifest_paths':[],
            'env_example_paths':[],'docker_paths':[],'mcp_related_paths':[],
            'languages':[],'frameworks':[],'providers':[],'external_services':[url],
            'upstream_commit':commit,'section':heading,
        }
        base.update(classify_execution(base)); base['execution_class']='REFERENCE_ONLY'
        entries.append(base)
    return entries

def build_catalog(root:Path,commit:str)->dict:
    root=Path(root)
    canonical={}
    registry=root/'agent_skills'/'registry.json'
    if registry.exists():
        data=json.loads(registry.read_text())
        canonical={x.get('path'):x for x in data.get('skills',[]) if x.get('path')}
    entries=[]
    for d in _qualifying_dirs(root):
        rel=d.relative_to(root).as_posix()
        manifests,envs,docker,skills,mcp,langs=_attach_files(root,d)
        subtype='agent_app'; title=_title_from_readme(d/'README.md')
        if (d/'SKILL.md').exists():
            subtype='canonical_skill' if rel in canonical else 'project_internal_skill'
            title=(canonical.get(rel) or {}).get('name') or d.name
        entry={
            'id':normalize_id('upstream_internal',rel),'source_type':'upstream_internal',
            'upstream_path':rel,'external_url':None,
            'license_status':'VERIFIED_NESTED_LICENSE' if _nearest_license(root,d) not in (None,'LICENSE') else 'VERIFIED_ROOT_LICENSE',
            'license_path':_nearest_license(root,d),'category':'skill' if 'skill' in subtype else 'agent_app',
            'subtype':subtype,'title':title,'readme_path':f'{rel}/README.md' if (d/'README.md').exists() else None,
            'skill_paths':skills,'manifest_paths':manifests,'env_example_paths':envs,
            'docker_paths':docker,'mcp_related_paths':mcp,'languages':langs,
            'frameworks':[],'providers':[],'external_services':[],'upstream_commit':commit,
        }
        entry.update(classify_execution(entry)); entries.append(entry)
    if (root/'README.md').exists(): entries.extend(extract_external_references((root/'README.md').read_text(errors='ignore'),commit))
    entries.sort(key=lambda e:e['id'])
    return {'schema_version':1,'upstream_commit':commit,'entries':entries}

def build_summary(catalog:dict)->dict:
    by_source=Counter(e['source_type'] for e in catalog['entries'])
    by_category=Counter(e['category'] for e in catalog['entries'])
    by_class=Counter(e['execution_class'] for e in catalog['entries'])
    return {'schema_version':catalog.get('schema_version',1),'upstream_commit':catalog.get('upstream_commit'),'entries':len(catalog['entries']),'by_source_type':dict(sorted(by_source.items())),'by_category':dict(sorted(by_category.items())),'by_execution_class':dict(sorted(by_class.items()))}

scan_internal_entries=lambda root,commit: [e for e in build_catalog(root,commit)['entries'] if e['source_type']=='upstream_internal']
