#!/usr/bin/env python3
"""Auditoria e descoberta controlada de ferramentas documentais no GitHub.

A descoberta nunca instala dependências. O relatório serve para avaliação humana,
licenciamento, segurança e decisão por PR.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_STATUSES = {
    "DISCOVERED",
    "EVALUATION",
    "APPROVED_OPTIONAL",
    "APPROVED_CORE",
    "APPROVED_GENERATION_ONLY",
    "APPROVED_CI",
    "REVIEW_REQUIRED",
    "REVIEW_REQUIRED_LICENSE",
    "REFERENCE_ONLY",
    "RESEARCH_ONLY",
    "BLOCKED",
    "RETIRED",
}


@dataclass(frozen=True)
class AuditFinding:
    repository: str
    severity: str
    code: str
    message: str


def load_registry(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data.get("repositories"), list) or not data["repositories"]:
        raise ValueError("Registro sem repositories")
    if data.get("policy", {}).get("auto_install_forbidden") is not True:
        raise ValueError("auto_install_forbidden deve permanecer true")
    seen: set[str] = set()
    for entry in data["repositories"]:
        for field in ("full_name", "category", "status", "purpose"):
            if not entry.get(field):
                raise ValueError(f"Registro incompleto: {entry!r}; falta {field}")
        if entry["full_name"] in seen:
            raise ValueError(f"Repositório duplicado: {entry['full_name']}")
        seen.add(entry["full_name"])
        if entry["status"] not in ALLOWED_STATUSES:
            raise ValueError(f"Status não governado: {entry['status']}")
        if entry.get("auto_install") is not False:
            raise ValueError(f"auto_install deve ser false: {entry['full_name']}")
    return data


def _request_json(url: str, token: str | None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AUTOMACAO-document-tooling-audit/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def audit_repository(entry: dict[str, Any], token: str | None) -> tuple[dict[str, Any], list[AuditFinding]]:
    full_name = entry["full_name"]
    url = f"https://api.github.com/repos/{full_name}"
    findings: list[AuditFinding] = []
    try:
        metadata = _request_json(url, token)
    except urllib.error.HTTPError as exc:
        severity = "CRITICAL" if entry["status"] == "APPROVED_CORE" else "HIGH"
        findings.append(AuditFinding(full_name, severity, "PLUGIN-HTTP", f"GitHub retornou HTTP {exc.code}"))
        return {"full_name": full_name, "available": False}, findings
    except Exception as exc:  # pragma: no cover - rede externa
        findings.append(AuditFinding(full_name, "HIGH", "PLUGIN-NETWORK", str(exc)))
        return {"full_name": full_name, "available": False}, findings

    if metadata.get("archived") or metadata.get("disabled"):
        severity = "CRITICAL" if entry["status"] == "APPROVED_CORE" else "HIGH"
        findings.append(AuditFinding(full_name, severity, "PLUGIN-INACTIVE", "Repositório arquivado ou desabilitado"))

    expected = entry.get("expected_license")
    actual = (metadata.get("license") or {}).get("spdx_id")
    if expected and actual and expected != actual:
        findings.append(
            AuditFinding(full_name, "HIGH", "PLUGIN-LICENSE", f"Licença esperada {expected}; encontrada {actual}")
        )
    if entry["status"].startswith("APPROVED") and not actual:
        findings.append(AuditFinding(full_name, "HIGH", "PLUGIN-LICENSE-MISSING", "Licença não identificada pela API"))

    result = {
        "full_name": full_name,
        "available": True,
        "archived": metadata.get("archived"),
        "disabled": metadata.get("disabled"),
        "default_branch": metadata.get("default_branch"),
        "pushed_at": metadata.get("pushed_at"),
        "license": actual,
        "html_url": metadata.get("html_url"),
        "status": entry["status"],
    }
    return result, findings


def discover_candidates(queries: list[str], token: str | None, per_query: int = 5) -> list[dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    for query in queries:
        url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
            {"q": query, "sort": "updated", "order": "desc", "per_page": per_query}
        )
        try:
            data = _request_json(url, token)
        except Exception:  # descoberta não deve bloquear o registro offline
            continue
        for item in data.get("items", []):
            full_name = item.get("full_name")
            if full_name:
                candidates[full_name] = {
                    "full_name": full_name,
                    "description": item.get("description"),
                    "updated_at": item.get("updated_at"),
                    "archived": item.get("archived"),
                    "license": (item.get("license") or {}).get("spdx_id"),
                    "html_url": item.get("html_url"),
                }
    return sorted(candidates.values(), key=lambda item: item["full_name"].lower())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default="plugins/document_tooling_registry.json")
    parser.add_argument("--out", default="document_tooling_audit.json")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args(argv)

    registry = load_registry(args.registry)
    report: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "registry_version": registry["registry_version"],
        "scope_statement": registry.get("scope_statement"),
        "auto_install": False,
        "repositories": [],
        "findings": [],
        "discovered_candidates": [],
    }

    if not args.offline:
        token = os.environ.get("GITHUB_TOKEN")
        all_findings: list[AuditFinding] = []
        for entry in registry["repositories"]:
            result, findings = audit_repository(entry, token)
            report["repositories"].append(result)
            all_findings.extend(findings)
        report["findings"] = [asdict(item) for item in all_findings]
        registered = {entry["full_name"] for entry in registry["repositories"]}
        report["discovered_candidates"] = [
            item for item in discover_candidates(registry.get("discovery_queries", []), token)
            if item["full_name"] not in registered
        ]
    else:
        report["repositories"] = [
            {"full_name": entry["full_name"], "status": entry["status"], "offline_validated": True}
            for entry in registry["repositories"]
        ]

    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    critical = [item for item in report["findings"] if item["severity"] == "CRITICAL"]
    print(f"repositories={len(report['repositories'])} candidates={len(report['discovered_candidates'])} critical={len(critical)}")
    return 1 if critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
