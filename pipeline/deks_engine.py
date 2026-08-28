from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "datacenter" / "DEKS_CONFIG.json"
CONFIG_SCHEMA = ROOT / "schemas" / "deks_config_v1.schema.json"
MASTER = ROOT / "datacenter" / "GLOSSARY_MASTER.json"
SOURCES = ROOT / "datacenter" / "GLOSSARY_SOURCES.json"
STATUS = ROOT / "datacenter" / "DEKS_STATUS.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_repo_path(value: str) -> Path:
    return (ROOT / value).resolve()


def validate() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    config = load_json(CONFIG)
    schema = load_json(CONFIG_SCHEMA)
    validator = Draft202012Validator(schema)
    for issue in sorted(validator.iter_errors(config), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in issue.path) or "<root>"
        errors.append(f"DEKS_CONFIG {location}: {issue.message}")

    for label, relative_path in config.get("source_of_truth", {}).items():
        path = resolve_repo_path(relative_path)
        if not path.exists():
            errors.append(f"source_of_truth ausente ({label}): {relative_path}")

    docs = config.get("documentation", {})
    for key in ("config", "docs_dir"):
        relative_path = docs.get(key)
        if relative_path and not resolve_repo_path(relative_path).exists():
            errors.append(f"documentation.{key} ausente: {relative_path}")

    governance = config.get("governance", {})
    if governance.get("github_is_normative_authority") is not False:
        errors.append("GitHub não pode ser autoridade normativa no DEKS")
    if governance.get("auto_promote_technical_content") is not False:
        errors.append("promoção automática de conteúdo técnico deve permanecer desabilitada")

    master = load_json(MASTER)
    sources = load_json(SOURCES)
    source_ids = {item.get("id") for item in sources.get("sources", [])}
    required_tool_sources = {"GH-MKDOCS-MATERIAL", "GH-MERMAID"}
    missing_tools = required_tool_sources - source_ids
    if missing_tools:
        errors.append(f"fontes de tooling DEKS não cadastradas: {sorted(missing_tools)}")

    entries = master.get("entries", [])
    id_map = {entry.get("id"): entry for entry in entries if entry.get("id")}
    if len(id_map) != len(entries):
        errors.append("GLOSSARY_MASTER contém ID ausente ou duplicado")

    term_map: dict[str, str] = {}
    for entry in entries:
        entry_id = entry.get("id", "<sem-id>")
        term = str(entry.get("term", "")).strip()
        if not term:
            errors.append(f"{entry_id}: termo vazio")
            continue
        term_map[term.casefold()] = entry_id
        for alias in entry.get("aliases", []):
            term_map[str(alias).casefold()] = entry_id

        refs = entry.get("source_refs", [])
        if not refs:
            errors.append(f"{entry_id}: sem rastreabilidade de fonte")
        if entry.get("status") == "CONFIRMADO_NORMATIVO" and entry.get("evidence_class") == "E7_GITHUB_OPEN_SOURCE":
            errors.append(f"{entry_id}: GitHub não pode confirmar conteúdo normativo sozinho")

    for entry in entries:
        entry_id = entry.get("id", "<sem-id>")
        for relationship in entry.get("relationships", []):
            target = str(relationship).casefold()
            if target not in term_map:
                warnings.append(f"{entry_id}: relação externa/não indexada: {relationship}")

    return errors, warnings


def write_status(errors: list[str], warnings: list[str]) -> None:
    payload = {
        "engine": "DEKS_ENGINE_V1_0",
        "ok": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "note": "O DEKS valida governança, configuração e rastreabilidade. Relações ainda não cadastradas são avisos até que o datacenter seja expandido.",
    }
    STATUS.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    errors, warnings = validate()
    write_status(errors, warnings)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("DEKS_ENGINE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
