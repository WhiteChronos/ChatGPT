"""Opt-in TypeSafe Jev API + official LLM System One adapter bridge.

No SDK installation, provider calls, credential provisioning, logging, or tool
execution happens on import. Every network-capable function is an explicit call.
Neither model inference nor the proposed LLM route grants workflow authority.
"""
from __future__ import annotations

import json
import math
import os
from collections.abc import Callable, Mapping
from typing import Any

MODEL_ID = "jev-1.13.0"
OFFICIAL_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
LLM_PROVIDERS = frozenset({"openai", "anthropic", "gemini"})
_SECRET_ENV = {"openai": ("OPENAI_API_KEY",), "anthropic": ("ANTHROPIC_API_KEY",),
               "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY")}


class IntegrationError(ValueError):
    """Fixed, credential-safe validation or dependency error."""


def _between(value: object, low: float = 0, high: float = 1) -> bool:
    return type(value) in (float, int) and math.isfinite(value) and low <= value <= high


def _validate_input(state: object, questions: object) -> dict[str, dict]:
    if not isinstance(state, (str, dict, list)):
        raise IntegrationError("state must be JSON text, object or array")
    if not isinstance(questions, dict) or not questions:
        raise IntegrationError("questions must be a nonempty mapping")
    try:
        json.dumps({"state": state, "questions": questions}, allow_nan=False)
    except (ValueError, TypeError, RecursionError) as exc:
        raise IntegrationError("input must contain finite, JSON-compatible data") from None
    for name, q in questions.items():
        if not isinstance(name, str) or not name.strip() or not isinstance(q, dict):
            raise IntegrationError("invalid question")
        if set(q) - {"type", "instructions", "criteria"}:
            raise IntegrationError("unsupported question field")
        kind = q.get("type")
        instructions = q.get("instructions")
        if kind not in {"choice", "score", "noul"}:
            raise IntegrationError("unsupported question type")
        if not isinstance(instructions, (str, dict, list)) or not instructions:
            raise IntegrationError("question instructions required")
        if isinstance(instructions, str) and not instructions.strip():
            raise IntegrationError("question instructions required")
        criteria = q.get("criteria")
        if kind == "choice":
            if not isinstance(criteria, dict) or not 2 <= len(criteria) <= 255:
                raise IntegrationError("choice needs 2-255 named alternatives")
            if any(not isinstance(k, str) or not k.strip() or
                   not isinstance(v, (str, dict, list, type(None))) for k, v in criteria.items()):
                raise IntegrationError("invalid choice criteria")
        if kind == "score":
            if not isinstance(criteria, list) or not 2 <= len(criteria) <= 10 or not all(
                isinstance(v, (str, dict, list)) and bool(v) for v in criteria
            ):
                raise IntegrationError("score needs 2-10 ordered levels")
        if kind == "noul" and criteria is not None:
            if not isinstance(criteria, dict) or not criteria or set(criteria) - {"true", "false"}:
                raise IntegrationError("invalid noul criteria")
    return questions


def _check_secret(*names: str) -> None:
    if not any(os.environ.get(name, "").strip() for name in names):
        raise IntegrationError("API credential required: " + " or ".join(names))


def _read_result(result: object, questions: Mapping[str, dict], *, model: str | None,
                 allow_unknown_usage: bool = False) -> dict[str, Any]:
    try:
        data = result if isinstance(result, dict) else result.model_dump(mode="json", exclude_none=True)
        if not isinstance(data, dict):
            raise IntegrationError("invalid provider response")
        returned_model = data.get("model")
        if not isinstance(returned_model, str) or not returned_model or (model and model != returned_model):
            raise IntegrationError("unexpected response model")
        answers = data.get("answers")
        usage = data.get("usage")
        if not isinstance(answers, dict) or set(answers) != set(questions):
            raise IntegrationError("answer IDs do not match the submitted questions")
        if not isinstance(usage, dict) or any(
            not (allow_unknown_usage and usage.get(k) is None)
            and (type(usage.get(k)) is not int or usage[k] < 0)
            for k in ("input_tokens", "output_tokens")
        ):
            raise IntegrationError("invalid provider usage")
        for key, q in questions.items():
            answer = answers[key]
            if not isinstance(answer, dict) or answer.get("type") != q["type"]:
                raise IntegrationError("answer type mismatch")
            if q["type"] == "noul":
                if not _between(answer.get("noul")):
                    raise IntegrationError("invalid noul probability")
                continue
            if not _between(answer.get("confidence")):
                raise IntegrationError("invalid confidence")
            probabilities = answer.get("probabilities")
            expected = (set(q["criteria"]) if q["type"] == "choice" else
                        {str(i) for i in range(len(q["criteria"]))})
            if not isinstance(probabilities, dict) or set(probabilities) != expected or not all(
                _between(v) for v in probabilities.values()
            ) or abs(sum(probabilities.values()) - 1) > 0.01:
                raise IntegrationError("invalid probability distribution")
            if q["type"] == "choice" and answer.get("choice") not in expected:
                raise IntegrationError("unlisted decision alternative")
            if q["type"] == "score":
                if not _between(answer.get("score"), 0, len(q["criteria"]) - 1):
                    raise IntegrationError("invalid ordinal score")
        allowed_fields = {"type", "noul", "choice", "score", "confidence",
                          "probabilities", "legend"}
        safe_answers = {name: {key: value for key, value in answer.items()
                               if key in allowed_fields} for name, answer in answers.items()}
        return {"model": returned_model, "answers": safe_answers,
                "usage": {"input_tokens": usage["input_tokens"],
                          "output_tokens": usage["output_tokens"]}}
    except IntegrationError:
        raise
    except (AttributeError, TypeError, ValueError, KeyError, OverflowError) as exc:
        raise IntegrationError("invalid provider response") from None


