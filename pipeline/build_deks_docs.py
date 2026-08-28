from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "datacenter" / "GLOSSARY_MASTER.json"
SOURCES = ROOT / "datacenter" / "GLOSSARY_SOURCES.json"
GLOSSARY_STATUS = ROOT / "datacenter" / "GLOSSARY_STATUS.json"
DEKS_STATUS = ROOT / "datacenter" / "DEKS_STATUS.json"
SOURCE_STATE = ROOT / "datacenter" / "GLOSSARY_SOURCE_STATE.json"
CANDIDATES = ROOT / "datacenter" / "GLOSSARY_CANDIDATES.json"
GENERATED = ROOT / "docs" / "generated"
GLOSSARY_DIR = GENERATED / "glossary"


def load_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is None:
            raise FileNotFoundError(path)
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def slug(value: str) -> str:
    value = value.casefold().replace("ç", "c")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "item"


def md_escape(value: Any) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def relationship_link(name: str, term_to_path: dict[str, str]) -> str:
    target = term_to_path.get(name.casefold())
    if target:
        return f"[{name}]({target})"
    return name


def entry_page(entry: dict[str, Any], term_to_path: dict[str, str]) -> str:
    term = entry.get("term", entry.get("id", "Sem termo"))
    aliases = entry.get("aliases", [])
    title_suffix = aliases[0] if aliases else entry.get("definition_en", "")
    disciplines = ", ".join(entry.get("discipline", [])) or "TBD"
    relationships = entry.get("relationships", [])
    related_documents = entry.get("related_documents", [])
    source_refs = entry.get("source_refs", [])

    relationship_lines = "\n".join(
        f"- {relationship_link(str(item), term_to_path)}" for item in relationships
    ) or "- Nenhuma relação cadastrada."
    document_lines = "\n".join(f"- {item}" for item in related_documents) or "- TBD"
    source_lines = "\n".join(f"- `{item}`" for item in source_refs) or "- PENDENTE"

    return f"""# {term} — {title_suffix}

<div class="deks-entry-meta">
<span class="deks-chip">{html.escape(entry.get('object_type', 'TBD'))}</span>
<span class="deks-chip">{html.escape(entry.get('status', 'TBD'))}</span>
<span class="deks-chip">{html.escape(entry.get('evidence_class', 'TBD'))}</span>
</div>

## 1. Consulta rápida

| Campo | Informação |
|---|---|
| **Termo / Tag** | `{md_escape(term)}` |
| **Disciplina** | {md_escape(disciplines)} |
| **Tipo de objeto** | {md_escape(entry.get('object_type', 'TBD'))} |
| **Função** | {md_escape(entry.get('function', 'TBD'))} |
| **Padrão de tag** | `{md_escape(entry.get('tag_pattern', 'TBD'))}` |
| **Família de símbolo** | {md_escape(entry.get('symbol_family', 'TBD'))} |
| **Localização** | {md_escape(entry.get('location', 'TBD'))} |

## 2. O que é

{entry.get('definition_pt', 'PENDENTE — NÃO HÁ EVIDÊNCIA SUFICIENTE PARA DEFINIR.')}

## 3. Engenharia

### Relações

{relationship_lines}

### Documentos relacionados

{document_lines}

## 4. Referência e rastreabilidade

**Status:** `{entry.get('status', 'TBD')}`  
**Classe de evidência:** `{entry.get('evidence_class', 'TBD')}`  
**Revisão:** `{entry.get('last_reviewed_at', 'TBD')}`

### Fontes

{source_lines}

!!! warning "Ressalva normativa / de projeto"
    {entry.get('normative_warning', 'Validar sempre contra documentos aprovados do projeto e normas aplicáveis.')}

---

[Voltar ao índice do glossário](../index.md)
"""


