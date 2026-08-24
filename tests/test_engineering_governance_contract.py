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


def test_prompt_preserves_engineering_pipeline_contract():
    text = Path('governance/PROMPT_MESTRE_AUTOMACAO_v4_4.md').read_text(encoding='utf-8')
    required = [
        'CMD, RUN, FAULT e AVAILABLE',
        'Simbologia e 12 mm',
        'Intertravamentos',
        'Redundância A/B',
        'Informação sem evidência permanece TBD/PROPOSTO',
    ]
    for item in required:
        assert item in text


def test_memory_policy_keeps_never_forget_contract():
    text = Path('memory/MEMORY_POLICY.md').read_text(encoding='utf-8')
    assert 'memória da ocorrência' in text
    assert 'regra de prevenção' in text
    assert 'teste automatizado de regressão' in text
    assert '24 horas' not in text
    assert '30 dias' not in text


def test_governance_schema_is_domain_correct():
    schema = json.loads(Path('schemas/governance_v4_4.schema.json').read_text(encoding='utf-8'))
    symbol = schema['properties']['symbol_standard']['properties']
    assert symbol['name']['const'] == 'AUTOMACAO DM R00-05'
    assert symbol['external_mm']['const'] == 12
    assert symbol['aspect_ratio']['const'] == 1
    assert symbol['families']['const'] == ['DISCRETE', 'SHARED_DISPLAY', 'COMPUTER', 'PLC']
    assert schema['properties']['critical_signal_roles']['const'] == ['CMD', 'RUN', 'FAULT', 'AVAILABLE']


def test_schema_does_not_use_invalid_object_const_for_numeric_values():
    schema = json.loads(Path('schemas/governance_v4_4.schema.json').read_text(encoding='utf-8'))
    symbol = schema['properties']['symbol_standard']['properties']
    assert symbol['external_mm'].get('type') != 'object'
    assert symbol['aspect_ratio'].get('type') != 'object'
