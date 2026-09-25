import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.protocol_zero_gate import validate_protocol_zero

def base():
    return {
        "release_gate": "BLOCK",
        "protocol_zero": {
            "policy": "QUESTION_BEFORE_FINDING",
            "unresolved_count": 1,
            "questions": [
                {
                    "id": "Q-01",
                    "question": "Which control philosophy applies?",
                    "answer": "",
                    "status": "UNANSWERED",
                    "promotes_to_finding": False,
                    "pre_escalation_search_completed": True,
                    "source_checks": [
                        {
                            "source_type": "PROJECT_DOCUMENT",
                            "source_id": "SYNTHETIC-PROJECT-DOC",
                            "result": "PARTIAL",
                            "note": "Synthetic project source checked first.",
                        },
                        {
                            "source_type": "REFERENCE_STANDARD",
                            "source_id": "PETROBRAS-N-1882",
                            "result": "NOT_FOUND",
                            "note": "Synthetic normative lookup completed before escalation.",
                        },
                    ],
                }
            ],
        },
    }

def test_unanswered_question_is_valid_pending():
    assert validate_protocol_zero(base()) == []

def test_unanswered_question_cannot_promote_to_finding():
    data = base()
    data["protocol_zero"]["questions"][0]["promotes_to_finding"] = True
    assert any("cannot be promoted" in e for e in validate_protocol_zero(data))

def test_pass_forbidden_with_unanswered_question():
    data = base()
    data["release_gate"] = "PASS"
    assert any("PASS is forbidden" in e for e in validate_protocol_zero(data))

def test_answered_question_requires_answer():
    data = base()
    q = data["protocol_zero"]["questions"][0]
    q["status"] = "ANSWERED"
    q["answer"] = ""
    data["protocol_zero"]["unresolved_count"] = 0
    assert any("requires a nonblank answer" in e for e in validate_protocol_zero(data))


def test_unanswered_question_requires_external_source_check():
    data = base()
    data["protocol_zero"]["questions"][0]["source_checks"] = [
        {
            "source_type": "PROJECT_DOCUMENT",
            "source_id": "SYNTHETIC-PROJECT-DOC",
            "result": "PARTIAL",
            "note": "Only project source was checked.",
        }
    ]
    assert any("normative/official/specialist" in e for e in validate_protocol_zero(data))


def test_pre_escalation_search_must_be_complete():
    data = base()
    data["protocol_zero"]["questions"][0]["pre_escalation_search_completed"] = False
    assert any("pre_escalation_search_completed" in e for e in validate_protocol_zero(data))
