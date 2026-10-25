"""Integrity-checked Replica dispatcher and non-overwriting skill installer."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def contained(root, relative):
    rel=PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or any(':' in part for part in rel.parts):
        raise ValueError('Unsafe package path: '+relative)
    path=root.joinpath(*rel.parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Package link escapes root: '+relative)
    return path

def verify_package(root=ROOT):
    root=Path(root)
    lock=json.loads((root/'upstream-lock.json').read_text(encoding='utf-8'))
    if lock.get('schema_version')!=1 or len(lock.get('skills',[]))!=11 or len(lock.get('tools',{}))!=6:
        raise ValueError('Invalid Replica lock')
    for name, expected in lock['files'].items():
        path=contained(root,name)
        if not path.is_file() or digest(path)!=expected:
            raise ValueError('Pinned source changed: '+name)
    for name,path in lock['tools'].items():
        if path not in lock['files'] or not path.endswith('.py'):
            raise ValueError('Tool is not pinned: '+name)
    for skill in lock['skills']:
        if not skill.startswith('replica-') or '/' in skill or '\\' in skill or ':' in skill:
            raise ValueError('Invalid skill name')
        if 'skills/'+skill+'/SKILL.md' not in lock['files']:
            raise ValueError('Skill is not pinned: '+skill)
    return lock

def run_tool(root, name, arguments):
    root=Path(root); lock=verify_package(root)
    if name not in lock['tools']:
        raise ValueError('Unknown tool: '+name)
    script=contained(root,lock['tools'][name])
    return subprocess.run([sys.executable,str(script),*arguments],shell=False,
                          capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)

def install_skills(root, destination, dry_run=False):
    root=Path(root); destination=Path(destination); lock=verify_package(root)
    names=lock['skills']+['replica-power-arena']
    actions=[]; files={}
    # Validate every destination before writing any skill. Never overwrite human files.
    for name in names:
        source=contained(root,'skills/'+name); target=destination/name
        entries=[p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
        if not entries or not (source/'SKILL.md').is_file():
            raise ValueError('Skill content missing: '+name)
        if target.is_symlink() or (target.exists() and not target.resolve().is_relative_to(destination.resolve())):
            raise ValueError('Destination escapes skill root')
        if target.exists():
            if not all((target/p.relative_to(source)).is_file() and digest(target/p.relative_to(source))==digest(p) for p in entries):
                raise FileExistsError('Existing skill differs; preserved: '+str(target))
            action='matching'
        else: action='install'
        actions.append((source,target,action))
        for p in entries:
            files[str(target/p.relative_to(source))]=digest(p)
    if not dry_run:
        destination.mkdir(parents=True,exist_ok=True)
        for source,target,action in actions:
            if action=='install': shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__'))
    return {'installed':sum(a=='install' for _,_,a in actions),
            'already_matching':sum(a=='matching' for _,_,a in actions),'dry_run':dry_run,
            'repository':lock['repository'],'commit':lock['commit'],'destination':str(destination.resolve()),
            'files':files,'rollback':'Remove only receipt-listed files whose digest still matches; preserve changed or additional human files.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('verify')
    run=commands.add_parser('run');run.add_argument('tool');run.add_argument('arguments',nargs=argparse.REMAINDER)
    install=commands.add_parser('install');install.add_argument('--dest',type=Path,required=True)
    install.add_argument('--receipt',type=Path,required=True);install.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    try:
        if args.command=='verify':
            lock=verify_package();print(json.dumps({'status':'PASS','skills':len(lock['skills']),'tools':list(lock['tools']),'commit':lock['commit']}));return 0
        if args.command=='run':
            result=run_tool(ROOT,args.tool,args.arguments)
            print(result.stdout,end='');print(result.stderr,end='',file=sys.stderr);return result.returncode
        receipt=install_skills(ROOT,args.dest,args.dry_run)
        args.receipt.parent.mkdir(parents=True,exist_ok=True)
        args.receipt.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
        print(json.dumps({k:v for k,v in receipt.items() if k!='files'}));return 0
    except (OSError,ValueError,subprocess.TimeoutExpired) as error:
        print(str(error),file=sys.stderr);return 2

if __name__=='__main__': raise SystemExit(main())
