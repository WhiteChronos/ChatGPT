#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from awesome_llm_apps_catalog import build_catalog, build_summary


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, prefix=f'.{path.name}.', suffix='.tmp', delete=False) as fh:
        json.dump(value, fh, indent=2, sort_keys=True)
        fh.write('\n')
        temp = Path(fh.name)
    temp.replace(path)


def validate_catalog(catalog: dict[str, Any], schema: dict[str, Any]) -> None:
    if not isinstance(catalog, dict):
        raise ValueError('catalog must be an object')
    required_top = set(schema.get('required', []))
    missing = sorted(required_top - catalog.keys())
    if missing:
        raise ValueError(f'catalog missing required fields: {missing}')
    expected_version = schema.get('properties', {}).get('schema_version', {}).get('const')
    if expected_version is not None and catalog.get('schema_version') != expected_version:
        raise ValueError(f'catalog schema_version must be {expected_version}')
    if not isinstance(catalog.get('upstream_commit'), str) or not catalog['upstream_commit']:
        raise ValueError('catalog upstream_commit must be a non-empty string')
    entries = catalog.get('entries')
    if not isinstance(entries, list):
        raise ValueError('catalog entries must be a list')

    entry_schema = schema.get('$defs', {}).get('entry', {})
    entry_required = set(entry_schema.get('required', []))
    props = entry_schema.get('properties', {})
    ids: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f'entry {index} must be an object')
        missing_entry = sorted(entry_required - entry.keys())
        if missing_entry:
            raise ValueError(f'entry {index} missing required fields: {missing_entry}')
        entry_id = entry.get('id')
        if not isinstance(entry_id, str) or not entry_id:
            raise ValueError(f'entry {index} id must be a non-empty string')
        if entry_id in ids:
            raise ValueError(f'duplicate catalog id: {entry_id}')
        ids.add(entry_id)
        for field in ('source_type', 'execution_class'):
            allowed = props.get(field, {}).get('enum')
            if allowed and entry.get(field) not in allowed:
                raise ValueError(f'entry {entry_id} has invalid {field}: {entry.get(field)!r}')
        for field in ('network_required','credentials_required','background_capable','self_modifying','high_stakes_domain'):
            if not isinstance(entry.get(field), bool):
                raise ValueError(f'entry {entry_id} {field} must be boolean')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Build the WhiteChronos Awesome LLM Apps catalog.')
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--catalog', required=True, type=Path)
    parser.add_argument('--summary', required=True, type=Path)
    parser.add_argument('--schema', required=True, type=Path)
    args = parser.parse_args(argv)

    schema = json.loads(args.schema.read_text(encoding='utf-8'))
    catalog = build_catalog(args.root, args.commit)
    validate_catalog(catalog, schema)
    summary = build_summary(catalog)
    _atomic_json(args.catalog, catalog)
    _atomic_json(args.summary, summary)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
