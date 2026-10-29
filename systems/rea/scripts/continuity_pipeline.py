#!/usr/bin/env python3
"""Read-only local REA doctor -> independent local memory; no host discovery claim."""
import argparse
import json
from pathlib import Path
import sys
import rea_memory
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bridge import native_runtime

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',required=True)
    p.add_argument('--datasheet',required=True)
    args=p.parse_args(argv)
    try:
        info=native_runtime()
        native=str(info.get('native_status','UNAVAILABLE'))
        rea_memory.append(args.db,'STATUS','REA read-only native runtime doctor',
                          {'native_status':native,'host_discovered':False,
                           'live_verified':False,'production_complete':False},
                          reference='rea_native_doctor.py')
        sheet=rea_memory.datasheet(args.db,args.datasheet)
        print(json.dumps({'product':rea_memory.PRODUCT,'native_status':native,
                          'host_discovered':False,'live_verified':False,
                          'datasheet':sheet['export_path'],'production_complete':False}))
        return 0
    except (OSError,ValueError,KeyError) as exc:
        print(json.dumps({'status':'BLOCKED','product':rea_memory.PRODUCT,
                          'reason_type':type(exc).__name__,'production_complete':False}))
        return 2

if __name__=='__main__':
    raise SystemExit(main())
