from pathlib import Path
import json

from pipeline.aut_panel_router import route_intent
from pipeline.context_manifest import build_context_manifest, sha256_object
from pipeline.aut_panel_handoff import build_handoff, validate_handoff

ROOT = Path(__file__).resolve().parents[1]


def test_router_known_intents_are_deterministic():
    decision = route_intent("layout do PN-AUT-01")
    assert decision.agent == "LAYOUT_OPTIMIZER"
    assert decision.mode == "DETERMINISTIC"

    decision = route_intent("programacao CLP e matriz I/O")
    assert decision.agent == "AUTOMATION_IO"
    assert decision.mode == "DETERMINISTIC"


def test_router_ambiguity_never_becomes_write_route():
    decision = route_intent("continuar trabalho")
    assert decision.agent == "ORCHESTRATOR"
    assert decision.mode == "ML_ROUTE_HINT"


def test_router_does_not_match_short_alias_inside_other_words():
    decision = route_intent("validacao documental")
    assert decision.agent == "ORCHESTRATOR"
    assert decision.mode == "ML_ROUTE_HINT"


def test_context_manifest_is_panel_scoped_and_content_addressed():
    manifest = build_context_manifest(
        ROOT,
        task_id="TEST-CTX-001",
        intent="layout",
        panel_id="PN-AUT-01",
        agent_version="test-v1",
    )
    assert manifest["panel_id"] == "PN-AUT-01"
    assert manifest["agent"] == "LAYOUT_OPTIMIZER"
    assert manifest["memory_scope"]["panel_scoped"] is True
    assert len(manifest["cache"]["key"]) == 64

    material = manifest["cache"]["material"]
    assert manifest["cache"]["key"] == sha256_object(material)
    assert any(x["path"] == "li/PN-AUT-01_LI.json" for x in manifest["canonical_inputs"])


def test_context_manifest_uses_missing_bom_sentinel_without_hiding_it():
    manifest = build_context_manifest(
        ROOT,
        task_id="TEST-CTX-002",
        intent="automation_io",
        panel_id="PN-AUT-02",
        agent_version="test-v1",
    )
    if manifest["cache"]["material"]["bom_hash"] == "MISSING":
        ids = {x["hold_id"] for x in manifest["holds"]}
        assert "HOLD-CACHE-BOM-MISSING" in ids


def test_handoff_contains_no_chain_of_thought_and_validates():
    payload = build_handoff(
        task_id="TEST-HO-001",
        from_agent="AUTOMATION_IO",
        to_agent="QA",
        panel="PN-AUT-01",
        revision="R02",
        status="PASS",
        outputs=[{"path": "example.json", "sha256": "abc"}],
        validated_facts=[{"fact": "IHM on door"}],
        source_refs=[{"path": "datasheet/datasheet.yaml"}],
        holds=[],
        next_action="Run QA deterministic gates.",
    )
    assert payload["chain_of_thought_included"] is False
    validate_handoff(payload)


def test_handoff_schema_exists_and_forbids_chain_of_thought():
    schema = json.loads((ROOT / "schemas" / "aut_panel_handoff_v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["chain_of_thought_included"]["const"] is False
