#!/usr/bin/env python3
"""Entrada unica para os adaptadores P&ID do workflow MCE existente.

Mantem fases originais de mce_workflow.py intactas e integra evidencias
secundarias SEM promover automaticamente reconhecimento de P&ID em logica MCE.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WF=ROOT/'.agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py'
BRIDGE=ROOT/'.agents/skills/engenharia-mce-projeto/scripts/pid_bridge.py'
SP=importlib.util.spec_from_file_location('mce_existing_workflow',WF)
wf=importlib.util.module_from_spec(SP);SP.loader.exec_module(wf)


def _ensure_intake(w):
    state=wf.load_state(w)
    if state['status']!='INVENTARIADO':
        raise ValueError('STOP: adaptadores so podem rodar antes do relatorio de entendimento e da autorizacao.')
    return state


def _source(w,state,name):
    source=next((x for x in state['sources'] if x['name']==name),None)
    if not source:raise ValueError('Documento nao consta do inventario: '+name)
    path=w/'sources'/name
    if not path.exists() or wf.digest(path)!=source['sha256']:
        raise ValueError('Documento externo ou SHA alterado: '+name)
    return path


def _output(w,name):
    if not isinstance(name,str) or Path(name).name!=name or '\\' in name or '/' in name or name in ('','.','..') or not name.lower().endswith('.json'):
        raise ValueError('Nome de saida invalido: use somente arquivo .json no diretorio derived.')
    path=w/'derived'/name
    if path.exists():raise ValueError('Saida existente; versionar o resultado em novo workspace.')
    return path


def _invoke(*params):
    result=subprocess.run([sys.executable,str(BRIDGE),*params],
         capture_output=True,text=True,check=False)
    if result.returncode:
        raise ValueError('Bridge bloqueou operacao: '+result.stderr.strip())
    return json.loads(result.stdout)


def _record(w,state,kind,result,source_name,out):
    state.setdefault('pid_integrations',[]).append({
        'kind':kind,'source_name':source_name,'output_file':str(out.relative_to(w)),
        'output_sha256':wf.digest(out),'review_status':'PENDENTE_REVISAO_ENGENHARIA',
        'eligible_to_edit_matrix':False,'result':result})
    wf.writejson(w/'state.json',state)
    print(json.dumps({'workflow_status':state['status'],'result':result,
       'system_gate':'STOP_ANTES_ENTENDIMENTO',
       'next_step':'Analisar os resultados e criar analise.json com evidencias do documento original.'},ensure_ascii=False))


def do_import(a):
    w=Path(a.workspace).resolve();s=_ensure_intake(w)
    source=_source(w,s,a.source_name)
    out=_output(w,a.output_name)
    result=_invoke('import','--adapter',a.adapter,'--input',str(source),
       '--output',str(out),'--document',a.document,'--revision',a.revision,'--location',a.location)
    _record(w,s,'PID_IMPORT:'+a.adapter,result,a.source_name,out)


def do_io(a):
    w=Path(a.workspace).resolve();s=_ensure_intake(w)
    path=_source(w,s,a.io_name)
    candidate=(w/'derived'/a.graph_name).resolve()
    derived=(w/'derived').resolve()
    if not candidate.is_relative_to(derived) or not candidate.is_file():
        raise ValueError('Grafo nao foi gerado na pasta derived do workspace.')
    rec=next((x for x in s.get('pid_integrations',[]) if x['output_file']==str(candidate.relative_to(w))),None)
    if not rec or wf.digest(candidate)!=rec['output_sha256']:
        raise ValueError('Grafo externo/alterado: importar pelo workflow principal primeiro.')
    out=_output(w,a.output_name)
    result=_invoke('compare-io','--graph',str(candidate),'--io',str(path),'--output',str(out))
    _record(w,s,'IO_COMPARE',result,a.io_name,out)


def do_status(a):
    w=Path(a.workspace).resolve();s=wf.load_state(w)
    print(json.dumps({'status':s['status'],'pid_integrations':s.get('pid_integrations',[]),
       'original_excel_sha256':s['template_sha256']},ensure_ascii=False,indent=2))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('pid-import');a.add_argument('--workspace',required=True)
    a.add_argument('--adapter',required=True,choices=['azure','houston','industrial'])
    a.add_argument('--source-name',required=True)
    a.add_argument('--document',required=True);a.add_argument('--revision',required=True)
    a.add_argument('--location',required=True);a.add_argument('--output-name',default='PID_NORMALIZADO.json')
    a.set_defaults(func=do_import)
    a=sub.add_parser('compare-io');a.add_argument('--workspace',required=True)
    a.add_argument('--graph-name',default='PID_NORMALIZADO.json')
    a.add_argument('--io-name',required=True);a.add_argument('--output-name',default='COMPARACAO_IO.json')
    a.set_defaults(func=do_io)
    a=sub.add_parser('status');a.add_argument('--workspace',required=True);a.set_defaults(func=do_status)
    args=ap.parse_args()
    try:args.func(args)
    except (ValueError,KeyError,OSError,PermissionError) as e:
        print('BLOQUEADO: '+str(e),file=sys.stderr);sys.exit(2)

if __name__=='__main__':main()