def evaluate_jev(state: str | dict | list, questions: dict, *,
                 client_factory: Callable[..., Any] | None = None) -> dict[str, Any]:
    """One explicitly invoked call to official Jev via TypeSafe's optional SDK.

    The real SDK uses TYPESAFE_API_KEY and the pinned version jev-1.13.0.
    Test callers may inject a harmless fake client; this never installs an SDK.
    """
    valid = _validate_input(state, questions)
    if client_factory is None:
        _check_secret("TYPESAFE_API_KEY")
        try:
            from typesafe_sdk import TypeSafeClient
        except ImportError:
            raise IntegrationError("Install the official typesafe-sdk in your approved environment") from None
        client_factory = TypeSafeClient
    try:
        with client_factory(model=MODEL_ID) as client:
            result = client.system_one(state=state, questions=valid, model=MODEL_ID)
        return _read_result(result, valid, model=MODEL_ID)
    except IntegrationError:
        raise
    except Exception:
        raise IntegrationError("TypeSafe request failed; check runtime configuration") from None


def evaluate_llm_comparison(state: str | dict | list, questions: dict, *,
                            provider: str, model: str,
                            client_factory: Callable[..., Any] | None = None) -> dict[str, Any]:
    """Optional official System-One LLM *comparison*, not a Jev model invocation.

    Supported adapter providers (per official TypeSafe README): OpenAI,
    Anthropic and Gemini. This only runs when called with a model and credentials.
    """
    if provider not in LLM_PROVIDERS:
        raise IntegrationError("unsupported LLM provider")
    if not isinstance(model, str) or not model.strip() or any(x in model for x in "\r\n"):
        raise IntegrationError("nonempty LLM model ID required")
    valid = _validate_input(state, questions)
    if client_factory is None:
        _check_secret(*_SECRET_ENV[provider])
        try:
            from system_one_adapter import SystemOneAdapterClient
        except ImportError:
            raise IntegrationError("Install the official system-one-adapter with the relevant provider extra") from None
        client_factory = SystemOneAdapterClient
    try:
        with client_factory() as client:
            result = client.system_one(state=state, questions=valid, provider=provider, model=model)
        view = _read_result(result, valid, model=None, allow_unknown_usage=True)
        return {**view, "provider": provider, "engine": "llm_comparison"}
    except IntegrationError:
        raise
    except Exception:
        raise IntegrationError("LLM comparison failed; check provider configuration") from None


def choose_llm_handler(decision: Mapping[str, Any], catalog: Mapping[str, Mapping[str, str]], *,
                       min_confidence: float = 0.80, min_probability: float = 0.75,
                       question: str = "route") -> dict[str, object]:
    """Pure allowlisted routing suggestion. Does not invoke an LLM or take an action.

    Thresholds are sample defaults, NOT calibrated production safety criteria.
    Caller must enforce permissions, data sharing consent and human review.
    """
    if not _between(min_confidence) or not _between(min_probability):
        raise IntegrationError("routing thresholds must be between zero and one")
    review = {"status": "REVIEW_REQUIRED", "reason": "unverified or uncertain route"}
    try:
        if not isinstance(decision, Mapping) or not isinstance(catalog, Mapping):
            return review
        a = decision["answers"][question]
        if not isinstance(a, Mapping) or a.get("type") != "choice":
            return review
        choice = a.get("choice")
        probs = a.get("probabilities")
        confidence = a.get("confidence")
        if not isinstance(choice, str) or not isinstance(probs, Mapping) or not _between(confidence):
            return review
        if not _between(probs.get(choice)) or confidence < min_confidence or probs[choice] < min_probability:
            return review
        record = catalog.get(choice)
        if not isinstance(record, Mapping):
            return review
        provider, model = record.get("provider"), record.get("model")
        if provider not in LLM_PROVIDERS or not isinstance(model, str) or not model.strip():
            return review
        return {"status": "SUGGESTED_ONLY", "route": choice, "provider": provider,
                "model": model, "confidence": confidence, "probability": probs[choice]}
    except (KeyError, TypeError, ValueError, AttributeError):
        return review


def route_with_jev(state: str | dict | list, catalog: Mapping[str, Mapping[str, str]], *,
                   instructions: str = "Which registered specialist best matches this request?",
                   min_confidence: float = 0.80, min_probability: float = 0.75,
                   client_factory: Callable[..., Any] | None = None) -> dict[str, object]:
    """Ask official Jev to *suggest* one configured LLM, never invoke it.

    The application must supply its own allowed models and descriptions, and
    should include a human/no-match route for out-of-scope requests.
    """
    if not isinstance(catalog, Mapping) or not 2 <= len(catalog) <= 255:
        raise IntegrationError("catalog needs 2-255 explicit handlers")
    if not isinstance(instructions, str) or not instructions.strip():
        raise IntegrationError("routing instructions are required")
    criteria = {}
    for name, entry in catalog.items():
        if not isinstance(name, str) or not name.strip() or not isinstance(entry, Mapping):
            raise IntegrationError("invalid routing catalog")
        description = entry.get("description")
        if not isinstance(description, str) or not description.strip():
            raise IntegrationError("each route needs a nonempty description")
        criteria[name] = description
    questions = {"route": {"type": "choice", "instructions": instructions, "criteria": criteria}}
    result = evaluate_jev(state, questions, client_factory=client_factory)
    return choose_llm_handler(result, catalog, min_confidence=min_confidence,
                              min_probability=min_probability)
