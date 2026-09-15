from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "pipeline/conversation_contract.py"
spec = importlib.util.spec_from_file_location("conversation_contract", SCRIPT)
cc = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(cc)


def test_contract_validate_passes():
    result = cc.validate_contract(ROOT)
    assert result["status"] == "PASS"
    assert result["memory_id"] == "AUT-PANEL-CONVERSATION-BRIDGE-V1"
    assert result["pipeline_id"] == "AUT-PANEL-IMMUTABLE-V1.6"


def test_explaincode_is_read_only():
    result = cc.dispatch(ROOT, "/explaincode pipeline/render_panel_scaled.py")
    assert result["mode"] == "READ_ONLY"
    assert result["may_modify_target"] is False


def test_refactor_marks_locked_target():
    result = cc.dispatch(ROOT, "/refactor pipeline/pipeline.yaml")
    assert result["mode"] == "BEHAVIOR_PRESERVING_WRITE"
    assert result["behavior_change_allowed"] is False
    assert result["locked_target"] is True
    assert result["explicit_authorization_required_before_edit"] is True


def test_refactor_allows_nonlocked_code_target_without_contract_permission():
    result = cc.dispatch(ROOT, "/refactor pipeline/some_nonlocked_module.py")
    assert result["locked_target"] is False
    assert result["behavior_change_allowed"] is False
