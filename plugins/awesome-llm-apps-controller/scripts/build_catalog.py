#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from awesome_llm_apps_catalog import build_catalog, build_summary

def validate_supported(catalog:dict, schema:dict):
    if catalog.get('schema_version') != schema['properties']['schema_version']['const']:
        raise ValueError('schema_version mismatch')
    if not isinstance(catalog.get('upstream_commit'), str) or not catalog['upstream_commit']:
        raise ValueError('upstream_commit required')
    required=schema['properties']['entries']['items']['required']
    for i,e in enumerate(catalog.get('entries',[])):
        for k in required:
            if k not in e: raise ValueError(f'entry {i} missing {k}')

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--root',required=True); p.add_argument('--commit',required=True)
    p.add_argument('--catalog',required=True); p.add_argument('--summary',required=True); p.add_argument('--schema',required=True)
    a=p.parse_args(argv)
    catalog=build_catalog(Path(a.root),a.commit)
    schema=json.loads(Path(a.schema).read_text())
    validate_supported(catalog,schema)
    Path(a.catalog).parent.mkdir(parents=True,exist_ok=True)
    Path(a.catalog).write_text(json.dumps(catalog,indent=2,sort_keys=True)+"\n")
    Path(a.summary).write_text(json.dumps(build_summary(catalog),indent=2,sort_keys=True)+"\n")
    return 0
if __name__=='__main__': raise SystemExit(main())
