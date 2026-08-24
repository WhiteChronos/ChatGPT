from pipeline.validate_engineering import validate_project


def test_rejects_non_12mm_and_distorted_symbol():
    data = {
        "documents": [{"id": "DOC-1", "understanding_status": "APROVADO"}],
        "symbols": [
            {
                "id": "SYM-1",
                "family": "PLC",
                "location": "MAIN_PANEL",
                "external_width_mm": 12.0,
                "external_height_mm": 10.0,
                "location_line": "SINGLE_SOLID",
                "status": "PROPOSTO"
            }
        ]
    }
    codes = {f.code for f in validate_project(data)}
    assert "DM-12MM" in codes
    assert "DM-DISTORTION" in codes


def test_redundant_machine_requires_command_run_fault_available_and_transfer_logic():
    data = {
        "documents": [{"id": "DOC-1", "understanding_status": "APROVADO"}],
        "equipment": [
            {
                "id": "EQ-A",
                "redundant_pair": True,
                "signal_roles": ["CMD", "RUN"],
                "transfer_logic": ""
            }
        ]
    }
    codes = {f.code for f in validate_project(data)}
    assert "REDUNDANCY-SIGNALS" in codes
    assert "REDUNDANCY-TRANSFER" in codes


def test_complete_interlock_passes():
    data = {
        "documents": [{"id": "DOC-1", "understanding_status": "APROVADO"}],
        "interlocks": [
            {
                "id": "INT-1",
                "cause": "FAULT_A",
                "condition": "FAULT_A=1",
                "affected_equipment": "MACHINE_A",
                "effect": "STOP_AND_BLOCK",
                "feedback": "RUN_A=0",
                "reset": "MANUAL_RESET",
                "safe_state": "A_STOPPED",
                "evidence": "DOC-X folha 9"
            }
        ]
    }
    assert validate_project(data) == []
