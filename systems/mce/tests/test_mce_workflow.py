import importlib.util
import json
import contextlib
import io
from types import SimpleNamespace
import sys
import subprocess
from pathlib import Path

import pytest
from defusedxml.common import EntitiesForbidden
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill, Font

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT/'.agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py'
SPEC = importlib.util.spec_from_file_location('mce_workflow',CLI)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def test_untrusted_worksheet_entities_are_rejected():
    payload = b'<!DOCTYPE x [<!ENTITY unsafe "INJECTED">]><worksheet>&unsafe;</worksheet>'
    with pytest.raises(EntitiesForbidden):
        mod.update_xml_sheet(payload, [], None, {})


def command(*args, ok=True):
    saved=sys.argv
    out,err=io.StringIO(),io.StringIO()
    code=0
    try:
        sys.argv=[str(CLI),*map(str,args)]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                mod.main()
            except SystemExit as e:
                code=int(e.code or 0)
    finally:
        sys.argv=saved
    result=SimpleNamespace(returncode=code,stdout=out.getvalue(),stderr=err.getvalue())
    if ok: assert result.returncode==0,(result.stdout,result.stderr)
    else: assert result.returncode!=0,(result.stdout,result.stderr)
    return result


def dump(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False),encoding='utf-8')
    return path


def fixture(tmp_path,colored=False):
    wb=Workbook();a=wb.active;a.title='CONTROLE';a['A1']='CABECALHO INALTERAVEL'
    b=wb.create_sheet('CAUSAS');b['C2']='ANTIGO';b['D2']='=1+1'
    if colored:b['C2'].fill=PatternFill('solid',fgColor='FF0000')
    c=wb.create_sheet('MCE');c['A4']='ID_CAUSA';c['A5']='C01';c['E5']='?';c['A6']='C02'
    model=tmp_path/'modelo.xlsx';wb.save(model)
    source=tmp_path/'fonte.txt';source.write_text('Projeto PROJETO TESTE e SS-TESTE\nDeteccao H2 documentada\n',encoding='utf-8')
    ws=tmp_path/'projeto';command('init','--workspace',ws,'--master',model,'--sources',source,
          '--classification','MODELO_APROVADO')
    s=mod.load_state(ws)
    analysis={'project':'PROJETO TESTE','ss':'SS-TESTE','summary':'Sistema de teste sintético.',
         'identity_evidence':{
            'project':{'source_name':source.name,'line':1,'verbatim_excerpt':'Projeto PROJETO TESTE e SS-TESTE'},
            'ss':{'source_name':source.name,'line':1,'verbatim_excerpt':'Projeto PROJETO TESTE e SS-TESTE'}},
         'findings':[{'classification':'DOCUMENTADO','text':'Deteccao H2 esta documentada',
             'source_name':source.name,'line':2,'verbatim_excerpt':'Deteccao H2 documentada'}],
         'gaps':['Setpoint nao documentado']}
    command('understand','--workspace',ws,'--analysis',dump(tmp_path/'analise.json',analysis))
    contract=mod.readjson(ws/'contract.json')
    contract.update(model_approved=True,
        matrix_ranges=[{'sheet':'MCE','first_data_row':5,'last_data_row':6}],
        editable_cells={'CAUSAS':['C2'],'MCE':['E5']},
        protected_rows_by_sheet={'CONTROLE':[[1,1]],'CAUSAS':[[1,1]],'MCE':[[1,4]]},
        frozen_sheets=['CONTROLE'])
    mod.writejson(ws/'contract.json',contract)
    approval={'decision':'AUTORIZO_ELABORACAO_MCE','approver':'Aprovador de teste',
              'project':'PROJETO TESTE','ss':'SS-TESTE',
              'source_manifest_sha256':s['source_manifest_sha256']}
    ap=dump(tmp_path/'aprovacao.json',approval)
    ch=[{'sheet':'CAUSAS','cell':'C2','old_text':'ANTIGO','new_text':'Deteccao de H2 confirmada',
        'source_name':source.name,'source_sha256':s['sources'][0]['sha256'],
        'source_location':'linha 2','reference_revision':'R00',
        'verbatim_excerpt':'Deteccao H2 documentada','evidence_status':'DOCUMENTADO'}]
    changefile=dump(tmp_path/'mudancas.json',ch)
    return ws,model,source,ap,changefile,ch


