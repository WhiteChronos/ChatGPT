"""Offline TDD for official TypeSafe Jev and LLM adapter integration."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "jev-decisions"))

from typesafe_bridge import (
    MODEL_ID,
    IntegrationError,
    choose_llm_handler,
    evaluate_jev,
    evaluate_llm_comparison,
)

QUESTIONS = {
    "route": {
        "type": "choice",
        "instructions": "Which specialist should respond?",
        "criteria": {"openai": "OpenAI", "anthropic": "Anthropic", "human": "human review"},
    },
}


def payload(model=MODEL_ID, choice="openai", confidence=0.92, p=0.91):
    return {"model": model, "answers": {"route": {"type": "choice", "choice": choice,
       "probabilities": {"openai": p, "anthropic": (1-p)*0.5, "human": (1-p)*0.5},
       "confidence": confidence}},
       "usage": {"input_tokens": 4, "output_tokens": 2},
       "request_id": "synthetic"}


class FakeClient:
    def __init__(self, response, **kwargs):
        self.response = response
        self.kwargs = kwargs
        self.calls = []
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.closed = True

    def system_one(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(model_dump=lambda **_kw: self.response)


def test_official_client_pins_model_and_accepts_official_contract(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    client = FakeClient(payload())
    got = evaluate_jev({"ticket": "public fictional example"}, QUESTIONS,
                       client_factory=lambda **kw: client)
    assert client.calls == [{"state": {"ticket": "public fictional example"},
                             "questions": QUESTIONS, "model": MODEL_ID}]
    assert client.closed
    assert got["model"] == MODEL_ID
    assert got["answers"]["route"]["choice"] == "openai"
    assert "task_id" not in got and "consumed" not in got
    assert "request_id" not in got


def test_default_official_requires_secret_before_sdk_import(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    with pytest.raises(IntegrationError, match="TYPESAFE_API_KEY"):
        evaluate_jev("synthetic", QUESTIONS)


@pytest.mark.parametrize("invalid_questions", [
    {},
    {"route": {"type": "choice", "instructions": "choose", "criteria": {"one": "one"}}},
    {"route": {"type": "score", "instructions": "choose", "criteria": ["one"]}},
    {"route": {"type": "noul", "instructions": ""}},
    {"route": {"type": "invented", "instructions": "q"}},
])
def test_invalid_questions_fail_before_factory(invalid_questions):
    with pytest.raises(IntegrationError):
        evaluate_jev("synthetic", invalid_questions,
                     client_factory=lambda **kw: pytest.fail("must not connect"))


def test_invalid_state_nan_fails_before_factory():
    with pytest.raises(IntegrationError):
        evaluate_jev({"not": float("nan")}, QUESTIONS,
                     client_factory=lambda **kw: pytest.fail("must not connect"))


@pytest.mark.parametrize("bad_response", [
    {**payload(), "model": "wrong-alias"},
    {**payload(), "answers": {}},
    {**payload(), "answers": {"route": {"type": "choice", "choice": "fake", "probabilities": {"openai": 1}, "confidence": 1}}},
    {**payload(), "answers": {"route": {"type": "choice", "choice": "openai", "probabilities": {"openai": 1}, "confidence": 1}}},
    {**payload(), "answers": {"route": {"type": "choice", "choice": "openai", "probabilities": {"openai": 0.3, "anthropic": 0.3, "human": 0.3}, "confidence": 1}}},
    {**payload(), "usage": {"input_tokens": "not an integer", "output_tokens": 3}},
])
def test_inconsistent_response_fails_closed(bad_response):
    with pytest.raises(IntegrationError):
        evaluate_jev("synthetic", QUESTIONS,
                     client_factory=lambda **kw: FakeClient(bad_response))


def test_unsafe_sdk_error_does_not_leak_secret_or_state(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "ultrasecret")
    class Bad(FakeClient):
        def system_one(self, **kwargs):
            raise ValueError("ultrasecret -- sensitive state")
    with pytest.raises(IntegrationError) as exc:
        evaluate_jev("sensitive state", QUESTIONS,
                     client_factory=lambda **kw: Bad(payload()))
    assert "ultrasecret" not in str(exc.value)
    assert "sensitive state" not in str(exc.value)


@pytest.mark.parametrize("provider", ["openai", "anthropic", "gemini"])
def test_llm_adapter_uses_explicit_provider_and_model_with_no_debug(provider):
    raw = payload(model="selected-model") | {"debug": {"llm_attempts": [{"secret": "should-not-return"}]}}
    fake = FakeClient(raw)
    got = evaluate_llm_comparison("synthetic", QUESTIONS, provider=provider, model="selected-model",
                                  client_factory=lambda **kw: fake)
    assert fake.calls == [{"state": "synthetic", "questions": QUESTIONS,
                           "provider": provider, "model": "selected-model"}]
    assert got["model"] == "selected-model"
    assert got["provider"] == provider
    assert "debug" not in got
    assert fake.closed


def test_llm_adapter_disallows_non_allowlisted_provider():
    with pytest.raises(IntegrationError, match="unsupported"):
        evaluate_llm_comparison("synthetic", QUESTIONS, provider="unknown", model="x",
                                client_factory=lambda **kw: pytest.fail("connect"))


def test_llm_adapter_requires_provider_credentials_by_default(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(IntegrationError, match="OPENAI_API_KEY"):
        evaluate_llm_comparison("synthetic", QUESTIONS, provider="openai", model="test-model")


def test_router_returns_suggestion_without_executing_any_provider():
    catalog = {"openai": {"provider": "openai", "model": "example-model"},
               "anthropic": {"provider": "anthropic", "model": "example-other"}}
    selected = choose_llm_handler(payload(), catalog, min_confidence=0.80, min_probability=0.75)
    assert selected == {"status": "SUGGESTED_ONLY", "route": "openai", "provider": "openai",
                        "model": "example-model", "confidence": 0.92, "probability": 0.91}


@pytest.mark.parametrize("data", [
    payload(confidence=0.30),
    payload(p=0.55),
    payload(choice="human", p=0.01),
    {"model": MODEL_ID, "answers": {}, "usage": {}},
])
def test_router_fail_closed_to_review_on_low_confidence_or_unsupported(data):
    catalog = {"openai": {"provider": "openai", "model": "example"}}
    selected = choose_llm_handler(data, catalog, min_confidence=0.8, min_probability=0.75)
    assert selected["status"] == "REVIEW_REQUIRED"
    assert "model" not in selected


def test_router_denies_unregistered_provider():
    route = payload()
    catalog = {"openai": {"provider": "external-with-secret-access", "model": "x"}}
    assert choose_llm_handler(route, catalog)["status"] == "REVIEW_REQUIRED"


def test_two_distinct_registry_records_and_chatgpt_openapi():
    repo = ROOT / "registry" / "integrations"
    official = json.loads((repo / "typesafe-jev.json").read_text())
    assert official["source"] == "plugins/jev-decisions"
    assert official["execution_class"] == "CREDENTIALLED"
    assert official["status"] == "ACTIVATION_GATED"
    assert not official["mcp_servers"] and official["runtime_probe"] is None
    schema = json.loads((ROOT / "plugins/jev-decisions/chatgpt-action-typesafe.openapi.json").read_text())
    assert schema["servers"] == [{"url": "https://api.typesafe.ai"}]
    action = schema["paths"]["/v1/systemone"]["post"]
    assert action["operationId"] == "askTypesafeJev"
    assert action["security"] == [{"TypeSafeBearer": []}]
    assert "TYPESAFE_API_KEY=" not in json.dumps(schema)


def test_route_with_jev_builds_choice_from_configured_llms_only():
    from typesafe_bridge import route_with_jev
    catalog = {
        "openai": {"provider": "openai", "model": "test-model", "description": "Open-ended text work"},
        "anthropic": {"provider": "anthropic", "model": "example-model", "description": "Long documents"},
        "human": {"provider": "human", "model": "", "description": "Human review when unsuitable"},
    }
    fake = FakeClient(payload())
    result = route_with_jev("fictional prompt", catalog, client_factory=lambda **kw: fake)
    assert result["status"] == "SUGGESTED_ONLY" and result["provider"] == "openai"
    assert fake.calls[0]["questions"]["route"]["criteria"] == {
        "openai": "Open-ended text work", "anthropic": "Long documents", "human": "Human review when unsuitable"
    }


def test_llm_router_allows_missing_usage_from_llm_adapter():
    raw = payload(model="test-model")
    raw["usage"] = {"input_tokens": None, "output_tokens": None}
    result = evaluate_llm_comparison("example", QUESTIONS, provider="openai", model="test-model",
                                     client_factory=lambda **kw: FakeClient(raw))
    assert result["usage"] == {"input_tokens": None, "output_tokens": None}


def test_llm_comparison_does_not_forward_nested_debug_metadata():
    raw = payload(model="example-model")
    raw["answers"]["route"]["debug"] = {"prompt": "confidential payload"}
    got = evaluate_llm_comparison("synthetic", QUESTIONS, provider="anthropic", model="example-model",
                                  client_factory=lambda **kw: FakeClient(raw))
    assert "debug" not in got["answers"]["route"]
    assert "confidential payload" not in json.dumps(got)
