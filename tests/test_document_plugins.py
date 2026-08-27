import json
from pathlib import Path

from pipeline.audit_document_plugins import load_registry


def test_registry_blocks_auto_install():
    registry = load_registry("plugins/document_tooling_registry.json")
    assert registry["policy"]["auto_install_forbidden"] is True
    assert all(entry["status"] for entry in registry["repositories"])


def test_registry_contains_core_document_tools():
    registry = load_registry("plugins/document_tooling_registry.json")
    names = {entry["full_name"] for entry in registry["repositories"]}
    assert "python-openxml/python-docx" in names
    assert "LibreOffice/core" in names
    assert "microsoft/markitdown" in names
    assert "docling-project/docling" in names


def test_datacenter_manifest_is_active_and_target_driven():
    data = json.loads(Path("datacenter/LI_IO_STANDARD.json").read_text(encoding="utf-8"))
    assert data["status"] == "ACTIVE"
    assert data["sheet_count_policy"] == "TARGET_DOCUMENT_DRIVEN"
    assert data["layout_lock"] == "TEXT_ONLY"
    assert len(data["canonical_sha256"]) == 64