def build_index(entries: list[dict[str, Any]], path_by_id: dict[str, str]) -> str:
    disciplines = sorted({item for entry in entries for item in entry.get("discipline", [])})
    object_types = sorted({str(entry.get("object_type", "TBD")) for entry in entries})
    statuses = sorted({str(entry.get("status", "TBD")) for entry in entries})

    def options(values: list[str], label: str) -> str:
        joined = "\n".join(
            f'<option value="{html.escape(value)}">{html.escape(value)}</option>' for value in values
        )
        return f'<option value="">{label}</option>\n{joined}'

    cards: list[str] = []
    for entry in sorted(entries, key=lambda item: str(item.get("term", ""))):
        discipline = " ".join(entry.get("discipline", []))
        aliases = " ".join(entry.get("aliases", []))
        search_text = " ".join(
            [
                str(entry.get("term", "")),
                aliases,
                discipline,
                str(entry.get("object_type", "")),
                str(entry.get("definition_pt", "")),
                str(entry.get("function", "")),
            ]
        )
        path = path_by_id[entry["id"]]
        cards.append(
            "\n".join(
                [
                    f'<article class="deks-card" data-discipline="{html.escape(discipline)}" data-object="{html.escape(str(entry.get("object_type", "")))}" data-status="{html.escape(str(entry.get("status", "")))}" data-search="{html.escape(search_text.casefold())}">',
                    f'  <h3><a href="{html.escape(path)}">{html.escape(str(entry.get("term", "")))}</a></h3>',
                    f'  <p>{html.escape(str(entry.get("definition_pt", "")))}</p>',
                    f'  <small>{html.escape(discipline)} · {html.escape(str(entry.get("status", "")))}</small>',
                    "</article>",
                ]
            )
        )

    return f"""# Glossário interativo

Use a pesquisa global do site ou os filtros abaixo. O índice é gerado automaticamente a partir de `datacenter/GLOSSARY_MASTER.json`.

<div class="deks-controls">
  <input id="deks-text-filter" type="search" placeholder="Filtrar termo, alias, função ou definição" aria-label="Filtrar glossário">
  <select id="deks-discipline-filter" aria-label="Filtrar por disciplina">
    {options(disciplines, 'Todas as disciplinas')}
  </select>
  <select id="deks-object-filter" aria-label="Filtrar por tipo de objeto">
    {options(object_types, 'Todos os tipos')}
  </select>
  <select id="deks-status-filter" aria-label="Filtrar por status">
    {options(statuses, 'Todos os status')}
  </select>
</div>

<div id="deks-result-count" class="deks-result-count"></div>

<div class="deks-grid">
{chr(10).join(cards)}
</div>
"""


def build_sources(sources: list[dict[str, Any]], state: dict[str, Any]) -> str:
    rows = []
    state_map = state.get("sources", {})
    for source in sources:
        current = state_map.get(source.get("id"), {})
        roles = ", ".join(source.get("role", []))
        rows.append(
            "| {id} | {repo} | {authority} | {roles} | {sha} |".format(
                id=md_escape(source.get("id", "")),
                repo=md_escape(source.get("repository", "")),
                authority=md_escape(source.get("authority", "")),
                roles=md_escape(roles),
                sha=md_escape(current.get("sha", "não sincronizado")[:12]),
            )
        )
    body = "\n".join(rows) or "| - | - | - | - | - |"
    return f"""# Fontes e proveniência

GitHub é fonte de tooling/modelo/software e **não** autoridade normativa por si só. A hierarquia completa está no Prompt-Mestre DEKS.

| ID | Repositório | Autoridade | Uso | SHA monitorado |
|---|---|---|---|---|
{body}
"""


