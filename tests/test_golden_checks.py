"""Golden checks da governança v4.6."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v46_schema_exists_and_has_constants():
    schema_path = ROOT / "schemas" / "governance_v4_6.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    symbol = schema["properties"]["symbol_standard"]["properties"]
    assert symbol["external_mm"]["const"] == 12
    assert symbol["aspect_ratio"]["const"] == 1
    assert symbol["name"]["const"] == "AUTOMACAO DM R00-05"
    assert schema["properties"]["critical_signal_roles"]["const"] == [
        "CMD", "RUN", "FAULT", "AVAILABLE"
    ]


def test_li_io_manifest_matches_schema_constants():
    manifest = json.loads((ROOT / "datacenter" / "LI_IO_STANDARD.json").read_text(encoding="utf-8"))
    assert manifest["standard_id"] == "LI_IO_PETROBRAS_AUTOMACAO_V1_0"
    assert manifest["sheet_count_policy"] == "TARGET_DOCUMENT_DRIVEN"
    assert manifest["canonical_sheet_count_is_not_target_constraint"] is True
    assert manifest["layout_lock"] == "TEXT_ONLY"
    assert manifest["binary_storage_policy"] == "PRIVATE_DATACENTER_ONLY"


def test_prompt_and_rule_documents_exist():
    required = [
        "governance/REGRA_DE_OURO.md",
        "governance/PROMPT_MESTRE_AUTOMACAO_v4_6.md",
        "governance/PROMPT_MESTRE_LI_ENTRADA_SAIDA_v1_0.md",
        "governance/LI_IO_STANDARD_v1_0.md",
        "governance/PLUGIN_SECURITY_POLICY.md",
        "memory/MEMORY_POLICY.md",
        "memory/LESSON_LI_IO_MODEL_2026-08-27.md",
    ]
    for relative in required:
        assert (ROOT / relative).is_file(), relative
