from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "datacenter" / "INGESTION_SOURCE_REGISTRY.json"
REGISTRY_SCHEMA = ROOT / "schemas" / "ingestion_source_registry_v1.schema.json"
BATCH_SCHEMA = ROOT / "schemas" / "ingestion_batch_v1.schema.json"
DEFAULT_QUEUE = ROOT / "datacenter" / "INGESTION_REVIEW_QUEUE.json"
STATUS_FILE = ROOT / "datacenter" / "INGESTION_STATUS.json"

CONTROL_FIELDS = {
    "entity_type",
    "external_id",
    "evidence_class",
    "provenance_json",
    "payload_json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_ingestion_id(source_id: str, entity_type: str, external_id: str, payload: dict[str, Any]) -> str:
    material = {
        "source_id": source_id,
        "entity_type": entity_type,
        "external_id": external_id,
        "payload": payload,
    }
    digest = hashlib.sha256(canonical_json(material).encode("utf-8")).hexdigest()[:20]
    return f"ING-{digest}"


def validate_with_schema(payload: Any, schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    for issue in sorted(validator.iter_errors(payload), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in issue.path) or "<root>"
        errors.append(f"{location}: {issue.message}")
    return errors


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    return load_json(path)


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors = validate_with_schema(registry, REGISTRY_SCHEMA)
    ids = [item.get("source_id") for item in registry.get("sources", [])]
    if len(ids) != len(set(ids)):
        errors.append("sources: source_id duplicado")
    if registry.get("auto_approval") is not False:
        errors.append("auto_approval deve permanecer false")
    return errors


def registry_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["source_id"]): item for item in registry.get("sources", [])}


def _json_records(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict) and isinstance(payload.get("records"), list):
        records = payload["records"]
    else:
        raise ValueError("JSON de entrada deve ser uma lista ou objeto com campo records")
    if not all(isinstance(item, dict) for item in records):
        raise ValueError("todos os registros de entrada devem ser objetos JSON")
    return records


def _csv_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            payload_json = (row.get("payload_json") or "").strip()
            provenance_json = (row.get("provenance_json") or "").strip()
            if payload_json:
                payload = json.loads(payload_json)
                if not isinstance(payload, dict):
                    raise ValueError(f"linha {row_number}: payload_json deve ser objeto")
            else:
                payload = {
                    key: value
                    for key, value in row.items()
                    if key not in CONTROL_FIELDS and value not in (None, "")
                }
            provenance = json.loads(provenance_json) if provenance_json else {"row": row_number}
            if not isinstance(provenance, dict):
                raise ValueError(f"linha {row_number}: provenance_json deve ser objeto")
            records.append(
                {
                    "entity_type": row.get("entity_type", ""),
                    "external_id": row.get("external_id", ""),
                    "evidence_class": row.get("evidence_class") or None,
                    "payload": payload,
                    "provenance": provenance,
                }
            )
    return records


