from pipeline.comment_control_pipeline import validate_payload
from pipeline.comment_control_analytics import summarize, risk_score_baseline


def base_payload():
    return {
        "project_id": "P1",
        "source_formal_comment_count": 2,
        "comments": [
            {
                "project_id": "P1",
                "comment_id": "C01",
                "severity": "GRAVE",
                "original_comment": "Corrigir A",
                "compiled_action": "Corrigir A",
                "origin_type": "FORMAL_COMMENT",
                "status_control": "UNCHECKED",
                "required_documents": ["MD-1"],
                "verified_documents": [],
                "created_at": "2026-09-01T00:00:00+00:00",
            },
            {
                "project_id": "P1",
                "comment_id": "C02",
                "severity": "ALTO",
                "original_comment": "Corrigir B",
                "compiled_action": "Corrigir B",
                "origin_type": "FORMAL_COMMENT",
                "status_control": "UNCHECKED",
                "required_documents": [],
                "verified_documents": [],
                "created_at": "2026-09-02T00:00:00+00:00",
            },
        ],
        "new_divergences": [],
    }


def codes(payload):
    return {f.code for f in validate_payload(payload)}


def test_valid_initial_payload_has_no_findings():
    assert validate_payload(base_payload()) == []


def test_count_mismatch_blocks():
    payload = base_payload()
    payload["source_formal_comment_count"] = 3
    assert "CC-COUNT-INTEGRITY" in codes(payload)


def test_duplicate_comment_blocks():
    payload = base_payload()
    payload["comments"][1]["comment_id"] = "C01"
    assert "CC-DUPLICATE" in codes(payload)


def test_checked_without_evidence_blocks():
    payload = base_payload()
    payload["comments"][0]["status_control"] = "CHECKED"
    payload["comments"][0]["verified_at"] = "2026-09-09T12:00:00+00:00"
    assert "CC-CHECKED-EVIDENCE" in codes(payload)


def test_checked_multidocument_requires_all_documents():
    payload = base_payload()
    row = payload["comments"][0]
    row["status_control"] = "CHECKED"
    row["verified_at"] = "2026-09-09T12:00:00+00:00"
    row["evidence_text"] = "MD corrigido"
    row["verified_documents"] = []
    assert "CC-MULTIDOC-EVIDENCE" in codes(payload)


def test_analytics_counts_only_formal_comments():
    payload = base_payload()
    payload["comments"].append(
        {
            "project_id": "P1",
            "comment_id": "ND01",
            "severity": "LEVE",
            "original_comment": "Nova divergência",
            "compiled_action": "Corrigir",
            "origin_type": "NEW_DIVERGENCE",
            "status_control": "UNCHECKED",
            "created_at": "2026-09-03T00:00:00+00:00",
        }
    )
    result = summarize(payload["comments"])
    assert result["formal_comment_count"] == 2


def test_risk_score_is_bounded():
    score = risk_score_baseline(base_payload()["comments"][0])["score"]
    assert 0 <= score <= 1
