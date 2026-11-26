"""Regressoes dos adaptadores P&ID: engenharia, origem e fail-closed."""
from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
BRIDGE=ROOT/'.agents/skills/engenharia-mce-projeto/scripts/pid_bridge.py'
SPEC=importlib.util.spec_from_file_location('pid_bridge',BRIDGE)
pid=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(pid)


def run(tmp_path,adapter,text):
    raw=tmp_path/('entrada.csv' if adapter=='houston' else 'entrada.json')
    raw.write_text(text,encoding='utf-8')
    out=tmp_path/'normalizado.json'
    p=subprocess.run([sys.executable,str(BRIDGE),'import','--adapter',adapter,
        '--input',str(raw),'--output',str(out),
        '--document','PI-001','--revision','R00','--location','folha 1'],
        capture_output=True,text=True)
    return p,out,raw


def azure_sample():
    return {'assets':[{'id':'s-1','label':'valve','text_associated':'XV-101',
        'bounding_box':{'topX':0.1,'topY':0.1,'bottomX':0.2,'bottomY':0.2},
        'connections':[{'id':'s-2','label':'pump','flow_direction':'unknown','segments':[{'id':'l-1'}]}]},
      {'id':'s-2','label':'pump','text_associated':'P-101','connections':[]}]}


def test_azure_export_as_documented_has_no_safety_action(tmp_path):
    p,out,raw=run(tmp_path,'azure',json.dumps(azure_sample()))
    assert p.returncode==0,p.stderr
    d=json.loads(out.read_text())
    assert d['graph_quality']['components']==2
    assert d['graph_quality']['connected_groups']==1
    assert d['connections'][0]['relation']=='CONECTIVIDADE_POTENCIAL_NAO_VALIDADA'
    assert d['eligible_for_mce_automatic'] is False
    assert d['approved_safety_effects']==[]
    assert d['components'][0]['tag_candidate']=='XV-101'
    assert d['components'][0]['verified_tag'] is False
    assert d['source']['input_sha256']==pid._sha(raw)
    assert d['document']['document_number']=='PI-001'
    assert raw.exists()


def test_azure_refuses_job_status_instead_of_assets(tmp_path):
    p,out,_=run(tmp_path,'azure',json.dumps({'job_status':'Submitted'}))
    assert p.returncode==2 and 'assets' in p.stderr and not out.exists()


def test_azure_refuses_duplicate_ids(tmp_path):
    data=azure_sample();data['assets'][1]['id']='s-1'
    p,out,_=run(tmp_path,'azure',json.dumps(data))
    assert p.returncode==2 and 'repetido' in p.stderr and not out.exists()


def test_azure_unknown_target_remains_unreviewed(tmp_path):
    data=azure_sample();data['assets'].pop()
    p,out,_=run(tmp_path,'azure',json.dumps(data))
    assert p.returncode==0,p.stderr
    d=json.loads(out.read_text())
    assert len(d['components'])==2
    assert any('GRAFO_INCOMPLETO' in x for x in d['warnings'])
    assert any(x['origin']=='MISSING_ASSET' for x in d['components'])


def test_azure_unknown_direction_is_rejected(tmp_path):
    data=azure_sample();data['assets'][0]['connections'][0]['flow_direction']='open-valve-now'
    p,out,_=run(tmp_path,'azure',json.dumps(data))
    assert p.returncode==2 and not out.exists()


def test_azure_duplicate_tag_candidates_reported(tmp_path):
    data=azure_sample();data['assets'][1]['text_associated']='XV-101'
    p,out,_=run(tmp_path,'azure',json.dumps(data))
    assert p.returncode==0,p.stderr
    d=json.loads(out.read_text())
    assert d['graph_quality']['duplicate_tag_candidates']==['XV-101']


def test_houston_csv_no_tag_invention(tmp_path):
    p,out,_=run(tmp_path,'houston','filename,consolidated_text\nplanta_1,"XV 101 P 101"\n')
    assert p.returncode==0,p.stderr
    d=json.loads(out.read_text())
    assert len(d['ocr_observations'])==1 and not d['components']
    assert d['ocr_observations'][0]['verified_tag'] is False
    assert d['approved_safety_effects']==[]