def test_end_to_end_preserves_unedited_ooxml(tmp_path):
    ws,model,source,ap,changes,ch=fixture(tmp_path)
    command('apply','--workspace',ws,'--changes',changes,ok=False)  # sem gate
    command('authorize','--workspace',ws,'--authorization',ap)
    command('apply','--workspace',ws,'--changes',changes)
    command('audit','--workspace',ws)
    base=ws/'base/modelo.xlsx';out=ws/'output/MCE_PRELIMINAR.xlsx'
    assert mod.digest(model)==mod.digest(base)
    w=load_workbook(out)
    assert w['CAUSAS']['C2'].value=='Deteccao de H2 confirmada'
    assert w['CAUSAS']['C2'].fill.fgColor.rgb=='FFD9D9D9'
    assert w['CAUSAS']['D2'].value=='=1+1'
    assert w['CONTROLE']['A1'].value=='CABECALHO INALTERAVEL'
    parts=mod.xml_changes(base,out)
    assert set(parts)=={'xl/styles.xml','xl/worksheets/sheet2.xml'}
    assert mod.readjson(ws/'AUDITORIA_MCE.json')['passed']


@pytest.mark.parametrize('existing_target', ['original', 'baseline', 'regular'])
def test_apply_refuses_existing_output_without_damaging_any_source(tmp_path, existing_target):
    ws, model, _, approval, changes, _ = fixture(tmp_path)
    command('authorize', '--workspace', ws, '--authorization', approval)
    baseline = ws/'base/modelo.xlsx'
    output = ws/'output/MCE_PRELIMINAR.xlsx'
    if existing_target == 'regular':
        output.write_bytes(b'previous private output must remain intact')
    else:
        output.hardlink_to(model if existing_target == 'original' else baseline)
    protected = {path: path.read_bytes() for path in (model, baseline, output)}
    result = command('apply', '--workspace', ws, '--changes', changes, ok=False)
    assert 'destino' in result.stderr.lower() or 'exist' in result.stderr.lower()
    for path, content in protected.items():
        assert path.read_bytes() == content
    assert mod.readjson(ws/'state.json')['status'] == 'AUTORIZADO'


def test_apply_rejects_output_directory_junction(tmp_path):
    ws, model, _, approval, changes, _ = fixture(tmp_path)
    command('authorize', '--workspace', ws, '--authorization', approval)
    outside = tmp_path/'outside'
    outside.mkdir()
    parent = ws/'output'
    parent.rmdir()
    linked = subprocess.run(['cmd', '/c', 'mklink', '/J', str(parent), str(outside)],
                            capture_output=True, check=False)
    if linked.returncode:
        pytest.skip('Windows junction unavailable')
    original = model.read_bytes()
    result = command('apply', '--workspace', ws, '--changes', changes, ok=False)
    assert 'destino inseguro' in result.stderr
    assert model.read_bytes() == original
    assert not list(outside.iterdir())


def test_blocks_unauthorized_cell_and_formula(tmp_path):
    ws,_,_,ap,changes,ch=fixture(tmp_path)
    command('authorize','--workspace',ws,'--authorization',ap)
    ch[0].update(cell='A1',old_text=None)
    dump(changes,ch)
    r=command('apply','--workspace',ws,'--changes',changes,ok=False)
    assert 'nao autorizada' in r.stderr
    ch[0].update(cell='D2',old_text='=1+1')
    mod.writejson(ws/'contract.json',{**mod.readjson(ws/'contract.json'),
          'editable_cells':{'CAUSAS':['D2']}})
    dump(changes,ch)
    r=command('apply','--workspace',ws,'--changes',changes,ok=False)
    assert 'Formula' in r.stderr


def test_blocks_51_items(tmp_path):
    ws,_,_,ap,_,_=fixture(tmp_path)
    c=mod.readjson(ws/'contract.json');c['matrix_ranges'][0]['last_data_row']=55
    mod.writejson(ws/'contract.json',c)
    r=command('authorize','--workspace',ws,'--authorization',ap,ok=False)
    assert '50 itens' in r.stderr


