from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "datacenter" / "GLOSSARY_MASTER.json"
REGISTRY = ROOT / "datacenter" / "INGESTION_SOURCE_REGISTRY.json"
STAGING_DIR = ROOT / "ingestion" / "staging"
OUTPUT = ROOT / "docs" / "generated" / "glossary" / "interactive.md"


def load_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is None:
            raise FileNotFoundError(path)
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def pretty(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)
    if value is None:
        return "—"
    return str(value)


def compact(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return "; ".join(f"{key}: {compact(val)}" for key, val in value.items())
    if value is None:
        return ""
    return str(value)


def iter_staging_records() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if not STAGING_DIR.exists():
        return items
    for path in sorted(STAGING_DIR.glob("*.json")):
        batch = load_json(path, {})
        for record in batch.get("records", []):
            normalized = dict(record)
            normalized["batch_id"] = batch.get("batch_id", "TBD")
            normalized["source_id"] = batch.get("source_id", "TBD")
            normalized["source_revision"] = batch.get("source_revision", "TBD")
            normalized["batch_file"] = path.name
            items.append(normalized)
    return items


def symbol_svg(payload: dict[str, Any]) -> str:
    geometry = payload.get("base_geometry", "")
    marking = payload.get("location_marking", "none")
    stroke = "currentColor"
    shapes: list[str] = []

    if geometry == "circle":
        shapes.append(f'<circle cx="50" cy="50" r="28" fill="none" stroke="{stroke}" stroke-width="3"/>')
    elif geometry == "circle_inside_square":
        shapes.append(f'<rect x="18" y="18" width="64" height="64" fill="none" stroke="{stroke}" stroke-width="3"/>')
        shapes.append(f'<circle cx="50" cy="50" r="22" fill="none" stroke="{stroke}" stroke-width="3"/>')
    elif geometry == "hexagon":
        shapes.append(f'<polygon points="50,16 78,32 78,68 50,84 22,68 22,32" fill="none" stroke="{stroke}" stroke-width="3"/>')
    elif geometry == "diamond_inside_square":
        shapes.append(f'<rect x="18" y="18" width="64" height="64" fill="none" stroke="{stroke}" stroke-width="3"/>')
        shapes.append(f'<polygon points="50,26 74,50 50,74 26,50" fill="none" stroke="{stroke}" stroke-width="3"/>')
    else:
        shapes.append(f'<rect x="18" y="18" width="64" height="64" rx="8" fill="none" stroke="{stroke}" stroke-width="3"/>')

    if marking == "one_solid_horizontal_bar":
        shapes.append(f'<line x1="18" y1="50" x2="82" y2="50" stroke="{stroke}" stroke-width="3"/>')
    elif marking == "one_dashed_horizontal_bar":
        shapes.append(f'<line x1="18" y1="50" x2="82" y2="50" stroke="{stroke}" stroke-width="3" stroke-dasharray="7 5"/>')
    elif marking == "two_solid_horizontal_bars":
        shapes.append(f'<line x1="18" y1="44" x2="82" y2="44" stroke="{stroke}" stroke-width="3"/>')
        shapes.append(f'<line x1="18" y1="56" x2="82" y2="56" stroke="{stroke}" stroke-width="3"/>')

    return '<svg class="deks-symbol-svg" viewBox="0 0 100 100" role="img" aria-label="Pré-visualização geométrica do símbolo">' + "".join(shapes) + "</svg>"


def table_rows(mapping: dict[str, Any]) -> str:
    rows: list[str] = []
    for key, value in mapping.items():
        rows.append(f"<tr><th>{esc(key)}</th><td><pre>{esc(pretty(value))}</pre></td></tr>")
    return "".join(rows) or "<tr><td colspan=\"2\">Sem dados cadastrados.</td></tr>"


def summary_from_payload(payload: dict[str, Any], external_id: str) -> str:
    for key in (
        "definition_pt",
        "definition",
        "description",
        "function",
        "document_title",
        "name",
        "standard",
        "tag",
    ):
        value = payload.get(key)
        if value:
            return compact(value)
    return f"Registro técnico em staging: {external_id}."


def canonical_card(entry: dict[str, Any]) -> str:
    title = str(entry.get("term", entry.get("id", "Sem termo")))
    source_refs = entry.get("source_refs", [])
    source = source_refs[0] if source_refs else "TBD"
    disciplines = compact(entry.get("discipline", [])) or "TBD"
    summary = str(entry.get("definition_pt", "PENDENTE — NÃO HÁ EVIDÊNCIA SUFICIENTE PARA DEFINIR."))
    search_text = " ".join(
        [
            title,
            compact(entry.get("aliases", [])),
            disciplines,
            str(entry.get("object_type", "")),
            summary,
            str(entry.get("function", "")),
            source,
        ]
    ).casefold()
    detail = {
        "ID": entry.get("id", "TBD"),
        "Termo / Tag": title,
        "Aliases": entry.get("aliases", []),
        "Disciplina": entry.get("discipline", []),
        "Tipo de objeto": entry.get("object_type", "TBD"),
        "Definição": entry.get("definition_pt", "TBD"),
        "Função": entry.get("function", "TBD"),
        "Padrão de tag": entry.get("tag_pattern", "TBD"),
        "Família de símbolo": entry.get("symbol_family", "TBD"),
        "Localização": entry.get("location", "TBD"),
        "Relações": entry.get("relationships", []),
        "Documentos relacionados": entry.get("related_documents", []),
        "Fontes": source_refs,
        "Classe de evidência": entry.get("evidence_class", "TBD"),
        "Status": entry.get("status", "TBD"),
        "Última revisão": entry.get("last_reviewed_at", "TBD"),
        "Ressalva": entry.get("normative_warning", "TBD"),
    }
    return f"""
<article class="deks-glossary-card" data-scope="canonical" data-source="{esc(source)}" data-entity="{esc(entry.get('object_type', 'TBD'))}" data-status="{esc(entry.get('status', 'TBD'))}" data-evidence="{esc(entry.get('evidence_class', 'TBD'))}" data-title="{esc(title.casefold())}" data-search="{esc(search_text)}">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-approved">BASE APROVADA</span><span class="deks-badge">{esc(entry.get('evidence_class', 'TBD'))}</span></div>
  <h3>{esc(title)}</h3>
  <p>{esc(summary)}</p>
  <div class="deks-card-meta">{esc(disciplines)} · {esc(entry.get('object_type', 'TBD'))} · {esc(entry.get('status', 'TBD'))}</div>
  <button class="deks-open-entry" type="button">Abrir ficha técnica</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-approved">BASE APROVADA — leitura do datacenter canônico</div>
    <h2>{esc(title)}</h2>
    <table class="deks-detail-table">{table_rows(detail)}</table>
  </template>
</article>
""".strip()


def staging_card(record: dict[str, Any]) -> str:
    payload = record.get("payload", {}) or {}
    provenance = record.get("provenance", {}) or {}
    external_id = str(record.get("external_id", record.get("ingestion_id", "Sem ID")))
    entity = str(record.get("entity_type", "TBD"))
    source = str(record.get("source_id", "TBD"))
    status = str(record.get("review_status", "REVIEW_REQUIRED"))
    evidence = str(record.get("evidence_class", "TBD"))
    summary = summary_from_payload(payload, external_id)
    search_text = " ".join(
        [external_id, entity, source, evidence, status, compact(payload), compact(provenance)]
    ).casefold()
    symbol_preview = symbol_svg(payload) if entity == "symbol" else ""
    dimension = payload.get("explicit_dimension_mm")
    if entity == "symbol":
        if dimension is not None:
            dimension_note = f"Dimensão explícita na folha: {dimension} mm."
        else:
            dimension_note = "Dimensão não explícita para esta célula na folha de referência."
    else:
        dimension_note = ""
    detail = {
        "Ingestion ID": record.get("ingestion_id", "TBD"),
        "Batch": record.get("batch_id", "TBD"),
        "Arquivo do batch": record.get("batch_file", "TBD"),
        "Fonte": source,
        "Revisão da fonte": record.get("source_revision", "TBD"),
        "Tipo de entidade": entity,
        "External ID": external_id,
        "Classe de evidência": evidence,
        "Review status": status,
        "Auto-promoted": record.get("auto_promoted", False),
        "Payload": payload,
        "Proveniência": provenance,
    }
    return f"""
<article class="deks-glossary-card deks-glossary-card-staging" data-scope="staging" data-source="{esc(source)}" data-entity="{esc(entity)}" data-status="{esc(status)}" data-evidence="{esc(evidence)}" data-title="{esc(external_id.casefold())}" data-search="{esc(search_text)}">
  <div class="deks-card-topline"><span class="deks-badge deks-badge-review">STAGING — NÃO APROVADO</span><span class="deks-badge">{esc(evidence)}</span></div>
  {symbol_preview}
  <h3>{esc(external_id)}</h3>
  <p>{esc(summary)}</p>
  {f'<p class="deks-dimension-note">{esc(dimension_note)}</p>' if dimension_note else ''}
  <div class="deks-card-meta">{esc(source)} · {esc(entity)} · {esc(status)}</div>
  <button class="deks-open-entry" type="button">Abrir registro de revisão</button>
  <template class="deks-entry-detail">
    <div class="deks-detail-banner deks-detail-review">STAGING — NÃO APROVADO. Ingestão não é aprovação.</div>
    {symbol_preview}
    <h2>{esc(external_id)}</h2>
    <table class="deks-detail-table">{table_rows(detail)}</table>
  </template>
</article>
""".strip()


def options(values: set[str], label: str) -> str:
    rows = [f'<option value="">{esc(label)}</option>']
    for value in sorted(item for item in values if item):
        rows.append(f'<option value="{esc(value)}">{esc(value)}</option>')
    return "".join(rows)


def build_page(master: dict[str, Any], registry: dict[str, Any], staging: list[dict[str, Any]]) -> str:
    canonical = master.get("entries", [])
    pending_sources = [item for item in registry.get("sources", []) if not item.get("enabled", False)]
    review_required = [item for item in staging if item.get("review_status") == "REVIEW_REQUIRED"]
    symbols = [item for item in staging if item.get("entity_type") == "symbol"]

    cards = [canonical_card(item) for item in canonical]
    cards.extend(staging_card(item) for item in staging)

    sources = {str(item.get("source_refs", ["TBD"])[0]) for item in canonical if item.get("source_refs")}
    sources.update(str(item.get("source_id", "TBD")) for item in staging)
    entities = {str(item.get("object_type", "TBD")) for item in canonical}
    entities.update(str(item.get("entity_type", "TBD")) for item in staging)
    statuses = {str(item.get("status", "TBD")) for item in canonical}
    statuses.update(str(item.get("review_status", "TBD")) for item in staging)
    evidences = {str(item.get("evidence_class", "TBD")) for item in canonical}
    evidences.update(str(item.get("evidence_class", "TBD")) for item in staging)

    pending_rows = "".join(
        f'<li><strong>{esc(item.get("name", item.get("source_id", "TBD")))}</strong> — {esc(item.get("status", "PENDENTE"))}</li>'
        for item in pending_sources
    ) or "<li>Nenhuma fonte bloqueada.</li>"

    return f"""# Glossário técnico interativo

<div class="deks-glossary-hero">
  <p class="deks-eyebrow">DEKS · Digital Engineering Knowledge System</p>
  <h2>Glossário Rev4.2 → AUTOMAÇÃO DM → tags/símbolos → P&amp;ID → Instrument Index/I/O → C&amp;E → datasheets</h2>
  <p>Consulta unificada com separação rígida entre <strong>base aprovada</strong> e <strong>staging técnico</strong>. Registros em staging nunca são apresentados como conhecimento aprovado.</p>
</div>

<div class="deks-metrics">
  <div class="deks-metric"><strong>{len(canonical)}</strong><span>verbetes na base aprovada</span></div>
  <div class="deks-metric"><strong>{len(staging)}</strong><span>registros em staging</span></div>
  <div class="deks-metric"><strong>{len(review_required)}</strong><span>REVIEW_REQUIRED</span></div>
  <div class="deks-metric"><strong>{len(symbols)}</strong><span>símbolos AUTOMAÇÃO DM</span></div>
  <div class="deks-metric"><strong>{len(pending_sources)}</strong><span>fontes bloqueadas por falta de arquivo</span></div>
</div>

<div class="deks-governance-callout">
  <strong>Regra de governança:</strong> INGESTÃO NÃO É APROVAÇÃO. O gerador lê <code>GLOSSARY_MASTER.json</code> em modo somente leitura e exibe staging separado.
</div>

<div class="deks-scope-tabs" role="group" aria-label="Escopo do glossário">
  <button type="button" class="deks-scope-button is-active" data-glossary-scope="all">Tudo</button>
  <button type="button" class="deks-scope-button" data-glossary-scope="canonical">Base aprovada</button>
  <button type="button" class="deks-scope-button" data-glossary-scope="staging">Staging</button>
  <button type="button" class="deks-scope-button" data-glossary-scope="symbol">Símbolos DM</button>
</div>

<div class="deks-controls deks-glossary-controls">
  <input id="deks-glossary-search" type="search" placeholder="Pesquisar termo, tag, função, símbolo, fonte ou documento" aria-label="Pesquisar no glossário">
  <select id="deks-glossary-source" aria-label="Filtrar por fonte">{options(sources, 'Todas as fontes')}</select>
  <select id="deks-glossary-entity" aria-label="Filtrar por tipo">{options(entities, 'Todos os tipos')}</select>
  <select id="deks-glossary-status" aria-label="Filtrar por status">{options(statuses, 'Todos os status')}</select>
  <select id="deks-glossary-evidence" aria-label="Filtrar por evidência">{options(evidences, 'Todas as classes de evidência')}</select>
  <select id="deks-glossary-sort" aria-label="Ordenar resultados">
    <option value="title">Ordenar por termo / ID</option>
    <option value="source">Ordenar por fonte</option>
    <option value="entity">Ordenar por tipo</option>
    <option value="status">Ordenar por status</option>
  </select>
</div>

<div class="deks-result-row">
  <div id="deks-glossary-result-count" class="deks-result-count"></div>
  <button id="deks-glossary-reset" type="button" class="deks-reset-button">Limpar filtros</button>
</div>

<div id="deks-glossary-grid" class="deks-glossary-grid">
{chr(10).join(cards)}
</div>

<div id="deks-glossary-empty" class="deks-empty-state" hidden>Nenhum registro corresponde aos filtros selecionados.</div>

<aside id="deks-detail-panel" class="deks-detail-panel" hidden aria-live="polite">
  <div class="deks-detail-panel-toolbar"><button id="deks-detail-close" type="button" aria-label="Fechar ficha">Fechar</button></div>
  <div id="deks-detail-content"></div>
</aside>

## Fontes ainda bloqueadas

<ul>
{pending_rows}
</ul>

!!! warning "Dados pendentes"
    Instrument Index/I/O, C&amp;E e datasheets só entram no glossário interativo quando seus arquivos técnicos autônomos forem ingeridos. Até lá: **PENDENTE — NÃO HÁ EVIDÊNCIA SUFICIENTE PARA DEFINIR.**
"""


def main() -> int:
    master = load_json(MASTER)
    registry = load_json(REGISTRY, {"sources": []})
    staging = iter_staging_records()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_page(master, registry, staging).rstrip() + "\n", encoding="utf-8")
    print(f"INTERACTIVE_GLOSSARY_BUILT canonical={len(master.get('entries', []))} staging={len(staging)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
