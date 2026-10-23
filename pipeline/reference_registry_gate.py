#!/usr/bin/env python3
"""Validate the canonical engineering reference registry."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import urlparse

DEFAULT = Path("datacenter/ENGINEERING_REFERENCE_REGISTRY.json")


def _https_url(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate_registry(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("registry_id") != "ENGINEERING_REFERENCE_REGISTRY_V1_0":
        errors.append("registry_id must be ENGINEERING_REFERENCE_REGISTRY_V1_0")

    authoritative = data.get("authoritative_sources")
    repositories = data.get("open_source_repositories")
    if not isinstance(authoritative, list) or not authoritative:
        errors.append("authoritative_sources must be a non-empty list")
        authoritative = []
    if not isinstance(repositories, list) or not repositories:
        errors.append("open_source_repositories must be a non-empty list")
        repositories = []

    seen: set[str] = set()
    for i, item in enumerate(authoritative):
        where = f"authoritative_sources[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where} must be an object")
            continue
        sid = item.get("id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"{where}.id must be nonblank")
        elif sid in seen:
            errors.append(f"duplicate registry id: {sid}")
        else:
            seen.add(sid)
        if not _https_url(item.get("official_url")):
            errors.append(f"{where}.official_url must be a nonblank https URL")
        for field in ("authority", "title", "status", "access_note"):
            if not isinstance(item.get(field), str) or not item.get(field, "").strip():
                errors.append(f"{where}.{field} must be nonblank")
        if not isinstance(item.get("applies_to"), list) or not item.get("applies_to"):
            errors.append(f"{where}.applies_to must be a non-empty list")

    for i, item in enumerate(repositories):
        where = f"open_source_repositories[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where} must be an object")
            continue
        sid = item.get("id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"{where}.id must be nonblank")
        elif sid in seen:
            errors.append(f"duplicate registry id: {sid}")
        else:
            seen.add(sid)
        if item.get("normative") is not False:
            errors.append(f"{where}.normative must be false")
        if not _https_url(item.get("repository_url")):
            errors.append(f"{where}.repository_url must be a nonblank https URL")
        if not isinstance(item.get("repository"), str) or "/" not in item.get("repository", ""):
            errors.append(f"{where}.repository must be owner/name")
        if item.get("archived") is not False:
            errors.append(f"{where}.archived must be false for canonical supporting repositories")
        if not isinstance(item.get("adoption_status"), str) or not item.get("adoption_status", "").startswith("REFERENCE_ONLY"):
            errors.append(f"{where}.adoption_status must remain REFERENCE_ONLY until separately approved")

    policy = data.get("policy")
    if not isinstance(policy, dict):
        errors.append("policy must be an object")
    else:
        required_true = (
            "open_source_is_not_normative",
            "require_official_url_for_authoritative_source",
            "require_repository_url_for_open_source",
            "require_license_security_maintenance_review_before_adoption",
            "do_not_store_licensed_standard_text_in_repository",
            "do_not_use_open_source_repository_as_project_evidence",
        )
        for key in required_true:
            if policy.get(key) is not True:
                errors.append(f"policy.{key} must be true")
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
    errors = validate_registry(data)
    if errors:
        print("RESULT: BLOCK")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