def test_blocks_colored_cell(tmp_path):
    ws,_,_,ap,changes,_=fixture(tmp_path,colored=True)
    command('authorize','--workspace',ws,'--authorization',ap)
    r=command('apply','--workspace',ws,'--changes',changes,ok=False)
    assert 'preenchimento funcional' in r.stderr
    assert not (ws/'output/MCE_PRELIMINAR.xlsx').exists()


def test_blocks_unverified_source_and_unapproved_model(tmp_path):
    ws,_,source,ap,changes,_=fixture(tmp_path)
    c=mod.readjson(ws/'contract.json');c['model_approved']=False
    mod.writejson(ws/'contract.json',c)
    r=command('authorize','--workspace',ws,'--authorization',ap,ok=False)
    assert 'nao homologado' in r.stderr
    source_copy=ws/'sources'/source.name
    source_copy.write_text('ALTERADO',encoding='utf-8')
    r=command('status','--workspace',ws,ok=False)
    assert 'fonte alterada' in r.stderr


def test_audit_rejects_header_mutation(tmp_path):
    ws,_,_,ap,changes,ch=fixture(tmp_path)
    command('authorize','--workspace',ws,'--authorization',ap)
    command('apply','--workspace',ws,'--changes',changes)
    output=ws/'output/MCE_PRELIMINAR.xlsx'
    w=load_workbook(output);w['CONTROLE']['A1']='CORROMPIDO';w.save(output)
    report=mod.audit(ws/'base/modelo.xlsx',output,ch,mod.readjson(ws/'contract.json'))
    assert not report['passed']
    assert any('nao autorizada' in e or 'componentes OOXML' in e for e in report['errors'])


def test_header_blocked_even_when_whitelisted(tmp_path):
    ws,_,source,ap,changes,ch=fixture(tmp_path)
    command('authorize','--workspace',ws,'--authorization',ap)
    c=mod.readjson(ws/'contract.json');c['editable_cells']['CONTROLE']=['A1']
    mod.writejson(ws/'contract.json',c)
    ch[0].update(sheet='CONTROLE',cell='A1',old_text='CABECALHO INALTERAVEL')
    dump(changes,ch)
    r=command('apply','--workspace',ws,'--changes',changes,ok=False)
    assert 'Cabecalho ou aba protegida' in r.stderr


def test_analysis_requires_documented_project_and_ss(tmp_path):
    model=tmp_path/'modelo.xlsx';a=Workbook();a.save(model)
    doc=tmp_path/'fonte.txt';doc.write_text('Sistema sem identificacao formal.',encoding='utf-8')
    ws=tmp_path/'proj';command('init','--workspace',ws,'--master',model,'--sources',doc)
    analysis={'project':'PROJETO INVENTADO','ss':'SS-INVENTADA','summary':'Resumo sintético',
              'findings':[],'gaps':['pendencia']}
    r=command('understand','--workspace',ws,'--analysis',dump(tmp_path/'analysis.json',analysis),ok=False)
    assert 'exige evidencia documental' in r.stderr


def test_unverified_evidence_rejected_at_apply(tmp_path):
    ws,_,_,ap,changes,ch=fixture(tmp_path)
    command('authorize','--workspace',ws,'--authorization',ap)
    ch[0]['verbatim_excerpt']='TRECHO INVENTADO'
    dump(changes,ch)
    r=command('apply','--workspace',ws,'--changes',changes,ok=False)
    assert 'nao confere' in r.stderr



