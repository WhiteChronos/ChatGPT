#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from awesome_llm_apps_catalog import build_catalog, build_summary


def _matches_type(value, kind):
    if kind == 'null':
        return value is None
    if kind == 'string':
        return isinstance(value, str)
    if kind == 'boolean':
        return isinstance(value, bool)
    if kind == 'array':
        return isinstance(value, list)
    if kind == 'object':
        return isinstance(value, dict)
    if kind == 'integer':
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == 'number':
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    raise ValueError(f'unsupported schema type: {kind}')


def _validate_node(value, schema, path):
    if 'const' in schema and value != schema['const']:
        raise ValueError(f'{path} must equal {schema["const"]!r}')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'{path} not in allowed enum')
    kinds = schema.get('type')
    if kinds:
        kinds = [kinds] if isinstance(kinds, str) else kinds
        if not any(_matches_type(value, kind) for kind in kinds):
            raise ValueError(f'{path} has invalid type')
    if isinstance(value, str) and 'minLength' in schema and len(value) < schema['minLength']:
        raise ValueError(f'{path} is too short')
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                raise ValueError(f'{path} missing {key}')
        properties = schema.get('properties', {})
        if schema.get('additionalProperties') is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                raise ValueError(f'{path} has unsupported properties: {", ".join(extra)}')
        for key, child in properties.items():
            if key in value:
                _validate_node(value[key], child, f'{path}.{key}')
    if isinstance(value, list) and 'items' in schema:
        for i, item in enumerate(value):
            _validate_node(item, schema['items'], f'{path}[{i}]')


def validate_supported(catalog: dict, schema: dict):
    _validate_node(catalog, schema, 'catalog')


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True)
    p.add_argument('--commit', required=True)
    p.add_argument('--catalog', required=True)
    p.add_argument('--summary', required=True)
    p.add_argument('--schema', required=True)
    a = p.parse_args(argv)
    catalog = build_catalog(Path(a.root), a.commit)
    schema = json.loads(Path(a.schema).read_text())
    validate_supported(catalog, schema)
    Path(a.catalog).parent.mkdir(parents=True, exist_ok=True)
    Path(a.catalog).write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n")
    Path(a.summary).write_text(json.dumps(build_summary(catalog), indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
