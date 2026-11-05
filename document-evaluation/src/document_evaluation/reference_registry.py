from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

CANONICAL_REGISTRY_ID = "ENGINEERING_REFERENCE_REGISTRY_V1_0"


def _https_url(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate_registry(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("registry_id") != CANONICAL_REGISTRY_ID:
        errors.append(f"registry_id must be {CANONICAL_REGISTRY_ID}")

    authoritative = data.get("authoritative_sources")
    repositories = data.get("open_source_repositories")
    if not isinstance(authoritative, list) or not authoritative:
        errors.append("authoritative_sources must be a non-empty list")
        authoritative = []
    if not isinstance(repositories, list) or not repositories:
        errors.append("open_source_repositories must be a non-empty list")
        repositories = []

    seen: set[str] = set()
    for group_name, items, url_field in (
        ("authoritative_sources", authoritative, "official_url"),
        ("open_source_repositories", repositories, "repository_url"),
    ):
        for i, item in enumerate(items):
            where = f"{group_name}[{i}]"
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
            if not _https_url(item.get(url_field)):
                errors.append(f"{where}.{url_field} must be a nonblank https URL")

    for i, item in enumerate(repositories):
        if not isinstance(item, dict):
            continue
        where = f"open_source_repositories[{i}]"
        if item.get("normative") is not False:
            errors.append(f"{where}.normative must be false")
        if item.get("archived") is not False:
            errors.append(f"{where}.archived must be false")
        status = item.get("adoption_status")
        if not isinstance(status, str) or not status.startswith("REFERENCE_ONLY"):
            errors.append(f"{where}.adoption_status must remain REFERENCE_ONLY until approved")

    policy = data.get("policy")
    if not isinstance(policy, dict):
        errors.append("policy must be an object")
    else:
        for key in (
            "open_source_is_not_normative",
            "require_official_url_for_authoritative_source",
            "require_repository_url_for_open_source",
            "require_license_security_maintenance_review_before_adoption",
            "do_not_store_licensed_standard_text_in_repository",
            "do_not_use_open_source_repository_as_project_evidence",
        ):
            if policy.get(key) is not True:
                errors.append(f"policy.{key} must be true")
    return errors


def load_registry(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
