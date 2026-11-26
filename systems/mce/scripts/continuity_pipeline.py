#!/usr/bin/env python3
"""Read-only MCE engineering readiness -> independent local memory."""
import argparse
import json
from pathlib import Path
import mce_memory
import production_readiness

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',required=True)
    p.add_argument('--workspace',required=True,type=Path)
    p.add_argument('--datasheet',required=True)
    args=p.parse_args(argv)
    try:
        report=production_readiness.assess(args.workspace)
        checks={key:item.get('status','UNKNOWN') for key,item in report['checks'].items()}
        mce_memory.append(args.db,'STATUS','Read-only MCE production-readiness',
                          {'readiness':report['status'],'checks':checks,'production_complete':False},
                          reference='production_readiness.py')
        sheet=mce_memory.datasheet(args.db,args.datasheet)
        print(json.dumps({'product':mce_memory.PRODUCT,'readiness':report['status'],
                          'datasheet':sheet['export_path'],'production_complete':False}))
        return 0 if report['status']=='TECHNICAL_READY_FOR_ENGINEERING_ACCEPTANCE' else 2
    except (OSError,ValueError,KeyError) as exc:
        print(json.dumps({'status':'BLOCKED','product':mce_memory.PRODUCT,
                          'reason_type':type(exc).__name__,'production_complete':False}))
        return 2

if __name__=='__main__':
    raise SystemExit(main())
