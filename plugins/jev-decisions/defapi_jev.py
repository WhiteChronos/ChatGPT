"""Opt-in DefAPI Jev-1.13 decision client; no runtime auto-activation.

Authentication is read from DEFAPI_API_KEY at call time. Request and response
content is never logged here. Do not send confidential engineering data unless
its third-party transmission has been separately approved.
"""
from __future__ import annotations

import json
import math
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAPI_URL = "https://api.defapi.org/api/v1/decisions"
MODEL = "typesafe/jev-1.13"
_MAX_RESPONSE_BYTES = 262144


class DecisionError(ValueError):
    """Safe client error that never includes the API key or submitted state."""


def _valid_number(value: object, low: float = 0, high: float = 1) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and low <= value <= high


def _questions(questions: object) -> dict[str, dict[str, object]]:
    if not isinstance(questions, dict) or not questions:
        raise DecisionError("questions must be a nonempty mapping")
    cleaned: dict[str, dict[str, object]] = {}
    for name, question in questions.items():
        if not isinstance(name, str) or not name.strip() or not isinstance(question, dict):
            raise DecisionError("invalid question name or definition")
        kind = question.get("type")
        instruction = question.get("instructions")
        if kind not in ("noul", "choice", "score") or not isinstance(instruction, str) or not instruction.strip():
            raise DecisionError("question needs a valid type and instructions")
        if set(question) - {"type", "instructions", "criteria"}:
            raise DecisionError("unsupported question field")
        entry: dict[str, object] = {"type": kind, "instructions": instruction}
        criteria = question.get("criteria")
        if kind == "noul":
            if criteria is not None:
                if not isinstance(criteria, dict) or not criteria or set(criteria) - {"true", "false"}:
                    raise DecisionError("noul criteria must describe true/false")
                if not all(isinstance(v, str) and v.strip() for v in criteria.values()):
                    raise DecisionError("invalid noul criteria descriptions")
                entry["criteria"] = criteria
        elif kind == "choice":
            if not isinstance(criteria, dict) or not 2 <= len(criteria) <= 255:
                raise DecisionError("choice needs 2-255 alternatives")
            if not all(isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip() for k, v in criteria.items()):
                raise DecisionError("invalid choice criteria")
            entry["criteria"] = criteria
        else:
            if not isinstance(criteria, list) or not 2 <= len(criteria) <= 10:
                raise DecisionError("score needs 2-10 ordered levels")
            if not all(isinstance(v, str) and v.strip() for v in criteria):
                raise DecisionError("invalid score criteria")
            entry["criteria"] = criteria
        cleaned[name] = entry
    return cleaned


def _decode_response(raw: bytes, questions: dict[str, dict[str, object]]) -> dict[str, object]:
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise DecisionError("invalid JSON response") from exc
    if not isinstance(data, dict) or data.get("model") != MODEL:
        raise DecisionError("unexpected model or response format")
    answers = data.get("answers")
    usage = data.get("usage")
    if not isinstance(answers, dict) or set(answers) != set(questions):
        raise DecisionError("missing or unexpected answers")
    if not isinstance(usage, dict) or any(type(usage.get(n)) is not int or usage[n] < 0 for n in ("input_tokens", "output_tokens")):
        raise DecisionError("invalid usage fields")
    if not isinstance(data.get("task_id"), str) or not data["task_id"] or not isinstance(data.get("consumed"), str):
        raise DecisionError("invalid task or cost fields")
    for name, question in questions.items():
        answer = answers[name]
        kind = question["type"]
        if not isinstance(answer, dict) or answer.get("type") != kind:
            raise DecisionError("answer type mismatch")
        if kind == "noul" and not _valid_number(answer.get("noul")):
            raise DecisionError("invalid noul probability")
        if kind == "choice" and answer.get("choice") not in question["criteria"]:
            raise DecisionError("invalid choice result")
        if kind == "score" and not _valid_number(answer.get("score"), 0, len(question["criteria"]) - 1):
            raise DecisionError("invalid score result")
        if "confidence" in answer and not _valid_number(answer["confidence"]):
            raise DecisionError("invalid confidence value")
        if "probabilities" in answer:
            probs = answer["probabilities"]
            if not isinstance(probs, dict) or not all(isinstance(k, str) and _valid_number(v) for k, v in probs.items()):
                raise DecisionError("invalid probability distribution")
    return data


def decide(state: str | dict | list, questions: dict, *, timeout: float = 15) -> dict[str, object]:
    """Submit typed questions to DefAPI on explicit call only.

    Raises DecisionError for missing credentials, invalid payload, transport
    failures, HTTP errors, or untrusted responses. It never falls back to a
    guessed answer and never triggers GitHub/CI/production actions.
    """
    if not isinstance(state, (str, dict, list)):
        raise DecisionError("state must be text, an object, or an array")
    normalized = _questions(questions)
    if not _valid_number(timeout, 0.000001, 120):
        raise DecisionError("timeout must be between 0 and 120 seconds")
    try:
        body = json.dumps({"model": MODEL, "state": state, "questions": normalized}, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise DecisionError("state must contain valid JSON data") from exc
    key = os.environ.get("DEFAPI_API_KEY", "").strip()
    if not key or "\r" in key or "\n" in key:
        raise DecisionError("DEFAPI_API_KEY is missing or invalid")
    request = Request(
        DEFAPI_URL,
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read(_MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        raise DecisionError(f"DefAPI request failed (HTTP {exc.code})") from None
    except (URLError, TimeoutError, OSError) as exc:
        raise DecisionError("DefAPI request failed (transport)") from None
    if len(raw) > _MAX_RESPONSE_BYTES:
        raise DecisionError("DefAPI response exceeded size limit")
    return _decode_response(raw, normalized)
