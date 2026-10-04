from __future__ import annotations

from typing import Any


def validate_protocol_zero(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    pz = data.get("protocol_zero")
    if not isinstance(pz, dict):
        return ["protocol_zero is required"]
    if pz.get("policy") != "QUESTION_BEFORE_FINDING":
        errors.append("protocol_zero.policy must be QUESTION_BEFORE_FINDING")

    questions = pz.get("questions")
    if not isinstance(questions, list) or not questions:
        return errors + ["protocol_zero.questions must be a non-empty list"]

    seen: set[str] = set()
    unresolved = 0
    for i, item in enumerate(questions):
        where = f"protocol_zero.questions[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where} must be an object")
            continue
        qid = item.get("id")
        status = item.get("status")
        answer = item.get("answer")
        if not isinstance(qid, str) or not qid.strip():
            errors.append(f"{where}.id must be nonblank")
        elif qid in seen:
            errors.append(f"duplicate protocol question id: {qid}")
        else:
            seen.add(qid)
        if status == "ANSWERED":
            if not isinstance(answer, str) or not answer.strip():
                errors.append(f"{where}: ANSWERED requires a nonblank answer")
        elif status == "UNANSWERED":
            unresolved += 1
            if isinstance(answer, str) and answer.strip():
                errors.append(f"{where}: UNANSWERED must not carry a substantive answer")
            if item.get("promotes_to_finding") is True:
                errors.append(f"{where}: unanswered question cannot be promoted to finding")
            if item.get("finding_ids"):
                errors.append(f"{where}: unanswered question cannot link to findings")
        else:
            errors.append(f"{where}.status must be ANSWERED or UNANSWERED")

    findings = data.get("findings", [])
    finding_by_id = {
        finding.get("id"): finding
        for finding in findings
        if isinstance(finding, dict) and isinstance(finding.get("id"), str)
    }
    question_by_id = {
        item.get("id"): item
        for item in questions
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    for fid, finding in finding_by_id.items():
        qid = finding.get("protocol_question_id")
        question = question_by_id.get(qid)
        if question is None:
            errors.append(f"finding {fid}: protocol_question_id must reference an existing question")
            continue
        if question.get("status") != "ANSWERED":
            errors.append(f"finding {fid}: linked question must be ANSWERED")
        if fid not in question.get("finding_ids", []):
            errors.append(f"finding {fid}: linked question must reciprocally list the finding id")

    if pz.get("unresolved_count") != unresolved:
        errors.append(f"protocol_zero.unresolved_count must equal computed unresolved count {unresolved}")
    if data.get("release_gate") == "PASS" and unresolved:
        errors.append("release_gate PASS is forbidden while Protocol Zero has unanswered questions")
    return errors