def read_records(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.casefold()
    if suffix == ".json":
        return _json_records(path)
    if suffix == ".csv":
        return _csv_records(path)
    raise ValueError(f"formato não suportado: {path.suffix}")


def normalize_record(record: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    entity_type = str(record.get("entity_type") or "").strip()
    external_id = str(record.get("external_id") or record.get("id") or record.get("term") or "").strip()
    if not entity_type:
        raise ValueError("entity_type ausente")
    if entity_type not in source.get("allowed_entity_types", []):
        raise ValueError(f"entity_type não permitido para {source['source_id']}: {entity_type}")
    if not external_id:
        raise ValueError("external_id ausente")

    payload = record.get("payload")
    if payload is None:
        payload = {
            key: value
            for key, value in record.items()
            if key not in {"entity_type", "external_id", "id", "term", "evidence_class", "provenance"}
        }
    if not isinstance(payload, dict) or not payload:
        raise ValueError(f"{external_id}: payload deve ser objeto não vazio")

    provenance = record.get("provenance") or {}
    if not isinstance(provenance, dict):
        raise ValueError(f"{external_id}: provenance deve ser objeto")
    provenance = dict(provenance)
    provenance["source_id"] = source["source_id"]

    evidence_class = record.get("evidence_class") or source["default_evidence_class"]
    ingestion_id = stable_ingestion_id(source["source_id"], entity_type, external_id, payload)

    return {
        "ingestion_id": ingestion_id,
        "entity_type": entity_type,
        "external_id": external_id,
        "payload": payload,
        "provenance": provenance,
        "evidence_class": evidence_class,
        "review_status": "REVIEW_REQUIRED",
        "auto_promoted": False,
    }


def build_batch(
    source_id: str,
    records: list[dict[str, Any]],
    registry: dict[str, Any],
    source_revision: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    sources = registry_map(registry)
    if source_id not in sources:
        raise ValueError(f"source_id não registrado: {source_id}")
    source = sources[source_id]
    if not source.get("enabled") or source.get("status") != "ACTIVE":
        raise ValueError(f"fonte não habilitada para ingestão: {source_id}")

    normalized = [normalize_record(record, source) for record in records]
    ids = [item["ingestion_id"] for item in normalized]
    if len(ids) != len(set(ids)):
        raise ValueError("lote contém registros duplicados após normalização")

    batch_material = {
        "source_id": source_id,
        "source_revision": source_revision,
        "ingestion_ids": sorted(ids),
    }
    batch_hash = hashlib.sha256(canonical_json(batch_material).encode("utf-8")).hexdigest()[:16]
    timestamp = created_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    batch = {
        "schema_version": "1.0",
        "batch_id": f"BATCH-{batch_hash}",
        "source_id": source_id,
        "source_revision": source_revision,
        "created_at": timestamp,
        "records": normalized,
    }
    errors = validate_with_schema(batch, BATCH_SCHEMA)
    if errors:
        raise ValueError("lote inválido: " + " | ".join(errors))
    return batch


def merge_review_queue(queue: dict[str, Any], batch: dict[str, Any]) -> dict[str, Any]:
    if queue.get("auto_approval") is not False:
        raise ValueError("fila de revisão com auto_approval inválido")

    existing = {item.get("ingestion_id"): item for item in queue.get("items", []) if item.get("ingestion_id")}
    for record in batch["records"]:
        ingestion_id = record["ingestion_id"]
        if ingestion_id in existing:
            continue
        existing[ingestion_id] = {
            "ingestion_id": ingestion_id,
            "batch_id": batch["batch_id"],
            "source_id": batch["source_id"],
            "entity_type": record["entity_type"],
            "external_id": record["external_id"],
            "evidence_class": record["evidence_class"],
            "review_status": "REVIEW_REQUIRED",
        }

    return {
        "schema_version": queue.get("schema_version", "1.0"),
        "queue_id": queue.get("queue_id", "DEKS-INGESTION-REVIEW"),
        "auto_approval": False,
        "allowed_statuses": queue.get("allowed_statuses", ["REVIEW_REQUIRED", "APPROVED", "REJECTED"]),
        "items": sorted(existing.values(), key=lambda item: item["ingestion_id"]),
    }


def write_status(ok: bool, errors: list[str]) -> None:
    payload = {
        "engine": "DEKS_KNOWLEDGE_INGESTION_V1_1",
        "ok": ok,
        "error_count": len(errors),
        "errors": errors,
        "auto_approval": False,
        "note": "Ingestão prepara staging e revisão; não promove automaticamente conteúdo canônico.",
    }
    write_json(STATUS_FILE, payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DEKS v1.1 Knowledge Ingestion")
    parser.add_argument("--validate-registry", action="store_true")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--source-id")
    parser.add_argument("--source-revision")
    parser.add_argument("--created-at")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--review-queue", type=Path, default=DEFAULT_QUEUE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    try:
        registry = load_registry(args.registry)
        errors.extend(validate_registry(registry))
        if errors:
            raise ValueError("registro de fontes inválido: " + " | ".join(errors))

        if args.validate_registry and not args.input:
            write_status(True, [])
            print("DEKS_INGESTION_REGISTRY_OK")
            return 0

        if args.input is None or not args.source_id:
            raise ValueError("--input e --source-id são obrigatórios para ingestão")

        source = registry_map(registry).get(args.source_id)
        if source is None:
            raise ValueError(f"source_id não registrado: {args.source_id}")
        input_format = args.input.suffix.casefold().lstrip(".")
        if input_format not in source.get("allowed_formats", []):
            raise ValueError(f"formato {input_format} não permitido para {args.source_id}")

        records = read_records(args.input)
        batch = build_batch(
            args.source_id,
            records,
            registry,
            source_revision=args.source_revision,
            created_at=args.created_at,
        )
        output = args.output or (ROOT / "ingestion" / "staging" / f"{batch['batch_id']}.json")
        write_json(output, batch)

        queue = load_json(args.review_queue) if args.review_queue.exists() else {
            "schema_version": "1.0",
            "queue_id": "DEKS-INGESTION-REVIEW",
            "auto_approval": False,
            "allowed_statuses": ["REVIEW_REQUIRED", "APPROVED", "REJECTED"],
            "items": [],
        }
        write_json(args.review_queue, merge_review_queue(queue, batch))
        write_status(True, [])
        print(f"DEKS_INGESTION_OK batch={batch['batch_id']} records={len(batch['records'])}")
        return 0
    except Exception as exc:
        message = str(exc)
        write_status(False, [message])
        print(f"ERROR: {message}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