def _synthetic_p09_l50(path):
    from openpyxl.styles import Font, Alignment
    book=Workbook()
    for n in range(1,4):
        ws=book.active if n==1 else book.create_sheet()
        ws.title=f'FOLHA {n}'
        ws.print_area='A1:AR50'
        for r in range(8,51):
            ws[f'H{r}']=(n-1)*43+r-7
            ws[f'H{r}'].font=Font(name='Arial',size=8)
            ws[f'C{r}'].font=Font(name='Arial',size=8)
            ws[f'C{r}'].alignment=Alignment(wrap_text=True)
            ws.row_dimensions[r].height=20
            ws.merge_cells(start_row=r,start_column=6,end_row=r,end_column=7)
        for r in (2,3,4):
            ws.merge_cells(start_row=r,start_column=6,end_row=r,end_column=7)
        for col in range(9,44):
            ws.cell(7,col).value=col-8
            ws.cell(7,col).font=Font(name='Arial',size=8)
            ws.cell(5,col).font=Font(name='Arial',size=8)
            ws.cell(5,col).alignment=Alignment(textRotation=90)
        for coord, value in (('G1','EFEITO'),('H1','Interface'),('A6','CAUSA')):
            ws[coord].value=value
            ws[coord].font=Font(name='Arial',size=10)
        ws['AR50'].font=Font(name='Arial',size=8)
    book.save(path)
    return book


def test_p09_l50_profile_boundaries(tmp_path):
    from openpyxl.styles import Alignment
    model=tmp_path/'synthetic_p09_l50.xlsx'
    book=_synthetic_p09_l50(model)
    c={'layout_profile':mod.P09_L50_PROFILE,
       'matrix_ranges':[{'sheet':f'FOLHA {i}', 'first_data_row':8, 'last_data_row':50} for i in range(1,4)]}
    mod.verify_p09_l50_model(model,c)
    book['FOLHA 2'].print_area='A1:AR57';book.save(model)
    with pytest.raises(ValueError,match='A1:AR50'):mod.verify_p09_l50_model(model,c)
    book['FOLHA 2'].print_area='A1:AR50'
    book['FOLHA 2']['H50']=50;book.save(model)
    with pytest.raises(ValueError,match='H8:H50'):mod.verify_p09_l50_model(model,c)
    book['FOLHA 2']['H50']=86
    book['FOLHA 2']['C51']='OVERFLOW';book.save(model)
    with pytest.raises(ValueError,match='abaixo da linha 50'):mod.verify_p09_l50_model(model,c)
    book['FOLHA 2']['C51']=None
    book['FOLHA 1']['I5'].alignment=Alignment(textRotation=0)
    book.save(model)
    with pytest.raises(ValueError,match='rotacao 90'):mod.verify_p09_l50_model(model,c)

def test_p09_l50_no_notes_policy(tmp_path):
    from openpyxl.comments import Comment
    model = tmp_path/'synthetic_clean_l50.xlsx'
    book = _synthetic_p09_l50(model)
    c = {'layout_profile':mod.P09_L50_PROFILE, 'annotation_policy':'EXTERNAL_ONLY',
         'matrix_ranges':[{'sheet':f'FOLHA {i}', 'first_data_row':8, 'last_data_row':50} for i in range(1,4)]}
    mod.verify_p09_l50_model(model, c)
    book['FOLHA 1']['AR20']='NOTA'
    book.save(model)
    with pytest.raises(ValueError, match='notas na coluna AR'): mod.verify_p09_l50_model(model, c)
    book['FOLHA 1']['AR20']=None
    book['FOLHA 1']['C12'].comment=Comment('temporary','tester')
    book.save(model)
    with pytest.raises(ValueError, match='comentarios nas celulas'): mod.verify_p09_l50_model(model, c)
    book['FOLHA 1']['C12'].comment=None
    book.save(model)
    mod.verify_p09_l50_model(model, c)


