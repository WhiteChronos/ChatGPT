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
                    "finding_ids": [],
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


def test_finding_requires_answered_linked_question():
    data = base()
    data["findings"] = [
        {
            "id": "F-01",
            "protocol_question_id": "Q-01",
        }
    ]
    data["protocol_zero"]["questions"][0]["finding_ids"] = ["F-01"]
    errors = validate_protocol_zero(data)
    assert any("linked Protocol Zero question must be ANSWERED" in e for e in errors)


def test_answered_question_and_finding_link_must_be_bidirectional():
    data = base()
    q = data["protocol_zero"]["questions"][0]
    q["status"] = "ANSWERED"
    q["answer"] = "The approved control philosophy applies."
    q["promotes_to_finding"] = True
    q["finding_ids"] = ["F-01"]
    data["protocol_zero"]["unresolved_count"] = 0
    data["findings"] = [{"id": "F-01", "protocol_question_id": "Q-OTHER"}]
    errors = validate_protocol_zero(data)
    assert any("protocol_question_id must reference an existing" in e or "points to a different" in e for e in errors)


def test_answered_question_and_finding_link_passes():
    data = base()
    q = data["protocol_zero"]["questions"][0]
    q["status"] = "ANSWERED"
    q["answer"] = "The approved control philosophy applies."
    q["promotes_to_finding"] = True
    q["finding_ids"] = ["F-01"]
    data["protocol_zero"]["unresolved_count"] = 0
    data["findings"] = [{"id": "F-01", "protocol_question_id": "Q-01"}]
    assert validate_protocol_zero(data) == []