def build_status_page(glossary_status: dict[str, Any], deks_status: dict[str, Any], candidates: dict[str, Any]) -> str:
    pending = [item for item in candidates.get("items", []) if item.get("status") == "PENDING_TECHNICAL_REVIEW"]
    candidate_lines = "\n".join(
        f"- `{item.get('source_id')}` → `{item.get('to_sha', '')[:12]}` — revisão técnica pendente"
        for item in pending
    ) or "- Nenhum candidato upstream pendente."
    return f"""# Estado do sistema

| Motor | OK | Erros | Avisos |
|---|---:|---:|---:|
| Glossary Engine | {glossary_status.get('ok', 'TBD')} | {glossary_status.get('error_count', 'TBD')} | - |
| DEKS Engine | {deks_status.get('ok', 'TBD')} | {deks_status.get('error_count', 'TBD')} | {deks_status.get('warning_count', 'TBD')} |

## Atualizações externas aguardando revisão

{candidate_lines}

!!! info "Governança"
    Mudança upstream em GitHub gera candidato. Não promove automaticamente conteúdo técnico ou normativo.
"""


def build_knowledge_map(entries: list[dict[str, Any]]) -> str:
    term_to_node: dict[str, str] = {}
    node_lines: list[str] = []
    edge_lines: list[str] = []

    for index, entry in enumerate(entries, start=1):
        node = f"N{index}"
        term = str(entry.get("term", entry.get("id", node)))
        term_to_node[term.casefold()] = node
        node_lines.append(f'{node}["{term.replace(chr(34), chr(39))}"]')

    external_nodes: dict[str, str] = {}
    external_counter = 0
    for entry in entries:
        source_node = term_to_node[str(entry.get("term", "")).casefold()]
        for relation in entry.get("relationships", []):
            relation_text = str(relation)
            target = term_to_node.get(relation_text.casefold())
            if not target:
                if relation_text not in external_nodes:
                    external_counter += 1
                    target = f"X{external_counter}"
                    external_nodes[relation_text] = target
                    safe = relation_text.replace('"', "'")
                    node_lines.append(f'{target}(["{safe}"])')
                else:
                    target = external_nodes[relation_text]
            edge_lines.append(f"{source_node} --> {target}")

    diagram = "\n".join(["graph LR", *[f"  {line}" for line in node_lines], *[f"  {line}" for line in edge_lines]])
    return f"""# Mapa de conhecimento

O diagrama é gerado a partir das relações atualmente registradas no datacenter. Nós arredondados representam conceitos relacionados ainda não cadastrados como verbetes canônicos.

```mermaid
{diagram}
```
"""


def main() -> int:
    master = load_json(MASTER)
    sources = load_json(SOURCES)
    glossary_status = load_json(GLOSSARY_STATUS, {"ok": "não executado", "error_count": "TBD"})
    deks_status = load_json(DEKS_STATUS, {"ok": "não executado", "error_count": "TBD", "warning_count": "TBD"})
    source_state = load_json(SOURCE_STATE, {"sources": {}})
    candidates = load_json(CANDIDATES, {"items": []})

    entries = master.get("entries", [])
    GLOSSARY_DIR.mkdir(parents=True, exist_ok=True)

    path_by_id: dict[str, str] = {}
    term_to_path: dict[str, str] = {}
    for entry in entries:
        filename = f"{slug(str(entry['id']))}.md"
        relative = f"glossary/{filename}"
        path_by_id[entry["id"]] = relative
        term_to_path[str(entry.get("term", "")).casefold()] = filename
        for alias in entry.get("aliases", []):
            term_to_path[str(alias).casefold()] = filename

    for entry in entries:
        filename = Path(path_by_id[entry["id"]]).name
        write_text(GLOSSARY_DIR / filename, entry_page(entry, term_to_path))

    write_text(GENERATED / "glossary" / "index.md", build_index(entries, {key: Path(value).name for key, value in path_by_id.items()}))
    write_text(GENERATED / "sources.md", build_sources(sources.get("sources", []), source_state))
    write_text(GENERATED / "status.md", build_status_page(glossary_status, deks_status, candidates))
    write_text(GENERATED / "knowledge-map.md", build_knowledge_map(entries))

    print(f"DEKS_DOCS_BUILT entries={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
