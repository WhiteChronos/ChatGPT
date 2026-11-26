#!/usr/bin/env python3
"""Auditoria read-only de X para planilhas MCE P09; nunca edita o mestre."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from openpyxl import load_workbook

PROFILES = {"p09-50": 57, "adm-gamboa-40": 47}
SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")

def txt(v):
    return "" if v is None else str(v).strip()

def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()

def inspect(workbook, profile="p09-50"):
    if profile not in PROFILES:
        raise ValueError("Perfil MCE desconhecido")
    end = PROFILES[profile]
    wb = load_workbook(workbook, read_only=False, data_only=False)
    data = {"workbook": str(workbook), "sha256": sha(workbook), "profile": profile,
            "sheets": [], "causes": [], "x": [], "missing_x": [],
            "missing_effects": [], "errors": []}
    for n, ws in enumerate(wb.worksheets, 1):
        name = ws.title
        if name != f"FOLHA {n}":
            data["errors"].append("ABA_INVALIDA:" + name)
        if txt(ws["C7"].value).casefold() not in (
            "equipamento / servico / zona", "equipamento / serviço / zona"
        ):
            data["errors"].append("CABECALHO_C7_INVALIDO:" + name)
        if ws.max_row > end:
            data["errors"].append("LINHAS_EXCEDENTES:" + name)
        if ws.max_column > 44:
            data["errors"].append("COLUNAS_EXCEDENTES:" + name)
        titles = {col: txt(ws.cell(5, col).value) for col in range(9, 44)}
        counts = {"sheet": name, "causes": 0, "x": 0}
        for row in range(8, end + 1):
            description, tag, index = [txt(ws.cell(row, col).value) for col in (3, 6, 8)]
            is_cause = bool(description or tag or index)
            valid = []
            for col in range(9, 44):
                cell = ws.cell(row, col)
                mark = txt(cell.value).upper()
                if not mark:
                    continue
                if mark != "X":
                    data["errors"].append("MARCADOR_DESCONHECIDO:" + name + "!" + cell.coordinate)
                    continue
                if not is_cause:
                    data["errors"].append("X_SEM_CAUSA:" + name + "!" + cell.coordinate)
                if not titles[col]:
                    data["errors"].append("X_SEM_TITULO:" + name + "!" + cell.coordinate)
                if is_cause and titles[col]:
                    valid.append(cell.coordinate)
                    data["x"].append({"sheet": name, "cell": cell.coordinate, "row": row,
                                      "index": index, "tag": tag, "effect": titles[col]})
                    counts["x"] += 1
            if is_cause:
                counts["causes"] += 1
                cause = {"sheet": name, "row": row, "index": index, "tag": tag,
                         "description": description, "x_cells": valid}
                data["causes"].append(cause)
                if not valid:
                    data["missing_x"].append(cause)
        for col, title in titles.items():
            if title and not any(
                txt(ws.cell(r, col).value).upper() == "X" and
                any(txt(ws.cell(r, c).value) for c in (3, 6, 8))
                for r in range(8, end + 1)
            ):
                data["missing_effects"].append({"sheet": name, "column": ws.cell(5, col).column_letter,
                                                 "effect": title})
        data["sheets"].append(counts)
    if not wb.worksheets:
        data["errors"].append("SEM_ABAS")
    data["counts"] = {"causes": len(data["causes"]), "x": len(data["x"]),
                      "causes_without_x": len(data["missing_x"]),
                      "effect_columns_without_x": len(data["missing_effects"])}
    return data

def audit(workbook, profile="p09-50", baseline=None, ledger=None,
          expected_causes=None, require_all_effects=True):
    data = inspect(workbook, profile)
    errors = data["errors"]
    approved = []
    if ledger:
        try:
            payload = json.loads(Path(ledger).read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or not isinstance(payload.get("approved_relations"), list):
                raise ValueError("Ledger invalido")
            approved = payload["approved_relations"]
        except (OSError, ValueError):
            errors.append("LEDGER_INVALIDO")
    fields = {"sheet", "cell", "index", "effect", "document", "source_sha256",
              "revision", "location", "verbatim_excerpt", "approver", "status"}
    allowed = set()
    for item in approved:
        if (not isinstance(item, dict) or not fields.issubset(item)
            or item.get("status") != "APROVADO"
            or not isinstance(item.get("source_sha256"), str)
            or not SHA256.fullmatch(item["source_sha256"])
            or any(not txt(item.get(k)) for k in fields - {"status"})):
            errors.append("EVIDENCIA_INCOMPLETA")
            continue
        allowed.add((str(item["sheet"]), str(item["cell"]), str(item["index"]),
                     str(item["effect"]), str(item.get("tag", ""))))
    def identity(x):
        return x["sheet"], x["cell"], str(x["index"]), x["effect"], x["tag"]
    present = {identity(x) for x in data["x"]}
    data["x_without_approved_evidence"] = [x for x in data["x"] if identity(x) not in allowed]
    if data["x_without_approved_evidence"]:
        errors.append("X_SEM_EVIDENCIA_APROVADA")
    if baseline:
        previous = inspect(baseline, profile)
        def causeid(c):
            return (c["sheet"], c["row"], str(c["index"]), c["tag"], c["description"])
        for c in {causeid(x) for x in previous["causes"]} - {causeid(x) for x in data["causes"]}:
            errors.append("CAUSA_REMOVIDA_OU_MODIFICADA:" + repr(c))
        prior_x = {identity(x) for x in previous["x"]}
        for x in prior_x - present:
            errors.append("X_REMOVIDO_OU_MOVIDO:" + repr(x))
        for x in present - prior_x - allowed:
            errors.append("X_ADICIONADO_SEM_APROVACAO:" + repr(x))
        if len(data["sheets"]) < len(previous["sheets"]):
            errors.append("FOLHAS_REMOVIDAS")
    if not data["causes"]:
        errors.append("SEM_CAUSAS")
    if not data["x"]:
        errors.append("MATRIZ_SEM_X")
    if data["missing_x"]:
        errors.append("CAUSA_SEM_X")
    if data["missing_effects"] and require_all_effects:
        errors.append("EFEITO_SEM_X")
    if expected_causes is not None and data["counts"]["causes"] != expected_causes:
        errors.append("QUANTIDADE_CAUSAS_DIVERGENTE")
    data["counts"]["x_without_approved_evidence"] = len(data["x_without_approved_evidence"])
    data["status"] = "BLOCKED" if errors else "PASS_ESTRUTURAL_COM_EVIDENCIAS"
    data["note"] = "Somente leitura: nao equivale a homologacao, QA Excel Windows ou aceite de engenharia."
    return data

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workbook", required=True)
    p.add_argument("--profile", choices=sorted(PROFILES), default="p09-50")
    p.add_argument("--baseline")
    p.add_argument("--ledger")
    p.add_argument("--expected-causes", type=int)
    p.add_argument("--allow-unused-effect-columns", action="store_true")
    p.add_argument("--output")
    p.add_argument("--fail-on-missing", action="store_true")
    a = p.parse_args()
    result = audit(a.workbook, a.profile, a.baseline, a.ledger,
                   a.expected_causes, not a.allow_unused_effect_columns)
    if a.output:
        Path(a.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
    print(json.dumps({"status": result["status"], "counts": result["counts"],
                      "errors": result["errors"][:20]}, ensure_ascii=False))
    if a.fail_on_missing and result["status"] == "BLOCKED":
        raise SystemExit(2)

if __name__ == "__main__":
    main()
