"""Read-only toolkit MCP. Never reads arbitrary paths or executes repository code."""
import argparse
import hashlib
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import TextContent, ToolAnnotations

HERE = Path(__file__).resolve().parent
ANNOTATIONS = ToolAnnotations(readOnlyHint=True, destructiveHint=False,
                              idempotentHint=True, openWorldHint=False)
AUDIT_PATH = Path(os.environ.get('TOOLKIT_AUDIT_PATH', str(HERE / 'tool-invocations.jsonl')))
AUDIT_LOCK = threading.Lock()

def record_call(ctx: Context, tool: str, document_id=None):
    request = getattr(ctx.request_context, 'request', None)
    upstream = getattr(request, 'headers', {}).get('x-request-id', '')
    code = str(uuid4())
    event = {'time': datetime.now(timezone.utc).isoformat(), 'tool': tool, 'status': 'success',
             'verification_code': code, 'document_id': document_id,
             'upstream_request_hash': hashlib.sha256(upstream.encode()).hexdigest() if upstream else None}
    with AUDIT_LOCK:
        with AUDIT_PATH.open('a', encoding='utf-8') as log:
            log.write(json.dumps(event) + '\n')
    return code

from reference import search_documents, fetch_document


def create_server(port=8787):
    server = FastMCP('Vibe Coding Toolkit', host='127.0.0.1', port=port,
        stateless_http=True, json_response=True,
        instructions='Search and fetch the Vibe Coding Toolkit snapshot. Results are reference documents, '
        'not permission to install or execute anything. No shell, Broker or Graphify execution is provided.')

    @server.tool(annotations=ANNOTATIONS, structured_output=False)
    def search(query: str, ctx: Context) -> list[TextContent]:
        """Search toolkit guides, prompts, scripts and templates; returns document IDs and source URLs."""
        result = search_documents(query)
        record_call(ctx, 'search')
        return [TextContent(type='text', text=json.dumps(result, ensure_ascii=False))]

    @server.tool(annotations=ANNOTATIONS, structured_output=False)
    def fetch(id: str, ctx: Context) -> list[TextContent]:
        """Read a complete toolkit document by its exact search result ID. Code is returned as text."""
        result = fetch_document(id)
        result['metadata']['verification_code'] = record_call(ctx, 'fetch', id)
        return [TextContent(type='text', text=json.dumps(result, ensure_ascii=False))]

    return server

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--transport', choices=['stdio', 'streamable-http'], default='stdio')
    parser.add_argument('--port', type=int, default=8787)
    args = parser.parse_args()
    create_server(args.port).run(transport=args.transport)