def test_houston_csv_excel_formula_alert(tmp_path):
    p,out,_=run(tmp_path,'houston','filename,consolidated_text\na,=HYPERLINK(1)\n')
    assert p.returncode==0,p.stderr
    assert any('RISCO_FORMULA_CSV' in x for x in json.loads(out.read_text())['warnings'])


def test_houston_csv_requires_exact_columns(tmp_path):
    p,out,_=run(tmp_path,'houston','file,text\na,b\n')
    assert p.returncode==2 and not out.exists()


def test_industrial_reference_coverage_correct_even_with_shadowing_bug_in_upstream(tmp_path):
    demo={'causes':['C1'],'effects':['E1','E2'], 'interlock_matrix':{'C1':['E1']}}
    p,out,_=run(tmp_path,'industrial',json.dumps(demo))
    assert p.returncode==0,p.stderr
    d=json.loads(out.read_text())
    assert d['reference_matrix']['uncovered_effects']==['E2']
    assert d['reference_matrix']['eligible_for_project'] is False
    assert d['eligible_for_mce_automatic'] is False
    assert not d['approved_safety_effects']


def test_industrial_unknown_effect_fails_closed(tmp_path):
    demo={'causes':['C1'],'effects':['E1'],'interlock_matrix':{'C1':['E2']}}
    p,out,_=run(tmp_path,'industrial',json.dumps(demo))
    assert p.returncode==2 and 'Efeito ausente' in p.stderr and not out.exists()


def test_industrial_unknown_cause_fails_closed(tmp_path):
    demo={'causes':['C1'],'effects':['E1'],'interlock_matrix':{'C2':['E1']}}
    p,out,_=run(tmp_path,'industrial',json.dumps(demo))
    assert p.returncode==2 and not out.exists()


def test_compare_io_exact_only_pending_review(tmp_path):
    p,out,_=run(tmp_path,'azure',json.dumps(azure_sample()))
    assert p.returncode==0,p.stderr
    io=tmp_path/'io.csv';io.write_text('tag\nXV-101\nPT-100\n',encoding='utf-8')
    report=tmp_path/'diff.json'
    c=subprocess.run([sys.executable,str(BRIDGE),'compare-io','--graph',str(out),
      '--io',str(io),'--output',str(report)],capture_output=True,text=True)
    assert c.returncode==0,c.stderr
    d=json.loads(report.read_text())
    assert d['exact_string_matches_pending_review']==['XV-101']
    assert d['only_in_io']==['PT-100']
    assert d['only_in_pid_unverified']==['P-101']
    assert d['validated_cause_effects']==0


def test_input_not_overwritten_and_output_is_create_only(tmp_path):
    p,out,_=run(tmp_path,'azure',json.dumps(azure_sample()))
    assert p.returncode==0
    p2,out2,_=run(tmp_path,'azure',json.dumps(azure_sample()))
    assert p2.returncode==2 and 'Destino existente' in p2.stderr


def test_bridge_requires_provenance_args(tmp_path):
    raw=tmp_path/'a.json';raw.write_text(json.dumps(azure_sample()))
    r=subprocess.run([sys.executable,str(BRIDGE),'import','--adapter','azure',
        '--input',str(raw),'--output',str(tmp_path/'b.json')],capture_output=True,text=True)
    assert r.returncode!=0 and not (tmp_path/'b.json').exists()


def test_catalog_three_adapters_and_read_only(tmp_path):
    p=subprocess.run([sys.executable,str(BRIDGE),'catalog'],capture_output=True,text=True)
    assert p.returncode==0
    d=json.loads(p.stdout)
    assert set(d)=={'azure','houston','industrial'}
    assert d['industrial']['license']=='NAO_IDENTIFICADA'


def test_research_snapshot_reproducible_and_ten_reviewed():
    p=subprocess.run([sys.executable,str(ROOT/'research/construir_funil.py')],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    with (ROOT/'research/candidatos_100.csv').open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
    top=json.loads((ROOT/'research/top10_verificados.json').read_text())['reviewed']
    assert len(rows)==100 and len(top)==10 and len({r['repo'] for r in rows})==100
    assert all(x['repo'] in {r['repo'] for r in rows} for x in top)
