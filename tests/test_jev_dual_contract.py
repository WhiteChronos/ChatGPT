"""Offline end-to-end contract checks for BOTH Jev API routes.

No real credentials or provider calls. A matching shape is not evidence that
both probabilistic models agree in production or that a live call succeeded.
"""
from __future__ import annotations

import copy
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from urllib.request import Request

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "jev-decisions"))
import defapi_jev
from defapi_jev import DecisionError, decide
from typesafe_bridge import IntegrationError, MODEL_ID, choose_llm_handler, evaluate_jev, evaluate_llm_comparison


QUESTIONS = {
    "binary": {"type": "noul", "instructions": "Is this fictional sample benign?"},
    "team": {"type": "choice", "instructions": "Which team should review?", "criteria": {
        "eng": "Engineering", "human": "Human escalation",
    }},
    "priority": {"type": "score", "instructions": "Assess urgency", "criteria": [
        "Normal", "Elevated", "Critical",
    ]},
}


ANSWERS = {
    "binary": {"type": "noul", "noul": 0.55},
    "team": {"type": "choice", "choice": "eng", "confidence": 0.82,
             "probabilities": {"eng": 0.82, "human": 0.18}},
    "priority": {"type": "score", "score": 1.5, "confidence": 0.7,
                 "probabilities": {"0": 0.0, "1": 0.5, "2": 0.5},
                 "legend": {"0": "Normal", "1": "Elevated", "2": "Critical"}},
}


class OfficialFake:
    def __init__(self, response):
        self.response = response
        self.called = []
    def __enter__(self):
        return self
    def __exit__(self, *_):
        pass
    def system_one(self, **kwargs):
        self.called.append(kwargs)
        return SimpleNamespace(model_dump=lambda **_kw: copy.deepcopy(self.response))


def _official():
    return {"model": MODEL_ID, "answers": copy.deepcopy(ANSWERS),
            "usage": {"input_tokens": 8, "output_tokens": 5}}


def _gateway():
    return {"model": defapi_jev.MODEL, "answers": copy.deepcopy(ANSWERS),
            "usage": {"input_tokens": 9, "output_tokens": 5},
            "task_id": "synthetic-task", "consumed": "0.0"}


def test_official_and_defapi_have_independent_contracts_and_auth(monkeypatch):
    monkeypatch.setenv("DEFAPI_API_KEY", "synthetic-defapi-key")
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    official = OfficialFake(_official())
    request_history = []
    def fake_open(request, *, timeout):
        request_history.append({"url": request.full_url,
                                "auth": request.get_header("Authorization"),
                                "body": json.loads(request.data)})
        return io.BytesIO(json.dumps(_gateway()).encode())
    monkeypatch.setattr(defapi_jev, "urlopen", fake_open)

    direct = evaluate_jev({"ticket": "fictional"}, QUESTIONS,
                          client_factory=lambda **_kw: official)
    gateway = decide({"ticket": "fictional"}, QUESTIONS)

    assert direct["model"] == MODEL_ID
    assert gateway["model"] == defapi_jev.MODEL
    assert set(direct["answers"]) == set(gateway["answers"]) == set(QUESTIONS)
    assert {n: a["type"] for n, a in direct["answers"].items()} == {n: a["type"] for n, a in gateway["answers"].items()}
    assert direct["answers"] == gateway["answers"]  # identical synthetic fixtures only
    assert request_history == [{"url": "https://api.defapi.org/api/v1/decisions",
                                "auth": "Bearer synthetic-defapi-key",
                                "body": {"model": defapi_jev.MODEL, "state": {"ticket": "fictional"},
                                         "questions": QUESTIONS}}]
    assert official.called[0]["model"] == MODEL_ID
    assert "task_id" not in direct
    assert gateway["task_id"] == "synthetic-task"


def test_gateway_key_does_not_authenticate_official_by_default(monkeypatch):
    monkeypatch.setenv("DEFAPI_API_KEY", "synthetic-gateway-key")
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    with pytest.raises(IntegrationError, match="TYPESAFE_API_KEY"):
        evaluate_jev("fictional", QUESTIONS)


def test_official_key_does_not_authenticate_gateway_by_default(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "synthetic-vendor-key")
    monkeypatch.delenv("DEFAPI_API_KEY", raising=False)
    monkeypatch.setattr(defapi_jev, "urlopen", lambda *_a, **_kw: pytest.fail("unauthorized network"))
    with pytest.raises(DecisionError, match="DEFAPI_API_KEY"):
        decide("fictional", QUESTIONS)


