from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
PARTITION = ROOT / "document-evaluation"


def test_partition_manifest_exists_and_is_extraction_ready():
    data = json.loads((PARTITION / "system-manifest.json").read_text(encoding="utf-8"))
    assert data["system_id"] == "DOCUMENT_EVALUATION_SYSTEM_V0_1"
    assert data["extraction_ready"] is True


def test_partition_has_required_product_areas():
    for path in (
        "agent/AGENT.md",
        "config/system.json",
        "datacenter/README.md",
        "datasheet/README.md",
        "governance/PRINCIPLES.md",
        "pipeline/run_evaluation.py",
        "ROADMAP.md",
    ):
        assert (PARTITION / path).exists(), path
