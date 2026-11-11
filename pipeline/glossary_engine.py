from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "datacenter" / "GLOSSARY_SOURCES.json"
MASTER = ROOT / "datacenter" / "GLOSSARY_MASTER.json"
DATASHEET = ROOT / "datasheet" / "GLOSSARY_ENTRY_DATA_SHEET.json"
STATUS = ROOT / "datacenter" / "GLOSSARY_STATUS.json"

ALLOWED_STATUS = {
    "CONFIRMADO_PROJETO",
    "CONFIRMADO_NORMATIVO",
    "SUPORTADO_GITHUB",
    "CONFIRMADO_COM_RESSALVA",
    "PROPOSTO",
    "CONFLITANTE",
    "TBD",
    "NÃO_APLICÁVEL",
}

ALLOWED_EVIDENCE = {
    "E1_PROJECT_DRAWING",
    "E2_PROJECT_DOCUMENT",
    "E3_FORMAL_CONFIRMATION",
    "E4_OFFICIAL_STANDARD",
    "E5_MANUFACTURER",
    "E6_ACADEMIC_BOOK_PAPER",
    "E7_GITHUB_OPEN_SOURCE",
    "E0_NO_EVIDENCE",
}

REQUIRED_ENTRY_FIELDS = {
    "id",
    "term",
    "discipline",
    "object_type",
    "definition_pt",
    "source_refs",
    "evidence_class",
    "status",
}


def _load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate() -> list[str]:
    errors: list[str] = []
    sources = _load(SOURCES)
    master = _load(MASTER)
    _load(DATASHEET)

    source_ids = {src["id"] for src in sources.get("sources", [])}
    seen_ids: set[str] = set()

    for entry in master.get("entries", []):
        missing = REQUIRED_ENTRY_FIELDS - set(entry)
        if missing:
            errors.append(f"{entry.get('id', '<sem-id>')}: campos ausentes: {sorted(missing)}")
            continue

        entry_id = entry["id"]
        if entry_id in seen_ids:
            errors.append(f"{entry_id}: id duplicado")
        seen_ids.add(entry_id)

        if entry["status"] not in ALLOWED_STATUS:
            errors.append(f"{entry_id}: status inválido: {entry['status']}")
        if entry["evidence_class"] not in ALLOWED_EVIDENCE:
            errors.append(f"{entry_id}: evidence_class inválido: {entry['evidence_class']}")

        refs = entry.get("source_refs", [])
        if not refs:
            errors.append(f"{entry_id}: verbete sem fonte")

        if entry["status"] == "CONFIRMADO_NORMATIVO" and entry["evidence_class"] == "E7_GITHUB_OPEN_SOURCE":
            errors.append(f"{entry_id}: GitHub não pode, sozinho, confirmar conteúdo normativo")

        for ref in refs:
            if ref.startswith("GH-") and ref not in source_ids:
                errors.append(f"{entry_id}: fonte GitHub não cadastrada: {ref}")

    return errors


def write_status(errors: list[str]) -> None:
    payload = {
        "engine": "GLOSSARY_ENGINE_V1_0",
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
        "note": "Este arquivo é atualizado pelo pipeline local/CI. Mudanças upstream do GitHub não promovem conteúdo técnico automaticamente.",
    }
    STATUS.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    errors = validate()
    write_status(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("GLOSSARY_ENGINE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
