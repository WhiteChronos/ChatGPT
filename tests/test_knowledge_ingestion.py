from __future__ import annotations

from copy import deepcopy

import pytest

from pipeline.knowledge_ingestion import (
    build_batch,
    load_registry,
    merge_review_queue,
    normalize_record,
    stable_ingestion_id,
    validate_registry,
)


def active_test_registry() -> dict:
    registry = load_registry()
    registry = deepcopy(registry)
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


def test_stable_ingestion_id_is_deterministic():
    payload = {"term": "PT", "definition_pt": "Transmissor de pressão"}
    first = stable_ingestion_id("SRC", "glossary_entry", "PT", payload)
    second = stable_ingestion_id("SRC", "glossary_entry", "PT", payload)
    assert first == second


def test_ingested_record_always_requires_review():
    registry = active_test_registry()
    source = registry["sources"][0]
    record = normalize_record(
        {
            "entity_type": "tag",
            "external_id": "PT-101",
            "payload": {"tag": "PT-101"},
            "provenance": {"row": 2},
        },
        source,
    )
    assert record["review_status"] == "REVIEW_REQUIRED"
    assert record["auto_promoted"] is False
    assert record["provenance"]["source_id"] == "TEST_FIXTURE"


def test_duplicate_record_is_blocked():
    registry = active_test_registry()
    record = {
        "entity_type": "tag",
        "external_id": "PT-101",
        "payload": {"tag": "PT-101"},
        "provenance": {"row": 2},
    }
    with pytest.raises(ValueError, match="duplicados"):
        build_batch("TEST_FIXTURE", [record, record], registry, created_at="2026-08-28T00:00:00+00:00")


def test_disabled_source_is_blocked():
    registry = load_registry()
    source_id = registry["sources"][0]["source_id"]
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
    queue = {
        "schema_version": "1.0",
        "queue_id": "DEKS-INGESTION-REVIEW",
        "auto_approval": False,
        "allowed_statuses": ["REVIEW_REQUIRED", "APPROVED", "REJECTED"],
        "items": [],
    }
    merged = merge_review_queue(queue, batch)
    assert merged["auto_approval"] is False
    assert merged["items"][0]["review_status"] == "REVIEW_REQUIRED"
