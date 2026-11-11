#!/usr/bin/env python3
"""Bridge local de P&ID para verificacao humana no workflow MCE.

Adaptadores baseados em contratos publicos OBSERVADOS, sem codigo de terceiros.
Nao acessa rede, nao executa software de terceiros, nao modifica XLSX e nunca
transforma conexao de P&ID ou matriz didatica em logica de intertravamento.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, deque
from pathlib import Path

BRIDGE_VERSION='mce.pid.v1'
CATALOG={
 'azure': {
  'repo':'Azure-Samples/digitization-of-piping-and-instrument-diagrams',
  'head':'c51302e3ec34147c676ef6eedbdd7551ea908b05',
  'contract':'docs/graph-construction-design.md#output',
  'license':'MIT','mode':'POTENTIAL_TOPOLOGY'},
 'houston':{
  'repo':'S-Houston/digitised-pid-mlops',
  'head':'f0165e6477be7d891ee2d2403a65e474f484cb17',
  'contract':'src/postprocessing/text_extraction.py:process_text_files',
  'license':'NAO_IDENTIFICADA','mode':'OCR_TEXT_ONLY'},
 'industrial':{
  'repo':'ZzzJjt/Industrial-Control',
  'head':'df9751647f92ea91ff8f51e985f8dbb6e663f380',
  'contract':'Models/Deepseek/B-A-B(Before-After-Before)/Interlocks/Interlock Cause & Effect Matrix.md',
  'license':'NAO_IDENTIFICADA','mode':'NON_NORMATIVE_BENCHMARK'},
}
MAX_BYTES=8_000_000
MAX_ELEMENTS=20_000


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _read_limited(path):
    p=Path(path)
    if not p.is_file():raise ValueError('Arquivo de entrada ausente.')
    if p.stat().st_size>MAX_BYTES:raise ValueError('Arquivo supera limite seguro de 8 MB.')
    return p.read_text(encoding='utf-8-sig')


def _text(s,where,maxlen=1024):
    if not isinstance(s,(str,int,float)) or isinstance(s,bool):
        raise ValueError('Valor textual invalido em '+where)
    t=str(s).strip()
    if not t or len(t)>maxlen or any(ord(c)<32 and c not in '\t\n' for c in t):
        raise ValueError('Texto vazio, excessivo ou com caracteres de controle em '+where)
    return t


def _document(args):
    return {'document_number':_text(args.document,'documento'),
      'revision':_text(args.revision,'revisao'),
      'evidence_location':_text(args.location,'localizacao')}


def _base(args,input_path):
    info=CATALOG[args.adapter]
    return {'schema':BRIDGE_VERSION,'adapter':args.adapter,
      'source':{'repo':info['repo'],'commit_sha':info['head'],
                'interface_reference':info['contract'],'license':info['license'],
                'input_file':Path(input_path).name,'input_sha256':_sha(input_path),
                'evidence_type':'USER_SUPPLIED_EXPORT_NOT_INDEPENDENTLY_CONFIRMED'},
      'document':_document(args),'components':[],'connections':[],
      'ocr_observations':[],'reference_matrix':None,'warnings':[],
      'eligible_for_mce_automatic':False,'approved_safety_effects':[],
      'approval_status':'AGUARDANDO_ENGENHEIRO'}


def _json_input(path):
    try:return json.loads(_read_limited(path))
    except json.JSONDecodeError as e:raise ValueError('JSON invalido: '+str(e)) from e


def _azure(data,out):
    # Contrato de adjacencia efetivamente descrito no docs/graph-construction-design.md.
    if not isinstance(data,dict) or not isinstance(data.get('assets'),list):
        raise ValueError('Azure requer objeto assets em lista, nao resposta job_status.')
    if len(data['assets'])>MAX_ELEMENTS:raise ValueError('Muitos assets no export.')
    known={}
    for asset in data['assets']:
        if not isinstance(asset,dict):raise ValueError('Asset invalido')
        ident=_text(asset.get('id'),'asset.id',180)
        if ident in known:raise ValueError('ID de asset repetido: '+ident)
        label=asset.get('label')
        cand=asset.get('text_associated')
        known[ident]={
            'id':ident,'class_name':str(label)[:128] if label is not None else 'NAO_CLASSIFICADO',
            'tag_candidate':str(cand)[:180] if cand is not None else None,
            'bounding_box':asset.get('bounding_box'),
            'verified_tag':False,'verified_connection':False,
            'origin':'AI_EXTRACTION_UNREVIEWED'}
    edges=[]
    for asset in data['assets']:
        a=_text(asset['id'],'source',180)
        conns=asset.get('connections',[])
        if not isinstance(conns,list):raise ValueError('connections exige lista')
        for conn in conns:
            if not isinstance(conn,dict):raise ValueError('Connection invalida')
            b=_text(conn.get('id'),'connected_symbol_id',180)
            if b not in known:
                known[b]={'id':b,'class_name':'REFERENCIADO_SEM_ASSET',
                     'tag_candidate':None,'bounding_box':None,'verified_tag':False,
                     'verified_connection':False,'origin':'MISSING_ASSET'}
                out['warnings'].append('GRAFO_INCOMPLETO: conexao '+a+' -> '+b+' sem descricao de asset')
            direction=conn.get('flow_direction','unknown')
            if direction not in ('unknown','upstream','downstream',None):
                raise ValueError('Direcao de fluxo nao reconhecida: '+str(direction))
            segs=conn.get('segments',[])
            if not isinstance(segs,list):raise ValueError('segments exige lista')
            edges.append({'source_id':a,'target_id':b,'reported_flow_direction':direction or 'unknown',
                 'relation':'CONECTIVIDADE_POTENCIAL_NAO_VALIDADA',
                 'segment_ids':[str(x.get('id')) for x in segs if isinstance(x,dict) and x.get('id') is not None],
                 'verified':False})
            if len(edges)>MAX_ELEMENTS:raise ValueError('Muitas conexoes no export')
    out['components']=list(known.values());out['connections']=edges
    out['warnings'].append('PROIBIDO inferir acao MCE, sinal ISA, fluxo ou intertravamento apenas deste grafo.')
    return out


def _houston(csv_data,out):
    reader=csv.DictReader(csv_data.splitlines())
    if not reader.fieldnames or not {'filename','consolidated_text'}.issubset(reader.fieldnames):
        raise ValueError('Houston requer CSV: filename,consolidated_text')
    for i,row in enumerate(reader,2):
        if i>MAX_ELEMENTS:raise ValueError('Muitas linhas OCR')
        name=_text(row.get('filename'),'filename',320)
        val=_text(row.get('consolidated_text'),'consolidated_text',6000)
        out['ocr_observations'].append({'source_filename':name,'csv_line':i,
                 'text_as_recognized':val,'verified_tag':False,
                 'origin':'OCR_NOT_ACCEPTED_AS_ENGINEERING_EVIDENCE'})
        if val[:1] in ('=','+','-','@'):
            out['warnings'].append('RISCO_FORMULA_CSV: linha '+str(i)+'; nao exportar diretamente para Excel')
    out['warnings'].append('Texto OCR nao prova TAG ou setpoint; conferir visualmente com P&ID aprovado.')
    return out


def _industrial(data,out):
    # Formato de intercâmbio criado pelo sistema, inspirado em estruturas
    # conceituais, NAO executa/copIa o codigo de exemplo do repositorio.
    if not isinstance(data,dict) or not all(k in data for k in ('causes','effects','interlock_matrix')):
        raise ValueError('Industrial requer JSON com causes, effects, interlock_matrix')
    causes=data['causes'];effects=data['effects'];mapping=data['interlock_matrix']
    if not isinstance(causes,list) or not isinstance(effects,list) or not isinstance(mapping,dict):
        raise ValueError('Tipos invalidos de causa/efeito/mapeamento')
    if len(causes)>MAX_ELEMENTS or len(effects)>MAX_ELEMENTS:raise ValueError('Matriz de referencia excessiva')
    cs=[_text(x,'causa',240) for x in causes]
    es=[_text(x,'efeito',240) for x in effects]
    if len(set(cs))!=len(cs) or len(set(es))!=len(es):raise ValueError('Causa ou efeito duplicado')
    if set(mapping)-set(cs):raise ValueError('Mapeamento possui causa nao definida')
    used=set()
    for k,values in mapping.items():
        if not isinstance(values,list):raise ValueError('Lista de efeitos obrigatoria para '+k)
        for effect in values:
            e=_text(effect,'efeito associado',240)
            if e not in es:raise ValueError('Efeito ausente no catalogo: '+e)
            used.add(e)
    out['reference_matrix']={'causes':cs,'effects':es,'interlock_matrix':mapping,
        'uncovered_effects':sorted(set(es)-used),
        'origin':'EXEMPLO_DE_TERCEIRO_NAO_NORMATIVO','eligible_for_project':False}
    if set(es)-used:out['warnings'].append('EFEITOS_DE_EXEMPLO_SEM_COBERTURA: '+', '.join(sorted(set(es)-used)))
    out['warnings'].append('EXEMPLO DIDATICO: nenhuma acao automaticamente convertida para MCE do projeto.')
    return out


def _check_graph(out):
    comps=out['components'];edges=out['connections'];ids={x['id'] for x in comps}
    if len(ids)!=len(comps):raise ValueError('IDs de componentes duplicados')
    for e in edges:
        if e['source_id'] not in ids or e['target_id'] not in ids:
            raise ValueError('Conexao com origem ou destino inexistente')
    tags=Counter(x['tag_candidate'] for x in comps if x['tag_candidate'])
    duplicated=sorted(x for x,n in tags.items() if n>1)
    for t in duplicated:out['warnings'].append('TAG_OCR_DUPLICADA: '+t)
    adjacency={i:set() for i in ids}
    for e in edges:
        a=e['source_id'];b=e['target_id'];adjacency[a].add(b);adjacency[b].add(a)
    groups=[];pending=set(ids)
    while pending:
        start=min(pending);seen={start};queue=deque([start]);pending.remove(start)
        while queue:
            for nxt in adjacency[queue.popleft()]:
                if nxt not in seen:
                    seen.add(nxt);queue.append(nxt);pending.remove(nxt)
        groups.append(sorted(seen))
    return {'components':len(comps),'edges':len(edges),'isolated_components':sum(not x for x in adjacency.values()),
            'connected_groups':len(groups),'groups':groups,
            'tag_candidates_not_validated':sum(bool(x['tag_candidate']) for x in comps),
            'duplicate_tag_candidates':duplicated,
            'approved_cause_effect_relations':0}


def run_import(args):
    p=Path(args.input)
    input_text=_read_limited(p)
    out=_base(args,p)
    if args.adapter=='azure':out=_azure(json.loads(input_text),out)
    elif args.adapter=='houston':out=_houston(input_text,out)
    elif args.adapter=='industrial':out=_industrial(json.loads(input_text),out)
    else:raise ValueError('Adaptador desconhecido')
    out['graph_quality']=_check_graph(out)
    dest=Path(args.output)
    if dest.resolve()==p.resolve():raise ValueError('Proibido sobrescrever entrada')
    if dest.exists():raise ValueError('Destino existente: mantenha historico versionado.')
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'adapter':args.adapter,'components':len(out['components']),
      'connections':len(out['connections']),'ocr_lines':len(out['ocr_observations']),
      'warnings':len(out['warnings']),'eligible_for_mce_automatic':False,'output':str(dest)},ensure_ascii=False))


def run_compare_io(args):
    data=_json_input(args.graph)
    if data.get('schema')!=BRIDGE_VERSION:raise ValueError('Grafo nao corresponde ao contrato atual')
    if data.get('eligible_for_mce_automatic') is not False:raise ValueError('Contrato violado: preenchimento automatico')
    text=_read_limited(args.io)
    reader=csv.DictReader(text.splitlines())
    if not reader.fieldnames or 'tag' not in reader.fieldnames:
        raise ValueError('Lista de I/O exige coluna tag')
    io_tags=[]
    for i,row in enumerate(reader,2):
        if i>MAX_ELEMENTS:raise ValueError('Lista I/O longa demais')
        io_tags.append(_text(row['tag'],'io.tag',200))
    if len(set(io_tags))!=len(io_tags):raise ValueError('TAG duplicada na lista de I/O')
    extracted=Counter(x['tag_candidate'] for x in data['components'] if x['tag_candidate'])
    result={'schema':BRIDGE_VERSION,'reference_input_sha256':_sha(args.graph),
      'io_sha256':_sha(args.io),'only_in_io':sorted(set(io_tags)-set(extracted)),
      'only_in_pid_unverified':sorted(set(extracted)-set(io_tags)),
      'exact_string_matches_pending_review':sorted(set(io_tags)&set(extracted)),
      'duplicate_pid_candidates':sorted(k for k,v in extracted.items() if v>1),
      'validated_cause_effects':0,'human_review_required':True}
    dest=Path(args.output)
    if dest.exists() or dest.resolve() in (Path(args.io).resolve(),Path(args.graph).resolve()):
        raise ValueError('Nao sobrescrever arquivos')
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'matches':len(result['exact_string_matches_pending_review']),
          'mismatches':len(result['only_in_io'])+len(result['only_in_pid_unverified']),
          'human_review_required':True},ensure_ascii=False))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest='command',required=True)
    sp=sub.add_parser('catalog');sp.set_defaults(func=lambda a:print(json.dumps(CATALOG,ensure_ascii=False,indent=2)))
    sp=sub.add_parser('import');sp.add_argument('--adapter',choices=sorted(CATALOG),required=True)
    sp.add_argument('--input',required=True);sp.add_argument('--output',required=True)
    sp.add_argument('--document',required=True);sp.add_argument('--revision',required=True)
    sp.add_argument('--location',required=True);sp.set_defaults(func=run_import)
    sp=sub.add_parser('compare-io');sp.add_argument('--graph',required=True)
    sp.add_argument('--io',required=True);sp.add_argument('--output',required=True)
    sp.set_defaults(func=run_compare_io)
    args=ap.parse_args()
    try:args.func(args)
    except (ValueError,OSError,KeyError,json.JSONDecodeError,csv.Error) as e:
        print('BLOQUEADO: '+str(e),file=sys.stderr);sys.exit(2)

if __name__=='__main__':main()
