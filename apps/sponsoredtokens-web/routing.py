"""Bounded Jev decision adapter for SponsoredTokens model routing."""

import http.client
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable

JEV_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
JEV_MODEL = "jev-latest"
JEV_TIMEOUT_SECONDS = 5
MAX_JEV_RESPONSE_BYTES = 65_536
MAX_JEV_MESSAGE_CHARS = 4_000

ROUTED_MODELS = {
    "fast": "sponsored/openai/gpt-6-luna",
    "balanced": "sponsored/openai/gpt-5.6-luna",
    "deep": "sponsored/openai/gpt-5.1-codex-mini",
}
DEFAULT_MODEL = ROUTED_MODELS["deep"]


@dataclass(frozen=True)
class RoutingDecision:
    model: str
    router: str


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _last_user_message(messages: list[dict[str, str]]) -> str:
    for message in reversed(messages):
        if message["role"] == "user":
            return message["content"][:MAX_JEV_MESSAGE_CHARS]
    return ""


def _payload(messages: list[dict[str, str]]) -> dict:
    return {
        "model": JEV_MODEL,
        "state": {"message": _last_user_message(messages)},
        "questions": {
            "route": {
                "type": "choice",
                "instructions": (
                    "Choose the least expensive route that can answer the user's request "
                    "reliably. Escalate ambiguous, risky, multi-step, or coding work."
                ),
                "criteria": {
                    "fast": "Simple chat, extraction, formatting, or a short factual answer.",
                    "balanced": "Ordinary analysis, drafting, or a bounded multi-step task.",
                    "deep": "Complex reasoning, code, debugging, security, or high-risk work.",
                },
            }
        },
    }


def select_model(
    api_key: str | None,
    messages: list[dict[str, str]],
    *,
    opener: Callable | None = None,
) -> RoutingDecision:
    """Return a Jev-selected model, failing open to the proven default."""
    if not api_key or not api_key.strip():
        return RoutingDecision(DEFAULT_MODEL, "fixed")

    if opener is None:
        opener = urllib.request.build_opener(_NoRedirectHandler()).open

    try:
        request = urllib.request.Request(
            JEV_ENDPOINT,
            data=json.dumps(_payload(messages), ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + api_key,
            },
            method="POST",
        )
        with opener(request, timeout=JEV_TIMEOUT_SECONDS) as response:
            body = response.read(MAX_JEV_RESPONSE_BYTES + 1)
        if len(body) > MAX_JEV_RESPONSE_BYTES:
            return RoutingDecision(DEFAULT_MODEL, "fixed")
        payload = json.loads(
            body,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError("Non-standard JSON number")
            ),
        )
        choice = payload.get("answers", {}).get("route", {}).get("choice")
        model = ROUTED_MODELS.get(choice)
        if model is None:
            return RoutingDecision(DEFAULT_MODEL, "fixed")
        return RoutingDecision(model, "jev")
    except urllib.error.HTTPError as error:
        error.close()
    except (
        TimeoutError,
        urllib.error.URLError,
        OSError,
        http.client.HTTPException,
        ValueError,
        TypeError,
        AttributeError,
        RecursionError,
    ):
        pass
    return RoutingDecision(DEFAULT_MODEL, "fixed")
