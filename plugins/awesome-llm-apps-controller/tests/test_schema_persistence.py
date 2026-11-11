from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def test_catalog_schema_is_persistent_repository_source():
    schema = REPO / "registry" / "awesome-llm-apps" / "catalog.schema.json"
    assert schema.is_file(), (
        "catalog.schema.json is a source-controlled input to synchronization "
        "and must not be deleted by a generated upstream sync"
    )
