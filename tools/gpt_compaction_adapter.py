"""Opt-in OpenAI Responses compaction transport; offline testable, no implicit network."""
import json
import os
import urllib.request

ENDPOINT = "https://api.openai.com/v1/responses/compact"


def build_payload(model, items):
    if not isinstance(model, str) or not model.strip():
        raise ValueError("model is required")
    if not isinstance(items, list) or not items:
        raise ValueError("nonempty input items required")
    return {"model": model, "input": items}


def compact(model, items, *, api_key=None, transport=None):
    """Use the documented /responses/compact route; fail closed on invalid output.

    Caller must explicitly provide api_key or OPENAI_API_KEY. No implicit invocation in CI.
    Transport signature: (url, payload, api_key) -> parsed JSON-compatible dict.
    """
    payload = build_payload(model, items)
    key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY missing; no request sent")
    send = transport or _http_transport
    reply = send(ENDPOINT, payload, key)
    if not isinstance(reply, dict) or not isinstance(reply.get("output"), list):
        raise ValueError("invalid compaction response; retain unmodified input")
    if not any(isinstance(item, dict) and item.get("type") == "compaction" for item in reply["output"]):
        raise ValueError("no compaction item; retain unmodified input")
    return reply["output"]


def _http_transport(url, payload, key):
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)
