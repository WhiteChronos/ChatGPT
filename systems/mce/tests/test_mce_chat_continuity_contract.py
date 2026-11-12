"""Public process metadata restart gate. No engineering files or private hashes."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "datacenter" / "CHAT_CONTINUITY_CONTRACT.json"
RESTART = ROOT / "docs" / "RETOMADA_ENTRE_CHATS.md"
MEMORY = ROOT / "spec" / "memoria.md"
WORKFLOW = ROOT / "docs" / "MCE_CHAT_CONTINUITY.md"


def test_mce_cross_chat_policy_references_real_workflow():
    obj = json.loads(POLICY.read_text(encoding="utf-8"))
    assert obj["schema"] == "mce.chat-continuity.v1"
    assert obj["product"] == "MCE_INDEPENDENTE"
    assert obj["classification"] == "PUBLIC_PROCESS_METADATA_ONLY"
    assert obj["states"]["PRODUCTION_COMPLETE"] == "NO"
    assert obj["states"]["MCE_XLSX"] == "NAO_EMITIDO_BLOQUEADO"
    assert [(a["kind"], a["last_observed_pv"]) for a in obj["reference_artifacts"]] == [
        ("MCE_XLSX", 3), ("QUESTIONS_DOCX", 4)
    ]
    assert all(a["bytes_in_private_vault_verified"] is False for a in obj["reference_artifacts"])
    assert obj["requirements"]["require_real_independent_code_reviewer"] is True
    assert obj["requirements"]["require_actual_private_bytes"] is True
    for path in (RESTART, MEMORY, WORKFLOW):
        assert path.is_file()
    assert "MCE_CHAT_CONTINUITY.md" in RESTART.read_text(encoding="utf-8")
    assert "CHAT_CONTINUITY_CONTRACT.json" in WORKFLOW.read_text(encoding="utf-8") or "CHAT_CONTINUITY_CONTRACT.json" in RESTART.read_text(encoding="utf-8")


def test_public_checkpoint_contains_no_industrial_payloads():
    obj = json.loads(POLICY.read_text(encoding="utf-8"))
    assert all("sha256" not in artifact and "file_name" not in artifact
               for artifact in obj["reference_artifacts"])
    assert "PRIVATE_PROCESS_METADATA" not in POLICY.read_text(encoding="utf-8")
