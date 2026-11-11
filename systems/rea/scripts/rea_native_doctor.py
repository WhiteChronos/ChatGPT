#!/usr/bin/env python3
"""Report external REA runtime prerequisites, not host discovery."""
import sys, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from bridge import native_runtime
if __name__=='__main__':
    status=native_runtime()
    status['internal_mcp_files_present']=all((Path(__file__).resolve().parents[1]/'src'/n).is_file() for n in ('server.py','internal_engine.py'))
    status['host_discovered']=False
    status['live_verified']=False
    print(json.dumps(status,indent=2))
