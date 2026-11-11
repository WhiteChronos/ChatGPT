"""Testes integrados da ponte P&ID -> MCE, sem burlar STOP."""
import json
import subprocess
import sys
from pathlib import Path
from openpyxl import Workbook

ROOT=Path(__file__).resolve().parents[1]
SYS=ROOT/'scripts/mce_system.py'
WF=ROOT/'.agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py'


def exe(*args):
    return subprocess.run([sys.executable,*map(str,args)],capture_output=True,text=True)


def make_workspace(tmp_path):
    xlsx=tmp_path/'master.xlsx';Workbook().save(xlsx)
    azure=tmp_path/'azure.json'
    azure.write_text(json.dumps({'assets':[{'id':'A','label':'sensor','text_associated':'PT-101',
      'connections':[{'id':'B','label':'valve','flow_direction':'unknown','segments':[]}]},
      {'id':'B','label':'valve','text_associated':'XV-101','connections':[]}]}))
    io=tmp_path/'io.csv';io.write_text('tag\nPT-101\n')
    proj=tmp_path/'proj'
    r=exe(WF,'init','--workspace',proj,'--master',xlsx,'--sources',azure,io)
    assert r.returncode==0,r.stderr
    return proj,azure,io,xlsx


def test_main_workflow_ingests_adapter_and_maintains_excel_sha(tmp_path):
    w,azure,io,master=make_workspace(tmp_path)
    import hashlib
    digest_before=hashlib.sha256(master.read_bytes()).hexdigest()
    r=exe(SYS,'pid-import','--workspace',w,'--adapter','azure','--source-name',azure.name,
      '--document','PI-001','--revision','R01','--location','folha 2')
    assert r.returncode==0,r.stderr
    state=json.loads((w/'state.json').read_text())
    assert state['status']=='INVENTARIADO'
    assert len(state['pid_integrations'])==1
    assert state['pid_integrations'][0]['eligible_to_edit_matrix'] is False
    assert hashlib.sha256(master.read_bytes()).hexdigest()==digest_before
    assert (w/'derived/PID_NORMALIZADO.json').exists()
    diff=exe(SYS,'compare-io','--workspace',w,'--io-name',io.name)
    assert diff.returncode==0,diff.stderr
    comp=json.loads((w/'derived/COMPARACAO_IO.json').read_text())
    assert comp['exact_string_matches_pending_review']==['PT-101']
    assert comp['validated_cause_effects']==0


def test_main_workflow_rejects_external_source(tmp_path):
    w,azure,io,_=make_workspace(tmp_path)
    r=exe(SYS,'pid-import','--workspace',w,'--adapter','azure','--source-name','injetado.json',
      '--document','PI','--revision','0','--location','folha 1')
    assert r.returncode==2 and 'inventario' in r.stderr


def test_main_workflow_blocks_automation_after_report(tmp_path):
    w,azure,io,_=make_workspace(tmp_path)
    analysis=tmp_path/'analysis.json'
    analysis.write_text(json.dumps({'summary':'Sem informacao suficiente',
       'findings':[],'gaps':['pendente']}))
    assert exe(WF,'understand','--workspace',w,'--analysis',analysis).returncode==0
    r=exe(SYS,'pid-import','--workspace',w,'--adapter','azure','--source-name',azure.name,
      '--document','PI','--revision','0','--location','folha 1')
    assert r.returncode==2 and 'STOP' in r.stderr


def test_main_workflow_rejects_tampered_graph(tmp_path):
    w,azure,io,_=make_workspace(tmp_path)
    r=exe(SYS,'pid-import','--workspace',w,'--adapter','azure','--source-name',azure.name,
      '--document','PI','--revision','0','--location','folha 1')
    assert r.returncode==0,r.stderr
    graph=w/'derived/PID_NORMALIZADO.json';graph.write_text('MODIFICADO')
    r=exe(SYS,'compare-io','--workspace',w,'--io-name',io.name)
    assert r.returncode==2 and 'alterado' in r.stderr


def test_workflow_understanding_requires_human_review_per_pid_sha(tmp_path):
    w,azure,io,_=make_workspace(tmp_path)
    r=exe(SYS,'pid-import','--workspace',w,'--adapter','azure','--source-name',azure.name,
      '--document','PI-001','--revision','R01','--location','folha 2')
    assert r.returncode==0,r.stderr
    analysis=tmp_path/'analysis.json'
    basic={'summary':'Entendimento independente com documento pendente',
       'findings':[],'gaps':['Narrativa ausente']}
    analysis.write_text(json.dumps(basic))
    blocked=exe(WF,'understand','--workspace',w,'--analysis',analysis)
    assert blocked.returncode==2 and 'revisao humana' in blocked.stderr
    record=json.loads((w/'state.json').read_text())['pid_integrations'][0]
    basic['pid_integration_review']=[{
       'output_file':record['output_file'],'output_sha256':record['output_sha256'],
       'review_status':'REVISADO_COM_RESSALVAS','reviewer':'Engenheiro de teste',
       'comment':'Conexoes apenas candidatas; sem narrativa aprovada.'}]
    analysis.write_text(json.dumps(basic))
    accepted=exe(WF,'understand','--workspace',w,'--analysis',analysis)
    assert accepted.returncode==0,accepted.stderr
    report=(w/'RELATORIO_ENTENDIMENTO.md').read_text()
    assert 'Conexoes apenas candidatas' in report
    assert json.loads((w/'state.json').read_text())['status']=='ANALISADO_AGUARDANDO_DECISAO'


def test_main_system_blocks_output_path_escape(tmp_path):
    w,azure,io,master=make_workspace(tmp_path)
    r=exe(SYS,'pid-import','--workspace',w,'--adapter','azure',
      '--source-name',azure.name,'--document','PI','--revision','0',
      '--location','folha 1','--output-name','../../EXTERNO.json')
    assert r.returncode==2
    assert 'Nome de saida invalido' in r.stderr
    assert not (tmp_path/'EXTERNO.json').exists()
