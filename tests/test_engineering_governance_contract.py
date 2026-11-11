from pathlib import Path
import json


def test_regra_de_ouro_preserves_engineering_domain():
    text = Path('governance/REGRA_DE_OURO.md').read_text(encoding='utf-8')
    required = [
        'AUTOMAÇÃO DM R00-05',
        '12 mm',
        'CMD != RUN',
        'AVAILABLE é estado independente',
        'MAN/AUTO != LOCAL/REMOTO',
        'Alarme não implica trip',
    ]
    for item in required:
        assert item in text


def test_prompt_v46_preserves_engineering_and_document_contracts():
    text = Path('governance/PROMPT_MESTRE_AUTOMACAO_v4_6.md').read_text(encoding='utf-8')
    required = [
        'CMD, RUN, FAULT e AVAILABLE',
        'Intertravamentos',
        'Informação sem evidência permanece TBD/PROPOSTO',
        'quantidade de abas nunca deve ser copiada',
        'LI_IO_PETROBRAS_AUTOMACAO_V1_0',
        'Data Center',
        'Data Sheet',
    ]
    for item in required:
        assert item in text


def test_li_io_standard_has_target_driven_sheet_count_and_note_placement():
    text = Path('governance/LI_IO_STANDARD_v1_0.md').read_text(encoding='utf-8')
    assert 'TARGET_DOCUMENT_DRIVEN' in text
    assert 'Nunca copiar a quantidade de abas' in text
    assert 'Não inserir linha genérica “NOTA”' in text
    assert 'BLOCK_ON_ANY_FAILURE' in text


def test_memory_policy_keeps_never_forget_contract():
    text = Path('memory/MEMORY_POLICY.md').read_text(encoding='utf-8')
    assert 'memória da ocorrência' in text
    assert 'regra de prevenção' in text
    assert 'teste automatizado de regressão' in text
    assert '24 horas' not in text
    assert '30 dias' not in text


def test_governance_schema_is_domain_correct():
    schema = json.loads(Path('schemas/governance_v4_6.schema.json').read_text(encoding='utf-8'))
    symbol = schema['properties']['symbol_standard']['properties']
    assert symbol['name']['const'] == 'AUTOMACAO DM R00-05'
    assert symbol['external_mm']['const'] == 12
    assert symbol['aspect_ratio']['const'] == 1
    assert symbol['families']['const'] == ['DISCRETE', 'SHARED_DISPLAY', 'COMPUTER', 'PLC']
    assert schema['properties']['critical_signal_roles']['const'] == ['CMD', 'RUN', 'FAULT', 'AVAILABLE']
    assert schema['properties']['document_policy']['properties']['sheet_count_source']['const'] == 'TARGET_DOCUMENT'
