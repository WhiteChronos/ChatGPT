"""Build the portable skills package; no upload or account mutation."""
import argparse
import json
from pathlib import Path
import zipfile
from replica import ROOT, INTEGRATION_SKILLS, verify_package

def package(output):
    lock=verify_package(ROOT)
    original=json.loads((ROOT/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))
    manifest={'$schema':'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
              'name':original['name'],'version':original['version'],
              'description':original['description'],'author':original['author'],'license':'MIT',
              'extensions':{'com.openai':{'interface':{
                  'displayName':'Replica + Power + Arena',
                  'shortDescription':'Eleven Replica skills with workflow routing',
                  'longDescription':'Replica skills and offline helpers coordinated with existing Superpowers and Arena. Does not create remote access to Windows or force every chat.',
                  'developerName':'WhiteChronos','category':'Developer Tools'}}}}
    files=set(lock['files'])|{'LICENSE','README.md','upstream-lock.json','scripts/replica.py','scripts/workflow.py'}
    for skill in INTEGRATION_SKILLS:
        files.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'skills'/skill).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('plugin.json',json.dumps(manifest,indent=2))
        for name in sorted(files):archive.write(ROOT/name,name)
    return {'package':str(output.resolve()),'skills':len(lock['skills'])+len(INTEGRATION_SKILLS),'upstream_commit':lock['commit'],'web_account_installation':'NOT_VERIFIED'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True,type=Path)
    print(json.dumps(package(parser.parse_args().out)))
