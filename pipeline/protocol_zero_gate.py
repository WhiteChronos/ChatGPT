#!/usr/bin/env python3
"""Protocol Zero semantic gate: question before finding."""
from __future__ import annotations
import json
from pathlib import Path
import sys
from typing import Any

DEFAULT = Path("datasheet/projects/example-project.json")

def validate_protocol_zero(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    pz = data.get("protocol_zero")
    if not isinstance(pz, dict):
        return ["protocol_zero is required"]
    if pz.get("policy") != "QUESTION_BEFORE_FINDING":
        errors.append("protocol_zero.policy must be QUESTION_BEFORE_FINDING")
    questions = pz.get("questions")
    if not isinstance(questions, list) or not questions:
        errors.append("protocol_zero.questions must be a non-empty list")
        return errors

    seen: set[str] = set()
    unresolved = 0
    for i, item in enumerate(questions):
        where = f"protocol_zero.questions[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where} must be an object")
            continue
        qid = item.get("id")
        question = item.get("question")
        answer = item.get("answer")
        status = item.get("status")
        promote = item.get("promotes_to_finding")
        finding_ids = item.get("finding_ids")
        if not isinstance(qid, str) or not qid.strip():
            errors.append(f"{where}.id must be nonblank")
        elif qid in seen:
            errors.append(f"duplicate protocol question id: {qid}")
        else:
            seen.add(qid)
        if not isinstance(question, str) or not question.strip():
            errors.append(f"{where}.question must be nonblank")
        if status not in {"ANSWERED", "UNANSWERED"}:
            errors.append(f"{where}.status must be ANSWERED or UNANSWERED")
            continue
        if not isinstance(promote, bool):
            errors.append(f"{where}.promotes_to_finding must be boolean")
        if not isinstance(finding_ids, list) or any(not isinstance(fid, str) or not fid.strip() for fid in finding_ids):
            errors.append(f"{where}.finding_ids must be a list of nonblank finding ids")
            finding_ids = []
        if status == "ANSWERED":
            if not isinstance(answer, str) or not answer.strip():
                errors.append(f"{where}: ANSWERED requires a nonblank answer")
        else:
            unresolved += 1
            if isinstance(answer, str) and answer.strip():
                errors.append(f"{where}: UNANSWERED must not carry a substantive answer")
            if promote is True:
                errors.append(f"{where}: unanswered question cannot be promoted to finding")
            if finding_ids:
                errors.append(f"{where}: unanswered question cannot link to findings")

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
            errors.append(f"finding {fid}: protocol_question_id must reference an existing Protocol Zero question")
            continue
        if question.get("status") != "ANSWERED":
            errors.append(f"finding {fid}: linked Protocol Zero question must be ANSWERED")
        linked = question.get("finding_ids", [])
        if fid not in linked:
            errors.append(f"finding {fid}: linked Protocol Zero question must reciprocally list the finding id")

    for qid, question in question_by_id.items():
        for fid in question.get("finding_ids", []) if isinstance(question.get("finding_ids"), list) else []:
            if fid not in finding_by_id:
                errors.append(f"Protocol Zero question {qid}: finding_ids references unknown finding {fid}")
            elif finding_by_id[fid].get("protocol_question_id") != qid:
                errors.append(f"Protocol Zero question {qid}: finding {fid} points to a different protocol_question_id")

    declared = pz.get("unresolved_count")
    if declared != unresolved:
        errors.append(f"protocol_zero.unresolved_count must equal computed unresolved count {unresolved}")

    if data.get("release_gate") == "PASS" and unresolved:
        errors.append("release_gate PASS is forbidden while Protocol Zero has unanswered questions")
    return errors

def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    path = Path(args[0]) if args else DEFAULT
    try:
        data = load(path)
    except Exception as exc:
        print(f"RESULT: BLOCK\nERROR: {exc}")
        return 1
    errors = validate_protocol_zero(data)
    if errors:
        print("RESULT: BLOCK")
        for err in errors:
            print(f"- {err}")
        return 1
    print("RESULT: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