def test_p09_l50_progressive_height_policy_and_width_profile(tmp_path):
    """DEC-MCE-034: 3 linhas=40 pt, 4 linhas=50 pt, sem tolerar 25/410 pt."""
    assert [mod.p09_l50_height_for_lines(n) for n in (1, 2, 3, 4, 5)] == [20, 30, 40, 50, 60]
    for bad in (0, -1, 1.5, True, 40):
        with pytest.raises(ValueError, match='linhas visuais|400 pt'):
            mod.p09_l50_height_for_lines(bad)
    for good in (20, 30.0, 40, 50, 400):
        assert mod.p09_l50_valid_row_height(good)
    for bad in (None, False, 10, 25, 35, 409.5, 410):
        assert not mod.p09_l50_valid_row_height(bad)

    model = tmp_path / 'p09_l50_progressive.xlsx'
    book = _synthetic_p09_l50(model)
    for ws in book:
        for col, value in mod.P09_L50_COLUMN_WIDTHS.items():
            ws.column_dimensions[col].width = value
        ws.row_dimensions[8].height = 40
        ws.row_dimensions[9].height = 50
    contract = {'layout_profile': mod.P09_L50_PROFILE,
                'column_width_profile': mod.P09_L50_WIDTH_PROFILE,
                'matrix_ranges':[{'sheet':f'FOLHA {i}', 'first_data_row':8, 'last_data_row':50} for i in range(1,4)]}
    book.save(model)
    mod.verify_p09_l50_model(model, contract)
    book['FOLHA 2'].row_dimensions[8].height = 25
    book.save(model)
    with pytest.raises(ValueError,match='20..400'):mod.verify_p09_l50_model(model, contract)
    book['FOLHA 2'].row_dimensions[8].height = 40
    book['FOLHA 2'].column_dimensions['C'].width = 55
    book.save(model)
    with pytest.raises(ValueError,match='largura P09 L50'):mod.verify_p09_l50_model(model,contract)


def test_p09_l50_all_columns_width_two_contract(tmp_path):
    """DEC-MCE-037: exige largura 2 em todas A:AR quando explicitamente contratado."""
    from openpyxl.utils import get_column_letter
    path=tmp_path/'l50_all_2.xlsx'
    wb=_synthetic_p09_l50(path)
    for ws in wb:
        for i in range(1,45): ws.column_dimensions[get_column_letter(i)].width=2.0
    wb.save(path)
    c={'layout_profile':mod.P09_L50_PROFILE,'column_width_profile':mod.P09_L50_ALL_COLUMNS_2,
       'matrix_ranges':[{'sheet':f'FOLHA {i}', 'first_data_row':8,'last_data_row':50} for i in range(1,4)]}
    mod.verify_p09_l50_model(path,c)
    wb['FOLHA 2'].column_dimensions['C'].width=56.0
    wb.save(path)
    with pytest.raises(ValueError,match='largura A:AR diferente de 2'):
        mod.verify_p09_l50_model(path,c)
    c.pop('column_width_profile')
    mod.verify_p09_l50_model(path,c)


def test_p09_l50_g_ar_two_with_effect_link_gate(tmp_path):
    """DEC-MCE-038: every populated cause must have a sourced effect heading and an X."""
    from openpyxl.utils import get_column_letter
    path=tmp_path/'g_ar_effects.xlsx'
    wb=_synthetic_p09_l50(path)
    for extra in list(wb.worksheets[1:]): wb.remove(extra)
    ws=wb.active
    for i in range(7,45): ws.column_dimensions[get_column_letter(i)].width=2.0
    ws['C8']='Detector H2 10%'
    ws['I5']='Alarme H2 local'
    ws['I8']='X'
    ws['I8'].font=Font(name='Arial',size=8)
    for j in range(9,51): ws[f'H{j}']=None
    wb.save(path)
    c={'layout_profile':mod.P09_L50_PROFILE,
       'column_width_profile':mod.P09_L50_G_AR_2,
       'require_effect_per_cause':True,
       'matrix_ranges':[{'sheet':'FOLHA 1','first_data_row':8,'last_data_row':50}]}
    mod.verify_p09_l50_model(path,c)
    ws['I8']=None;wb.save(path)
    with pytest.raises(ValueError,match='causa sem efeito/X'):
        mod.verify_p09_l50_model(path,c)
    ws['I8']='X';ws['I5']=None;wb.save(path)
    with pytest.raises(ValueError,match='X sem titulo'):
        mod.verify_p09_l50_model(path,c)
    ws['I5']='Alarme H2 local';ws.column_dimensions['G'].width=3.0;wb.save(path)
    with pytest.raises(ValueError,match='largura G:AR diferente de 2'):
        mod.verify_p09_l50_model(path,c)
    ws.column_dimensions['G'].width=2.0
    ws['C9']='Interface sem efeito'
    ws['H9']=2
    wb.save(path)
    with pytest.raises(ValueError,match='causa sem efeito/X'):
        mod.verify_p09_l50_model(path,c)



