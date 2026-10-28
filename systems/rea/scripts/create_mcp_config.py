#!/usr/bin/env python3
"""Print opt-in Codex registrations for independent REA processes; never mutate host."""
from pathlib import Path
import sys, argparse, json

def generate_config(app_root: Path, data_root: Path, python: str) -> str:
    app=Path(app_root).resolve(strict=True)
    root=Path(data_root).resolve(strict=True)
    script=app/'src/server.py'
    if not script.is_file() or not root.is_dir(): raise ValueError('Invalid REA paths')
    py=Path(python).resolve(strict=True)
    q=lambda x:json.dumps(x,ensure_ascii=True)
    return ('# Review with your Codex config. These entries do not install anything.\n'
            '# The upstream REA official MCP registration must be produced by npx rea-agents setup.\n'
            '\n[mcp_servers.rea_internal]\ncommand = '+q(str(py))+'\n'
            'args = '+q([str(script),'--transport','stdio','--root',str(root)])+'\nstartup_timeout_sec = 30\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--data-root',type=Path,required=True)
    a=parser.parse_args()
    print(generate_config(Path(__file__).resolve().parents[1],a.data_root,sys.executable))
