from document_evaluation.protocol_zero import validate_protocol_zero


def test_unanswered_question_blocks_pass():
    data = {
        "release_gate": "PASS",
        "findings": [],
        "protocol_zero": {
            "policy": "QUESTION_BEFORE_FINDING",
            "unresolved_count": 1,
            "questions": [{
                "id": "Q-01",
                "question": "Which philosophy applies?",
                "answer": "",
                "status": "UNANSWERED",
                "promotes_to_finding": False,
                "finding_ids": [],
            }],
        },
    }
    assert any("PASS is forbidden" in error for error in validate_protocol_zero(data))