def test_p09_l50_no_overlapping_two_width_ranges(tmp_path):
    """DEC-MCE-039 regression: value=2 alone cannot hide OOXML overlapping spans."""
    from openpyxl.utils import get_column_letter
    model=tmp_path/'p09_l50_G_AR_2_exact.xlsx'
    wb=_synthetic_p09_l50(model)
    for ws in wb:
        for col in range(7,45):
            ws.column_dimensions[get_column_letter(col)].width=2.0
    wb.save(model)
    contract={'layout_profile':mod.P09_L50_PROFILE,'column_width_profile':mod.P09_L50_G_AR_2,
      'matrix_ranges':[{'sheet':f'FOLHA {n}','first_data_row':8,'last_data_row':50} for n in range(1,4)]}
    mod.verify_p09_l50_model(model,contract)
    wb['FOLHA 1'].column_dimensions['I'].min=9
    wb['FOLHA 1'].column_dimensions['I'].max=38
    wb.save(model)
    with pytest.raises(ValueError,match='faixas de colunas sobrepostas'):
        mod.verify_p09_l50_model(model,contract)
    wb['FOLHA 1'].column_dimensions['I'].min=9
    wb['FOLHA 1'].column_dimensions['I'].max=9
    wb['FOLHA 1'].column_dimensions['G'].width=1.29
    wb.save(model)
    with pytest.raises(ValueError,match='largura G:AR diferente de 2'):
        mod.verify_p09_l50_model(model,contract)
    wb['FOLHA 1'].column_dimensions['G'].width=2.0
    wb.save(model)
    mod.verify_p09_l50_model(model,contract)


def test_p09_l50_ui_two_requires_ooxml_2p7109375_and_unique_spans(tmp_path):
    """DEC-MCE-040: raw width 2 displays 1.29, stored 2.7109375 displays 2.00."""
    from openpyxl.utils import get_column_letter
    assert mod.p09_l50_gui_width_from_ooxml(2.0) == 1.29
    assert mod.p09_l50_gui_width_from_ooxml(2.7109375) == 2.0
    path=tmp_path/'display_width_2.xlsx'
    wb=_synthetic_p09_l50(path)
    for ws in wb:
        for col in range(7,45):
            ws.column_dimensions[get_column_letter(col)].width=2.7109375
    wb.save(path)
    contract={'layout_profile':mod.P09_L50_PROFILE,
        'column_width_profile':mod.P09_L50_G_AR_DISPLAY_2,
        'matrix_ranges':[{'sheet':f'FOLHA {n}','first_data_row':8,'last_data_row':50} for n in range(1,4)]}
    mod.verify_p09_l50_model(path,contract)
    wb['FOLHA 1'].column_dimensions['G'].width=2.0
    wb.save(path)
    with pytest.raises(ValueError,match='largura EXIBIDA G:AR diferente de 2'):
        mod.verify_p09_l50_model(path,contract)
    wb['FOLHA 1'].column_dimensions['G'].width=2.7109375
    wb['FOLHA 2'].column_dimensions['I'].max=38
    wb.save(path)
    with pytest.raises(ValueError,match='faixas de colunas sobrepostas'):
        mod.verify_p09_l50_model(path,contract)


def test_p09_l50_g_aq_display_two_ar_display_ninety_six(tmp_path):
    """DEC-MCE-041: AR is 96.00 in GUI, not width 2; G:AQ remain GUI 2.00."""
    from openpyxl.utils import get_column_letter
    assert mod.p09_l50_gui_width_from_ooxml(96.7109375) == 96.0
    book=_synthetic_p09_l50(tmp_path/'ar96.xlsx')
    for ws in book:
        for i in range(7,44): ws.column_dimensions[get_column_letter(i)].width=2.7109375
        ws.column_dimensions['AR'].width=96.7109375
    path=tmp_path/'ar96.xlsx';book.save(path)
    contract={'layout_profile':mod.P09_L50_PROFILE,
       'column_width_profile':mod.P09_L50_G_AQ_DISPLAY_2_AR_96,
       'matrix_ranges':[{'sheet':f'FOLHA {n}', 'first_data_row':8,'last_data_row':50} for n in range(1,4)]}
    mod.verify_p09_l50_model(path,contract)
    book['FOLHA 1'].column_dimensions['AR'].width=2.7109375
    book.save(path)
    with pytest.raises(ValueError,match='largura EXIBIDA AR diferente de 96'):
        mod.verify_p09_l50_model(path,contract)
    book['FOLHA 1'].column_dimensions['AR'].width=96.7109375
    book['FOLHA 2'].column_dimensions['AQ'].width=96.7109375
    book.save(path)
    with pytest.raises(ValueError,match='largura EXIBIDA G:AR diferente de 2'):
        mod.verify_p09_l50_model(path,contract)


