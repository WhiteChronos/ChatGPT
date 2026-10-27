"""Build a self-contained original adapter plugin for each verified repository."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile
from manifest_compat import portable, codex, VERSION

def write_owned(path, content):
    data=content.encode('utf-8') if isinstance(content,str) else content
    if path.exists() and path.read_bytes()!=data:
        raise FileExistsError('Preserve differing output: '+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists(): path.write_bytes(data)

def generate(root, output, packages):
    root=Path(root).resolve();output=Path(output).resolve();packages=Path(packages).resolve()
    skills=(root/'skills').resolve()
    if output==root or root.is_relative_to(output) or output.is_relative_to(skills) or packages.is_relative_to(skills):
        raise ValueError('Output must be separate from source skill files')
    rows=json.loads((root/'registry.json').read_text(encoding='utf-8'))
    prepared=[]
    for row in rows:
        name=row['skill_name']
        if not re.fullmatch('[a-z0-9-]{1,64}',name): raise ValueError('Invalid plugin identifier')
        source=skills/name
        if not source.resolve().is_relative_to(skills): raise ValueError('Source escape')
        folder=output/name
        if not folder.resolve().is_relative_to(output): raise ValueError('Output escape')
        manifest=portable(name,row['repository']+' Workflow','Workflow individual para '+row['repository'])
        overlay=codex(manifest)
        workflow={'repository':row['repository'],'skill':name,'default_mode':'individual',
                  'individual':{'steps':[name],'executed':False,'depends_on_other_systems':False},
                  'integrations':{'rea':{'skill':'whitechronos-lab','when':'static-analysis-requested'},
                                  'superpowers':{'skill':'superpowers-workflow','when':'development-or-debugging'},
                                  'replica':{'skill':'replica-workflow','when':'reconstruction-or-parity'},
                                  'arena':{'skill':'arena-workflow','when':'review-requested'},
                                  'vibe':{'skill':'vibe-coding-toolkit','when':'project-setup-or-guidance'}},
                  'execution_owner':'current host agent','background_enabled':False,
                  'web_account_installation':'NOT_VERIFIED','host_discovery':'NOT_VERIFIED'}
        files={'.codex-plugin/plugin.json':json.dumps(overlay,ensure_ascii=False,indent=2),
               'plugin.json':json.dumps(manifest,ensure_ascii=False,indent=2),
               'workflow.json':json.dumps(workflow,ensure_ascii=False,indent=2),
               'LICENSE':(root/'LICENSE').read_bytes(),
               'README.md':f'''# {row['repository']} — workflow individual

Skill: `{name}`. Plugin: `{name}`. Versão: {VERSION}.
Origem: https://github.com/{row['repository']}.

Use `${name}` ao trabalhar nas skills deste repositório. Confirme o alvo, leia a skill upstream pertinente e execute os passos autorizados com as ferramentas disponíveis no host. O arquivo `workflow.json` registra o modo individual e as integrações opcionais. Não é um executor de comandos.

O modo padrão usa somente este sistema. REA (`whitechronos-lab`) é opcional para análise estática; Superpowers para processo de desenvolvimento; Replica para reconstrução/paridade; Arena para revisão; Vibe para preparação e padrões. Escolha somente as camadas solicitadas e disponíveis. Este plugin funciona como entrada individual sem exigir a instalação do pacote conjunto.

No Codex, esta pasta pode ser usada como fonte local de plugin pelo marketplace do integrador. Na web, importe o ZIP deste plugin e confira nome e versão. Se o pacote conjunto já fornecer a mesma skill, escolha uma das entradas para evitar duplicação.

Este adaptador é próprio e referencia as fontes em `skills/{name}/references/source.json`; não distribui os corpos das skills upstream, não instala seus runtimes e preserva os plugins oficiais. Leia recursos e requisitos atuais antes de executar. Sem acesso ao checkout/conector necessário, registre BLOCKED.

Instalação, seleção e execução são evidências distintas. Upload da conta web, descoberta em novas conversas e runtime upstream permanecem não verificados. Sem serviços permanentes, monitoramento periódico, mudança de modelo/conta ou instalação Linux/WSL/Docker.
'''}
        for p in sorted(source.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts: continue
            if p.is_symlink() or not p.resolve().is_relative_to(source.resolve()): raise ValueError('Source escape')
            files['skills/'+name+'/'+p.relative_to(source).as_posix()]=p.read_bytes()
        for rel,content in files.items():
            target=folder/rel
            if not target.resolve().is_relative_to(output): raise ValueError('Output symlink escape')
            if target.exists():
                data=content.encode('utf-8') if isinstance(content,str) else content
                if target.read_bytes()!=data: raise FileExistsError('Preserve differing output: '+str(target))
        prepared.append((row,folder,files))
    # Preflight every plugin before writing any output file.
    result=[]
    for row,folder,files in prepared:
        name=row['skill_name']
        for rel,content in files.items(): write_owned(folder/rel,content)
        packages.mkdir(parents=True,exist_ok=True)
        archive=packages/(name+'-'+VERSION+'.zip')
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for rel in sorted(files): z.write(folder/rel,rel)
        result.append({'repository':row['repository'],'name':name,'version':VERSION,'zip':archive.name,
                       'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(files),
                       'web_account_installation':'NOT_RUN'})
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--output',type=Path,required=True);p.add_argument('--packages',type=Path,required=True)
    p.add_argument('--receipt',type=Path,required=True)
    args=p.parse_args();result=generate(args.root,args.output,args.packages)
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'individual_plugins':len(result),'individual_archives':len(result),'upstream_runtime':'NOT_VERIFIED','web_upload':'NOT_RUN'}))
