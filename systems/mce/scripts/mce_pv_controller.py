#!/usr/bin/env python3
"""Create immutable PV copies of audited MCE XLSX files; never edit cells.

A PV is a working version, NOT an engineering approval or a final revision.
The canonical MCE executor remains the sole editor of the underlying workbook.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import zipfile
from pathlib import Path

LEDGER = 'pv_versions.jsonl'
NAME_RE = re.compile(r'^([A-Za-z0-9][A-Za-z0-9._=-]{0,159}) - PV ([0-9]{2,})\.xlsx$')
DOCUMENT_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._=-]{0,159}$')
GENESIS = '0' * 64


class PVBlocked(ValueError):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def document_name(name: str) -> str:
    if (not isinstance(name, str) or not DOCUMENT_RE.fullmatch(name)
            or name.endswith((' ', '.')) or 'PV ' in name):
        raise PVBlocked('Nome do documento invalido ou ja versionado')
    return name


def pv_filename(name: str, number: int) -> str:
    document_name(name)
    if type(number) is not int or not 1 <= number <= 9999:
        raise PVBlocked('PV deve ser inteiro positivo de 1 a 9999')
    marker = f'{number:02d}'
    return f'{name} - PV {marker}.xlsx'


def parse_pv_filename(value: str) -> tuple[str, int]:
    match = NAME_RE.fullmatch(value or '')
    if not match:
        raise PVBlocked('Nome da MCE fora do padrao PV')
    name, version = match.group(1), match.group(2)
    parsed = int(version)
    if parsed < 1 or version != f'{parsed:02d}':
        raise PVBlocked('Numeracao PV nao canonica')
    document_name(name)
    return name, parsed


def bounded_file(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise PVBlocked('A fonte deve ser relativa ao workspace privado')
    path = root / relative
    if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != root.parent):
        raise PVBlocked('Links simbolicos nao permitidos')
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
        raise PVBlocked('Fonte fora do workspace ou inexistente')
    if path.stat().st_nlink != 1:
        raise PVBlocked('Hardlinks nao permitidos')
    return resolved


def canonical_record(record: dict) -> bytes:
    return json.dumps(record, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode('utf-8')


def read_ledger(ledger: Path, dest_root: Path) -> list[dict]:
    if ledger.is_symlink():
        raise PVBlocked('Ledger por link nao permitido')
    if not ledger.exists():
        return []
    if not ledger.is_file() or ledger.stat().st_size > 4 * 1024 * 1024:
        raise PVBlocked('Ledger invalido')
    records = []
    prev = GENESIS
    by_doc: dict[str, int] = {}
    for line in ledger.read_text(encoding='utf-8').splitlines():
        try:
            obj = json.loads(line)
            payload = {k: v for k, v in obj.items() if k != 'digest'}
            calc = hashlib.sha256(canonical_record(payload)).hexdigest()
            name, number = parse_pv_filename(obj['filename'])
            if obj['digest'] != calc or obj['prev_digest'] != prev:
                raise PVBlocked('Cadeia de SHA do ledger adulterada')
            if obj['document_name'] != name or obj['pv_number'] != number:
                raise PVBlocked('Documento/numero PV incompativel')
            if number != by_doc.get(name, 0) + 1:
                raise PVBlocked('Sequencia PV descontinua')
            target = dest_root / obj['filename']
            if target.is_symlink() or not target.is_file() or sha256(target) != obj['sha256']:
                raise PVBlocked('Arquivo PV arquivado ausente ou alterado')
            by_doc[name] = number
            prev = obj['digest']
            records.append(obj)
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise PVBlocked('Ledger PV invalido: ' + str(exc)) from exc
    return records


def stage(root: Path, source: str, name: str, expected_sha256: str) -> dict:
    root = root.resolve()
    name = document_name(name)
    if not isinstance(expected_sha256, str) or not re.fullmatch(r'[0-9a-f]{64}', expected_sha256):
        raise PVBlocked('SHA-256 esperado obrigatorio')
    src = bounded_file(root, source)
    if src.suffix.lower() != '.xlsx' or not zipfile.is_zipfile(src):
        raise PVBlocked('Fonte deve ser XLSX OOXML valido')
    with zipfile.ZipFile(src) as archive:
        if archive.testzip() is not None or 'xl/workbook.xml' not in archive.namelist():
            raise PVBlocked('OOXML invalido')
    if sha256(src) != expected_sha256:
        raise PVBlocked('SHA-256 da fonte divergente')
    folder = root / 'pv'
    if folder.is_symlink():
        raise PVBlocked('Diretorio de versoes por link nao permitido')
    folder.mkdir(exist_ok=True)
    ledger = folder / LEDGER
    records = read_ledger(ledger, folder)
    mine = [r for r in records if r['document_name'] == name]
    previous = mine[-1] if mine else None
    if previous and previous['sha256'] == expected_sha256:
        raise PVBlocked('Sem mudanca de bytes: nao emitir PV seguinte identica')
    number = len(mine) + 1
    filename = pv_filename(name, number)
    target = folder / filename
    if target.exists() or target.is_symlink():
        raise PVBlocked('Proibido sobrescrever PV existente')
    fd = os.open(str(target), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, 'wb') as out, src.open('rb') as incoming:
            for chunk in iter(lambda: incoming.read(1024 * 1024), b''):
                out.write(chunk)
            out.flush()
            os.fsync(out.fileno())
        if sha256(target) != expected_sha256:
            raise PVBlocked('Divergencia na copia PV')
        payload = {
            'schema': 'mce.pv.version.v1', 'document_name': name,
            'filename': filename, 'pv_number': number,
            'sha256': expected_sha256, 'source_sha256': expected_sha256,
            'previous_pv_sha256': previous['sha256'] if previous else None,
            'prev_digest': records[-1]['digest'] if records else GENESIS,
            'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
            'state': 'PRELIMINAR_NAO_HOMOLOGADA',
            'engineering_approved': False, 'production_complete': False,
        }
        record = {**payload, 'digest': hashlib.sha256(canonical_record(payload)).hexdigest()}
        if ledger.is_symlink():
            raise PVBlocked('Ledger alterado durante operacao')
        with ledger.open('a', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + '\n')
            f.flush()
            os.fsync(f.fileno())
        return {'filename': filename, 'pv_number': number, 'sha256': expected_sha256,
                'state': record['state'], 'engineering_approved': False,
                'ledger': str(ledger), 'file': str(target)}
    except Exception:
        target.unlink(missing_ok=True)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description='Versiona copia MCE sem editar XLSX')
    parser.add_argument('--workspace', required=True, type=Path)
    parser.add_argument('--source', required=True)
    parser.add_argument('--document-name', required=True)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(stage(args.workspace, args.source, args.document_name, args.sha256),
                         ensure_ascii=False))
        return 0
    except (PVBlocked, OSError, zipfile.BadZipFile) as exc:
        print('PV_BLOQUEADA: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