@pytest.mark.parametrize("faulty", [
    {"eng": 0.3, "human": 0.3},  # missing probability mass
    {"eng": 0.8, "invented": 0.2},  # unexpected class / missing required class
    {"eng": 0.8, "human": 0.4},  # excess probability mass
])
def test_defapi_rejects_invalid_choice_distributions(monkeypatch, faulty):
    monkeypatch.setenv("DEFAPI_API_KEY", "synthetic-only")
    payload = _gateway()
    payload["answers"]["team"]["probabilities"] = faulty
    monkeypatch.setattr(defapi_jev, "urlopen", lambda *_a, **_kw: io.BytesIO(json.dumps(payload).encode()))
    with pytest.raises(DecisionError, match="probability"):
        decide("fictional", QUESTIONS)


def test_defapi_rejects_invalid_ordinal_distribution(monkeypatch):
    monkeypatch.setenv("DEFAPI_API_KEY", "synthetic-only")
    payload = _gateway()
    payload["answers"]["priority"]["probabilities"] = {"0": .6, "1": .4, "9": 0.0}
    monkeypatch.setattr(defapi_jev, "urlopen", lambda *_a, **_kw: io.BytesIO(json.dumps(payload).encode()))
    with pytest.raises(DecisionError, match="probability"):
        decide("fictional", QUESTIONS)


def test_defapi_returns_no_untrusted_echo_or_debug(monkeypatch):
    monkeypatch.setenv("DEFAPI_API_KEY", "synthetic-only")
    payload = _gateway()
    payload["debug"] = {"request": "private fake data"}
    payload["answers"]["team"]["debug"] = "private fake data"
    monkeypatch.setattr(defapi_jev, "urlopen", lambda *_a, **_kw: io.BytesIO(json.dumps(payload).encode()))
    result = decide("fictional", QUESTIONS)
    assert "private fake data" not in json.dumps(result)
    assert result["task_id"] == "synthetic-task"


def test_defapi_redirect_handler_denies_redirects_to_avoid_auth_leakage():
    request = Request("https://api.defapi.org/api/v1/decisions", headers={"Authorization": "Bearer synthetic-key"})
    handler = defapi_jev._NoRedirect()
    assert handler.redirect_request(request, None, 302, "Found", {}, "https://evil.example/steal") is None


def test_jev_router_refuses_forged_distribution_or_model():
    catalog = {"eng": {"provider": "openai", "model": "only-approved-model"}}
    fake = {"model": MODEL_ID, "answers": {"route": {"type": "choice", "choice": "eng",
            "confidence": 0.99, "probabilities": {"eng": 0.99}}}}
    assert choose_llm_handler(fake, catalog)["status"] == "REVIEW_REQUIRED"
    fake["answers"]["route"]["probabilities"] = {"eng": 1.0}
    fake["model"] = "other-model"
    assert choose_llm_handler(fake, catalog)["status"] == "REVIEW_REQUIRED"


def test_llm_comparison_rejects_response_from_wrong_model():
    fake = OfficialFake({**_official(), "model": "different-provider-model"})
    with pytest.raises(IntegrationError, match="model"):
        evaluate_llm_comparison("fictional", QUESTIONS, provider="openai", model="selected-model",
                                client_factory=lambda **_kw: fake)


def test_both_openapi_specs_use_distinct_environments_and_credentials():
    directory = ROOT / "plugins" / "jev-decisions"
    official = json.loads((directory / "chatgpt-action-typesafe.openapi.json").read_text())
    gateway = json.loads((directory / "chatgpt-action.openapi.json").read_text())
    assert official["servers"][0]["url"] == "https://api.typesafe.ai"
    assert gateway["servers"][0]["url"] == "https://api.defapi.org"
    assert {"askTypesafeJev"} == {official["paths"]["/v1/systemone"]["post"]["operationId"]}
    assert {"submitJevDecisions"} == {gateway["paths"]["/api/v1/decisions"]["post"]["operationId"]}
    assert official["components"]["securitySchemes"] != gateway["components"]["securitySchemes"]


def test_typesafe_sdk_nullable_token_counts_do_not_become_fake_zero():
    """The official SDK's Usage allows None when tokens are unreported."""
    payload = _official()
    payload["usage"] = {"input_tokens": None, "output_tokens": None}
    result = evaluate_jev("fictional", QUESTIONS, client_factory=lambda **_kw: OfficialFake(payload))
    assert result["usage"] == {"input_tokens": None, "output_tokens": None}
