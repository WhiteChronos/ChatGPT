"""Start the optional MCP transport with the selected Python, never auto-install."""
from importlib.util import find_spec
from pathlib import Path
import runpy
import sys

if find_spec('mcp') is None:
    print('MCP_SDK_UNAVAILABLE: escolha um Python com mcp==1.30.0. '
          'A consulta offline reference.py continua disponivel.', file=sys.stderr)
    sys.exit(2)

sys.path.insert(0, str(Path(__file__).resolve().parent))
runpy.run_path(str(Path(__file__).with_name('server.py')), run_name='__main__')