def test_propose_contract_does_not_grant_approval(tmp_path):
    """DEC-MCE-075: proposal is useful, but cannot approve engineering."""
    model=tmp_path/'synthetic_proposal.xlsx'
    book=_synthetic_p09_l50(model)
    book['FOLHA 1']['C8']='Synthetic cause'
    book['FOLHA 1']['AR8'].font=Font(name='Arial',size=8)
    book['FOLHA 1']['D8']='10%'
    book['FOLHA 1']['I8']='X'
    book.save(model)
    ws=tmp_path/'ws'
    command('init','--workspace',ws,'--master',model)
    original_sha=mod.digest(ws/'base/modelo.xlsx')
    blocked_contract=(ws/'contract.json').read_bytes()
    original_state=(ws/'state.json').read_bytes()
    command('propose-contract','--workspace',ws,
            '--annotation-policy','IN_MATRIX','--sp-policy','UNUSED')
    proposal=mod.readjson(ws/'contract.proposed.json')
    assert proposal['model_approved'] is False
    assert proposal['schema']=='mce.contract.candidate.v1'
    assert proposal['coverage']['causes']==129
    assert proposal['coverage']['existing_x_unverified']==1
    assert 'C8' in proposal['editable_cells']['FOLHA 1']
    assert 'AR8' in proposal['editable_cells']['FOLHA 1']
    assert 'D8' in proposal['editable_cells']['FOLHA 1']
    assert 'I8' not in proposal['editable_cells']['FOLHA 1']
    assert proposal['protected_rows_by_sheet']['FOLHA 1']==[[1,7]]
    assert (ws/'contract.json').read_bytes()==blocked_contract
    assert (ws/'state.json').read_bytes()==original_state
    assert mod.digest(ws/'base/modelo.xlsx')==original_sha
    command('propose-contract','--workspace',ws,
            '--annotation-policy','IN_MATRIX','--sp-policy','UNUSED',ok=False)
    r=command('apply','--workspace',ws,'--changes',dump(tmp_path/'changes.json',[]),ok=False)
    assert 'autorizacao' in r.stderr


def test_propose_contract_respects_annotation_and_sp_policies(tmp_path):
    model=tmp_path/'synthetic_external.xlsx'
    book=_synthetic_p09_l50(model)
    book['FOLHA 1']['AR8'].font=Font(name='Arial',size=8)
    book['FOLHA 1']['D8']='10%'
    book.save(model)
    ws=tmp_path/'ws'
    command('init','--workspace',ws,'--master',model)
    command('propose-contract','--workspace',ws,
            '--annotation-policy','EXTERNAL_ONLY','--sp-policy','DOCUMENTED')
    proposal=mod.readjson(ws/'contract.proposed.json')
    assert 'AR8' not in proposal['editable_cells']['FOLHA 1']
    assert 'D8' not in proposal['editable_cells']['FOLHA 1']
    assert proposal['coverage']['sp_legacy_for_review']==[]


def test_propose_contract_rejects_generic_workbook(tmp_path):
    model=tmp_path/'generic.xlsx'
    Workbook().save(model)
    ws=tmp_path/'ws'
    command('init','--workspace',ws,'--master',model)
    r=command('propose-contract','--workspace',ws,
              '--annotation-policy','IN_MATRIX','--sp-policy','UNUSED',ok=False)
    assert 'FOLHA N' in r.stderr
    assert not (ws/'contract.proposed.json').exists()
