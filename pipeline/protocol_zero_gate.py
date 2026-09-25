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
        source_checks = item.get("source_checks")
        pre_search = item.get("pre_escalation_search_completed")
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
        if pre_search is not True:
            errors.append(f"{where}.pre_escalation_search_completed must be true")
        if not isinstance(source_checks, list) or not source_checks:
            errors.append(f"{where}.source_checks must be a non-empty list")
            source_types = set()
        else:
            source_types = {
                check.get("source_type")
                for check in source_checks
                if isinstance(check, dict)
            }
            if not source_types.intersection({"PROJECT_DOCUMENT", "CONTRACT_OR_PROJECT_BASIS"}):
                errors.append(f"{where}: source_checks must include project source review")
        if status == "ANSWERED":
            if not isinstance(answer, str) or not answer.strip():
                errors.append(f"{where}: ANSWERED requires a nonblank answer")
        else:
            unresolved += 1
            if isinstance(answer, str) and answer.strip():
                errors.append(f"{where}: UNANSWERED must not carry a substantive answer")
            if promote is True:
                errors.append(f"{where}: unanswered question cannot be promoted to finding")
            external_types = {
                "APPLICABLE_STANDARD",
                "REFERENCE_STANDARD",
                "OFFICIAL_AUTHORITY",
                "OFFICIAL_MANUFACTURER",
                "SPECIALIST_REFERENCE",
            }
            if not source_types.intersection(external_types):
                errors.append(
                    f"{where}: unanswered question requires normative/official/specialist pre-escalation source check"
                )

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
