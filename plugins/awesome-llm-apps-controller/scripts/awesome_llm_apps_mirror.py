from __future__ import annotations
from pathlib import Path
import hashlib, os, shutil, subprocess

EXCLUDED_DIRS={'.git','node_modules','.venv','venv','__pycache__','.pytest_cache','.next','dist','build'}
MEDIA_EXT={'.gif','.mp4','.mov','.webm','.avi'}
LIMIT=10*1024*1024

def _git_sha(root:Path, rel:str):
    try:
        p=subprocess.run(['git','-C',str(root),'ls-files','-s','--',rel],capture_output=True,text=True,check=False)
        if p.stdout.strip(): return p.stdout.split()[1]
    except OSError: pass
    f=root/rel
    if f.is_file(): return hashlib.sha1(f.read_bytes()).hexdigest()
    return None

def plan_mirror(root:Path):
    root=Path(root).resolve(); plan=[]; seen_dirs=set()
    for cur,dirs,files in os.walk(root,topdown=True,followlinks=False):
        c=Path(cur)
        keep=[]
        for d in sorted(dirs):
            p=c/d; rel=p.relative_to(root).as_posix()
            if d in EXCLUDED_DIRS:
                plan.append({'path':rel,'action':'exclude','reason':'generated_or_dependency_dir','size':0,'git_sha':_git_sha(root,rel)}); continue
            if p.is_symlink():
                try: target=p.resolve(strict=False); safe=(target==root or root in target.parents)
                except OSError: safe=False
                if not safe:
                    plan.append({'path':rel,'action':'exclude','reason':'unsafe_symlink','size':0,'git_sha':_git_sha(root,rel)}); continue
            keep.append(d)
        dirs[:]=keep
        for name in sorted(files):
            p=c/name; rel=p.relative_to(root).as_posix()
            if p.is_symlink():
                try: target=p.resolve(strict=False); safe=(target==root or root in target.parents)
                except OSError: safe=False
                if not safe:
                    plan.append({'path':rel,'action':'exclude','reason':'unsafe_symlink','size':0,'git_sha':_git_sha(root,rel)}); continue
                plan.append({'path':rel,'action':'include_symlink','reason':None,'size':0,'git_sha':_git_sha(root,rel)}); continue
            size=p.stat().st_size
            if p.suffix.lower() in MEDIA_EXT and size>LIMIT:
                plan.append({'path':rel,'action':'exclude','reason':'large_demo_media','size':size,'git_sha':_git_sha(root,rel)})
            else:
                plan.append({'path':rel,'action':'include','reason':None,'size':size,'git_sha':_git_sha(root,rel)})
    plan.sort(key=lambda x:x['path']); return plan

def copy_mirror(root:Path,dest:Path,plan:list,commit:str):
    root=Path(root).resolve(); dest=Path(dest)
    if dest.exists(): shutil.rmtree(dest)
    dest.mkdir(parents=True)
    excluded=[]; included_files=0; included_bytes=0
    for item in plan:
        src=root/item['path']; out=dest/item['path']
        if item['action']=='exclude':
            excluded.append({**item,'upstream_commit':commit}); continue
        out.parent.mkdir(parents=True,exist_ok=True)
        if item['action']=='include_symlink': os.symlink(os.readlink(src),out)
        else:
            shutil.copy2(src,out); included_files+=1; included_bytes+=item['size']
    return {'included_files':included_files,'included_bytes':included_bytes,'excluded':excluded,'excluded_files':len(excluded),'excluded_bytes':sum(x['size'] for x in excluded),'upstream_commit':commit}
