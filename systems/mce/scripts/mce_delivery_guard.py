#!/usr/bin/env python3
"""Gate independente e somente leitura para entrega de MCE funcional.

Executar DEPOIS de mce_workflow.py apply/audit, nunca editar workbook aqui.
Um artefato de layout ou um caderno de propostas nao substitui MCE_XLSX.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
from openpyxl import load_workbook


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def inspect(workspace: Path, changes_path: Path, profile: str = 'p09-50') -> dict:
    errors = []
    def err(code: str) -> None:
        if code not in errors:
            errors.append(code)
    def read_json(path: Path):
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            err('ARQUIVO_INVALIDO:' + path.name)
            return None

    state = read_json(workspace / 'state.json') or {}
    contract = read_json(workspace / 'contract.json') or {}
    audit = read_json(workspace / 'AUDITORIA_MCE.json') or {}
    diffs = read_json(workspace / 'ALTERACOES_MCE.json')
    changes = read_json(changes_path)
    master = workspace / 'base' / 'modelo.xlsx'
    output = workspace / 'output' / 'MCE_PRELIMINAR.xlsx'

    if state.get('status') != 'MCE_PRELIMINAR_PARA_REVISAO':
        err('EXECUTOR_CANONICO_NAO_CONCLUIDO')
    if state.get('template_classification') != 'MODELO_APROVADO' or contract.get('model_approved') is not True:
        err('MODELO_NAO_HOMOLOGADO')
    approval = state.get('approval') or {}
    if approval.get('decision') != 'AUTORIZO_ELABORACAO_MCE' or not approval.get('source_manifest_sha256') or approval.get('source_manifest_sha256') != state.get('source_manifest_sha256'):
        err('APROVACAO_NAO_VINCULADA_AS_FONTES')
    if contract.get('template_sha256') != state.get('template_sha256'):
        err('CONTRATO_MODELO_HASH_DIVERGENTE')
    if audit.get('passed') is not True:
        err('AUDITORIA_CANONICA_REPROVADA')
    if not master.is_file() or digest(master) != state.get('template_sha256'):
        err('MESTRE_HASH_DIVERGENTE')
    if not output.is_file():
        err('MCE_XLSX_AUSENTE')
    elif digest(output) != state.get('output_sha256'):
        err('MCE_XLSX_HASH_DIVERGENTE')
    if not isinstance(diffs, list) or not diffs:
        err('DIFF_CANONICO_AUSENTE')
        diffs = []
    if not isinstance(changes, list) or not changes:
        err('LEDGER_DE_EVIDENCIAS_AUSENTE')
        changes = []

    by_diff = {(d.get('sheet'), d.get('cell')): d for d in diffs if isinstance(d, dict)}
    by_change = {(c.get('sheet'), c.get('cell')): c for c in changes if isinstance(c, dict)}
    docs = {d.get('name'): d for d in state.get('sources', []) if isinstance(d, dict)}
    causes = 0
    marks = 0
    cause_without_x = []
    x_untracked = []
    if output.is_file():
        try:
            wb = load_workbook(output, read_only=False, data_only=False)
            baseline = load_workbook(master, read_only=False, data_only=False) if master.is_file() else None
            if not wb.sheetnames or wb.sheetnames != [f'FOLHA {i}' for i in range(1, len(wb.sheetnames) + 1)]:
                err('ABAS_FORA_DO_PADRAO_MCE')
            last_row = {'p09-50': 57, 'p09-l50': 50}.get(profile)
            if last_row is None:
                err('PERFIL_DESCONHECIDO')
                last_row = 57
            for sheet in wb:
                effects = {col for col in range(9, 44) if str(sheet.cell(5, col).value or '').strip()}
                for row in range(8, last_row + 1):
                    is_cause = any(sheet[f'{col}{row}'].value is not None for col in ('C', 'F', 'H'))
                    found = 0
                    for col in range(9, 44):
                        cell = sheet.cell(row, col)
                        if str(cell.value or '').strip().upper() != 'X':
                            continue
                        marks += 1
                        found += 1
                        k = (sheet.title, cell.coordinate)
                        if col not in effects or not is_cause:
                            err('X_SEM_CAUSA_OU_EFEITO')
                        diff = by_diff.get(k)
                        change = by_change.get(k)
                        if diff is None:
                            if (baseline is None or sheet.title not in baseline
                                or str(baseline[sheet.title][cell.coordinate].value or '').strip().upper() != 'X'):
                                x_untracked.append(f'{sheet.title}!{cell.coordinate}')
                            continue
                        if diff.get('after') != 'X' or change is None or change.get('new_text') != 'X':
                            x_untracked.append(f'{sheet.title}!{cell.coordinate}')
                            continue
                        source = docs.get(change.get('source_name'))
                        if (change.get('evidence_status') != 'DOCUMENTADO'
                            or not source or source.get('sha256') != change.get('source_sha256')
                            or not change.get('verbatim_excerpt')
                            or not change.get('source_location')
                            or not change.get('reference_revision')
                            or (source.get('extension') not in ('.txt', '.md') and change.get('manual_evidence_verified') is not True)):
                            x_untracked.append(f'{sheet.title}!{cell.coordinate}')
                    if is_cause:
                        causes += 1
                        if not found:
                            cause_without_x.append(f'{sheet.title}!{row}')
            if marks == 0:
                err('MATRIZ_SEM_X')
            if causes == 0:
                err('MATRIZ_SEM_CAUSAS')
            if cause_without_x:
                err('CAUSAS_SEM_X')
            if x_untracked:
                err('X_SEM_EVIDENCIA_INDIVIDUAL')
        except Exception as exc:
            err('XLSX_ILEGIVEL:' + type(exc).__name__)
    return {
        'status': 'PASS_ESTRUTURAL_PRELIMINAR' if not errors else 'MCE_XLSX=NAO_EMITIDO_BLOQUEADO',
        'causes': causes, 'x_total': marks,
        'causes_without_x': cause_without_x, 'x_without_evidence': x_untracked,
        'errors': errors,
        'nota': 'PASS nao e aceite FAT/SAT, homologacao nem QA Excel Windows.'
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--changes', type=Path, required=True, help='JSON exato aprovado e aplicado pelo executor canonico')
    parser.add_argument('--profile', choices=['p09-50', 'p09-l50'], default='p09-50')
    args = parser.parse_args()
    result = inspect(args.workspace, args.changes, args.profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result['status'] == 'PASS_ESTRUTURAL_PRELIMINAR' else 2)


if __name__ == '__main__':
    main()
