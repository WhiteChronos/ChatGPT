"""Local Laya decision adapter with a deterministic routing fallback."""

import http.client
import json
import math
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable

MAX_ROUTER_RESPONSE_BYTES = 65_536
MAX_ROUTER_MESSAGE_CHARS = 4_000

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


@dataclass(frozen=True)
class RoutingConfig:
    endpoint: str = "http://127.0.0.1:8770/v1/systemone"
    model: str = "multilingual"
    timeout_seconds: float = 2.0
    min_confidence: float = 0.70

    def __post_init__(self):
        parsed = urllib.parse.urlsplit(self.endpoint)
        if (
            parsed.scheme != "http"
            or parsed.hostname != "127.0.0.1"
            or parsed.port != 8770
            or parsed.path != "/v1/systemone"
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Router endpoint must use the approved loopback service")


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _last_user_message(messages: list[dict[str, str]]) -> str:
    for message in reversed(messages):
        if message["role"] == "user":
            return message["content"][:MAX_ROUTER_MESSAGE_CHARS]
    return ""


def _searchable_message(message: str) -> str:
    normalized = unicodedata.normalize("NFKD", message).encode("ascii", "ignore")
    return normalized.decode("ascii").lower()


def deterministic_route(messages: list[dict[str, str]]) -> RoutingDecision:
    """Choose a conservative local route without network access or credentials."""
    message = _last_user_message(messages)
    searchable = _searchable_message(message)
    deep_indicators = (
        "```",
        "stack trace",
        "traceback",
        "debug",
        "corrija",
        "codigo",
        "seguranca",
        "credencial",
        "api key",
        "token",
        "juridic",
        "legal",
        "medic",
        "financeir",
        "alto risco",
        "alta garantia",
    )
    many_actions = len(re.findall(r"\b(?:e|depois|entao|tambem)\b", searchable)) >= 3
    long_structured = len(message) > 2_000 or message.count("\n") >= 20
    if any(indicator in searchable for indicator in deep_indicators) or many_actions or long_structured:
        return RoutingDecision(ROUTED_MODELS["deep"], "deterministic")

    fast_intents = (
        "traduza",
        "traduzir",
        "formate",
        "formatar",
        "extraia",
        "extrair",
        "resuma em uma linha",
        "resumir em uma linha",
        "resposta breve",
        "responda brevemente",
    )
    if len(message) <= 500 and any(intent in searchable for intent in fast_intents):
        return RoutingDecision(ROUTED_MODELS["fast"], "deterministic")
    return RoutingDecision(ROUTED_MODELS["balanced"], "deterministic")


def _payload(config: RoutingConfig, messages: list[dict[str, str]]) -> dict:
    return {
        "model": config.model,
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


def _finite_probability(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and 0.0 <= value <= 1.0
    )


def _validated_laya_decision(
    payload: object,
    config: RoutingConfig,
    *,
    require_admission: bool = True,
) -> RoutingDecision | None:
    if not isinstance(payload, dict):
        return None
    answers = payload.get("answers")
    route = answers.get("route") if isinstance(answers, dict) else None
    if not isinstance(route, dict):
        return None
    choice = route.get("choice")
    probabilities = route.get("probabilities")
    confidence = route.get("confidence")
    if choice not in ROUTED_MODELS or not isinstance(probabilities, dict):
        return None
    if set(probabilities) != set(ROUTED_MODELS):
        return None
    if not all(_finite_probability(probabilities[name]) for name in ROUTED_MODELS):
        return None
    if not math.isclose(sum(probabilities.values()), 1.0, abs_tol=0.02):
        return None
    if not _finite_probability(confidence):
        return None
    if require_admission and choice != "deep" and confidence < config.min_confidence:
        return None
    return RoutingDecision(ROUTED_MODELS[choice], "laya")


def _query_laya(
    config: RoutingConfig,
    messages: list[dict[str, str]],
    opener: Callable | None,
    *,
    require_admission: bool = True,
) -> RoutingDecision | None:
    if opener is None:
        opener = urllib.request.build_opener(_NoRedirectHandler()).open
    try:
        request = urllib.request.Request(
            config.endpoint,
            data=json.dumps(_payload(config, messages), ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with opener(request, timeout=config.timeout_seconds) as response:
            body = response.read(MAX_ROUTER_RESPONSE_BYTES + 1)
        if len(body) > MAX_ROUTER_RESPONSE_BYTES:
            return None
        payload = json.loads(
            body,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError("Non-standard JSON number")
            ),
        )
        return _validated_laya_decision(
            payload, config, require_admission=require_admission
        )
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
    return None


def select_model(
    config: RoutingConfig,
    messages: list[dict[str, str]],
    *,
    opener: Callable | None = None,
) -> RoutingDecision:
    """Return a valid local Laya decision or the deterministic fallback."""
    return _query_laya(config, messages, opener) or deterministic_route(messages)


def probe_router(
    config: RoutingConfig,
    *,
    opener: Callable | None = None,
) -> bool:
    """Confirm that the loopback listener implements the expected Laya contract."""
    safe_probe = [{"role": "user", "content": "Classifique uma solicitação local."}]
    return _query_laya(
        config, safe_probe, opener, require_admission=False
    ) is not None
