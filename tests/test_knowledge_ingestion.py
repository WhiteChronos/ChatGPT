from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from pipeline.knowledge_ingestion import (
    BATCH_SCHEMA,
    build_batch,
    load_registry,
    merge_review_queue,
    normalize_record,
    stable_ingestion_id,
    validate_registry,
    validate_with_schema,
)

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "ingestion" / "staging"
QUEUE = ROOT / "datacenter" / "INGESTION_REVIEW_QUEUE.json"
PLAN = ROOT / "datacenter" / "INGESTION_PIPELINE_PLAN.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def active_test_registry() -> dict:
    registry = deepcopy(load_registry())
    source = registry["sources"][0]
    source["source_id"] = "TEST_FIXTURE"
    source["name"] = "Fixture controlada"
    source["source_type"] = "test_fixture"
    source["authority_tier"] = 7
    source["default_evidence_class"] = "E0_NO_EVIDENCE"
    source["allowed_formats"] = ["json", "csv"]
    source["allowed_entity_types"] = ["glossary_entry", "tag", "symbol", "pid_object", "instrument_index_item", "io_item", "cause_effect", "datasheet", "source"]
    source["enabled"] = True
    source["status"] = "ACTIVE"
    registry["sources"] = [source]
    return registry


def test_production_registry_is_schema_valid():
    assert validate_registry(load_registry()) == []


def test_production_registry_activates_only_evidenced_sources():
    registry = load_registry()
    active = {item["source_id"] for item in registry["sources"] if item["enabled"] and item["status"] == "ACTIVE"}
    pending = {item["source_id"] for item in registry["sources"] if not item["enabled"]}
    assert active == {"PROJECT_GLOSSARY_REV4_2", "AUTOMACAO_DM_R00_05", "PROJECT_PID"}
    assert {"PROJECT_INSTRUMENT_INDEX", "PROJECT_IO_LIST", "PROJECT_CAUSE_EFFECT", "PROJECT_DATASHEETS"} <= pending


def test_stable_ingestion_id_is_deterministic():
    payload = {"term": "PT", "definition_pt": "Transmissor de pressão"}
    first = stable_ingestion_id("SRC", "glossary_entry", "PT", payload)
    second = stable_ingestion_id("SRC", "glossary_entry", "PT", payload)
    assert first == second


def test_ingested_record_always_requires_review():
    registry = active_test_registry()
    source = registry["sources"][0]
    record = normalize_record(
        {"entity_type": "tag", "external_id": "PT-101", "payload": {"tag": "PT-101"}, "provenance": {"row": 2}},
        source,
    )
    assert record["review_status"] == "REVIEW_REQUIRED"
    assert record["auto_promoted"] is False
    assert record["provenance"]["source_id"] == "TEST_FIXTURE"


def test_duplicate_record_is_blocked():
    registry = active_test_registry()
    record = {"entity_type": "tag", "external_id": "PT-101", "payload": {"tag": "PT-101"}, "provenance": {"row": 2}}
    with pytest.raises(ValueError, match="duplicados"):
        build_batch("TEST_FIXTURE", [record, record], registry, created_at="2026-08-28T00:00:00+00:00")


def test_disabled_source_is_blocked():
    registry = load_registry()
    source_id = next(item["source_id"] for item in registry["sources"] if not item["enabled"])
    with pytest.raises(ValueError, match="não habilitada"):
        build_batch(
            source_id,
            [{"entity_type": "tag", "external_id": "PT-101", "payload": {"tag": "PT-101"}}],
            registry,
            created_at="2026-08-28T00:00:00+00:00",
        )


def test_review_queue_never_auto_approves():
    registry = active_test_registry()
    batch = build_batch(
        "TEST_FIXTURE",
        [{"entity_type": "tag", "external_id": "PT-101", "payload": {"tag": "PT-101"}}],
        registry,
        created_at="2026-08-28T00:00:00+00:00",
    )
    queue = {"schema_version": "1.0", "queue_id": "DEKS-INGESTION-REVIEW", "auto_approval": False, "allowed_statuses": ["REVIEW_REQUIRED", "APPROVED", "REJECTED"], "items": []}
    merged = merge_review_queue(queue, batch)
    assert merged["auto_approval"] is False
    assert merged["items"][0]["review_status"] == "REVIEW_REQUIRED"


def test_committed_staging_batches_are_schema_valid_and_review_only():
    batches = [load_json(path) for path in sorted(STAGING.glob("BATCH-*.json"))]
    assert len(batches) == 3
    assert sum(len(batch["records"]) for batch in batches) == 40
    for batch in batches:
        assert validate_with_schema(batch, BATCH_SCHEMA) == []
        for record in batch["records"]:
            assert record["review_status"] == "REVIEW_REQUIRED"
            assert record["auto_promoted"] is False
            assert record["provenance"]["source_id"] == batch["source_id"]


def test_review_queue_matches_all_staged_records_without_approval():
    queue = load_json(QUEUE)
    assert queue["auto_approval"] is False
    assert len(queue["items"]) == 40
    assert {item["review_status"] for item in queue["items"]} == {"REVIEW_REQUIRED"}
    staged_ids = {
        record["ingestion_id"]
        for path in STAGING.glob("BATCH-*.json")
        for record in load_json(path)["records"]
    }
    assert {item["ingestion_id"] for item in queue["items"]} == staged_ids


def test_automacao_dm_matrix_has_16_cells_and_no_dimension_inference():
    batch = load_json(STAGING / "BATCH-c1bb0237fbc5ef53.json")
    symbols = [record for record in batch["records"] if record["entity_type"] == "symbol"]
    assert len(symbols) == 16
    explicit = [record for record in symbols if record["payload"]["explicit_dimension_mm"] is not None]
    assert len(explicit) == 1
    assert explicit[0]["external_id"] == "DM-INSTRUMENTO_DISCRETO-CAMPO"
    assert explicit[0]["payload"]["explicit_dimension_mm"] == 12


def test_project_drawing_ingestion_does_not_assume_pid_equivalence():
    batch = load_json(STAGING / "BATCH-9e6d8528ff88108b.json")
    source = next(record for record in batch["records"] if record["entity_type"] == "source")
    assert source["payload"]["pid_equivalence"] == "not_assumed"
    objects = {record["external_id"] for record in batch["records"] if record["entity_type"] == "pid_object"}
    assert objects == {"AC-0244.0002", "AC-0244.0003"}


def test_downstream_unavailable_sources_remain_pending():
    plan = load_json(PLAN)
    pending_stages = {item["stage"] for item in plan["sequence"] if item["state"] == "PENDING_SOURCE_FILE"}
    assert pending_stages == {"Instrument Index / I/O", "C&E", "datasheets"}
    assert plan["guards"]["canonical_glossary_modified_by_this_sequence"] is False


def test_ingestion_engine_has_no_canonical_glossary_write_target():
    engine = (ROOT / "pipeline" / "knowledge_ingestion.py").read_text(encoding="utf-8")
    assert "GLOSSARY_MASTER.json" not in engine
