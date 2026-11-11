from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "datacenter" / "DEKS_CONFIG.json"
CONFIG_SCHEMA = ROOT / "schemas" / "deks_config_v1_1.schema.json"
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

    source_of_truth = config.get("source_of_truth", {})
    for label, relative_path in source_of_truth.items():
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

    ingestion = config.get("ingestion", {})
    for key in ("engine", "batch_schema", "source_registry_schema"):
        relative_path = ingestion.get(key)
        if not relative_path:
            errors.append(f"ingestion.{key} ausente")
        elif not resolve_repo_path(relative_path).exists():
            errors.append(f"ingestion.{key} não encontrado: {relative_path}")
    if ingestion.get("auto_approve") is not False:
        errors.append("Knowledge Ingestion não pode aprovar itens automaticamente")
    if ingestion.get("staging_required") is not True:
        errors.append("Knowledge Ingestion deve exigir staging")
    if ingestion.get("review_required") is not True:
        errors.append("Knowledge Ingestion deve exigir revisão técnica")
    if set(ingestion.get("supported_formats", [])) != {"json", "csv"}:
        errors.append("Knowledge Ingestion v1.1 deve suportar exatamente JSON e CSV")

    ingestion_sources_path = source_of_truth.get("ingestion_sources")
    if ingestion_sources_path and resolve_repo_path(ingestion_sources_path).exists():
        ingestion_sources = load_json(resolve_repo_path(ingestion_sources_path))
        if ingestion_sources.get("auto_approval") is not False:
            errors.append("registro de fontes de ingestão não pode habilitar auto_approval")
        ingestion_source_ids = [item.get("source_id") for item in ingestion_sources.get("sources", [])]
        if len(ingestion_source_ids) != len(set(ingestion_source_ids)):
            errors.append("registro de fontes de ingestão contém source_id duplicado")

    ingestion_queue_path = source_of_truth.get("ingestion_review_queue")
    if ingestion_queue_path and resolve_repo_path(ingestion_queue_path).exists():
        ingestion_queue = load_json(resolve_repo_path(ingestion_queue_path))
        if ingestion_queue.get("auto_approval") is not False:
            errors.append("fila de revisão de ingestão não pode habilitar auto_approval")
        allowed_statuses = set(ingestion_queue.get("allowed_statuses", []))
        for item in ingestion_queue.get("items", []):
            if item.get("review_status") not in allowed_statuses:
                errors.append(
                    f"fila de ingestão contém status inválido para {item.get('ingestion_id', '<sem-id>')}"
                )

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
        "engine": "DEKS_ENGINE_V1_1",
        "ok": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "note": "O DEKS v1.1 valida governança, rastreabilidade e a camada Knowledge Ingestion. Relações ainda não cadastradas permanecem como avisos até expansão do datacenter.",
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
