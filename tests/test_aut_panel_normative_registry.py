from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]

def _load(path):
    return yaml.safe_load((ROOT/path).read_text(encoding="utf-8"))

def test_normative_registry_has_required_core_references_and_evidence_fields():
    reg=_load("datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml")
    assert reg["registry_id"]=="AUT-PANEL-NORMATIVE-REFERENCES-V1"
    assert reg["status"]=="CONTROLLED_ACTIVE"
    assert reg["reverify_before_release"] is True
    refs={x["reference"]:x for x in reg["standards"]}
    required={
        "ABNT NBR 5410:2004 Versao Corrigida:2008",
        "NR-10",
        "NR-12",
        "IEC 61439-1:2020",
        "IEC 61439-2:2020",
        "IEC 60204-1:2016+AMD1:2021",
        "IEC 60529:1989+AMD1:1999+AMD2:2013",
        "IEC 62208:2023",
        "IEC 60445:2021+AMD1:2026",
        "IEC 61082-1:2014",
        "IEC 81346-1:2022",
        "IEC 60947-2:2024",
        "IEC 60947-3:2020+AMD1:2025",
        "IEC 60947-4-1:2023",
        "IEC 60947-5-1:2024",
        "IEC 60947-7-1:2025",
        "IEC 61643-11:2025",
        "IEC 60269-1:2024",
        "IEC 61131-2:2017",
        "IEC 61000-6-2:2016",
        "IEC 61000-6-4:2018",
        "IEC 61800-3:2022",
        "IEC 62040-1:2017+AMD1:2021+AMD2:2022",
        "IEC 61158-1:2023",
        "IEC 62443-3-3:2013",
        "ISO 13849-1:2023",
        "IEC 62061:2021",
    }
    assert required.issubset(refs)
    for ref in refs.values():
        for key in ("id","reference","title","publisher","jurisdiction","category","applicability","use_in_elaboration","source_status","official_url","verified_at"):
            assert key in ref
        assert ref["official_url"].startswith("https://")

def test_normative_memory_and_canonical_registries_are_linked():
    mem=_load("memory/AUT_PANEL_NORMATIVE_MEMORY.yaml")
    dc=_load("datacenter/datacenter.yaml")
    ds=_load("datasheet/datasheet.yaml")
    pipe=_load("pipeline/pipeline.yaml")
    ctx=_load("context/AUT_PANEL_CONVERSATION_MEMORY.yaml")
    expected="datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml"
    assert mem["registry_path"]==expected
    assert dc["canonical_sources"]["normative_registry"]==expected
    assert ds["production_contract"]["normative_registry"]==expected
    assert pipe["contracts"]["normative_registry"]==expected
    assert ctx["immutable_contract"]["normative_registry"]==expected
    bootstrap=next(x for x in pipe["sequence"] if x["id"]=="BOOTSTRAP_CONTEXT")
    assert "normative_registry_loaded" in bootstrap["gate"]

def test_normative_policy_is_fail_closed_and_does_not_copy_standard_text():
    reg=_load("datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml")
    assert reg["copyright_policy"]["store_metadata_not_normative_text"] is True
    assert reg["applicability_policy"]["unverified_edition_status"]=="HOLD"
    assert reg["applicability_policy"]["conflicting_requirements_status"]=="HOLD"
    assert reg["applicability_policy"]["project_specific_requirement_precedence"] is True


def test_conversation_contract_bootstrap_returns_normative_ids():
    import importlib.util
    script=ROOT/"pipeline/conversation_contract.py"
    spec=importlib.util.spec_from_file_location("conversation_contract_norms",script)
    mod=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    result=mod.validate_contract(ROOT)
    assert result["normative_registry_id"]=="AUT-PANEL-NORMATIVE-REFERENCES-V1"
    assert result["normative_memory_id"]=="AUT-PANEL-NORMATIVE-MEMORY-V1"
