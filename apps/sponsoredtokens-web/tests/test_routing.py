import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import routing


class FakeResponse:
    def __init__(self, payload):
        self.body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.read_sizes = []
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def read(self, size):
        self.read_sizes.append(size)
        return self.body[:size]


def laya_payload(choice="balanced", confidence=0.91, probabilities=None):
    if probabilities is None:
        remainder = (1.0 - confidence) / 2
        probabilities = {"fast": remainder, "balanced": remainder, "deep": remainder}
        probabilities[choice] = confidence
    return {
        "answers": {
            "route": {
                "choice": choice,
                "probabilities": probabilities,
                "confidence": confidence,
            }
        },
        "model": "multilingual",
    }


class DeterministicRoutingTests(unittest.TestCase):
    def test_deterministic_routes_high_risk_and_code_to_deep(self):
        cases = (
            "Corrija este código:\n```python\nprint(secret)\n```",
            "Avalie a segurança desta API e das credenciais",
            "Preciso de orientação médica de alto risco",
        )
        for message in cases:
            with self.subTest(message=message):
                self.assertEqual(
                    routing.deterministic_route([{"role": "user", "content": message}]),
                    routing.RoutingDecision(
                        "sponsored/openai/gpt-5.1-codex-mini", "deterministic"
                    ),
                )

    def test_deterministic_routes_explicit_short_transform_to_fast(self):
        cases = (
            "Traduza para inglês: bom dia",
            "Formate esta data: 13/10/2026",
            "Resuma em uma linha: texto curto",
        )
        for message in cases:
            with self.subTest(message=message):
                self.assertEqual(
                    routing.deterministic_route([{"role": "user", "content": message}]),
                    routing.RoutingDecision(
                        "sponsored/openai/gpt-6-luna", "deterministic"
                    ),
                )

    def test_deterministic_routes_ordinary_request_to_balanced(self):
        self.assertEqual(
            routing.deterministic_route(
                [{"role": "user", "content": "Escreva um convite cordial para a equipe"}]
            ),
            routing.RoutingDecision(
                "sponsored/openai/gpt-5.6-luna", "deterministic"
            ),
        )

    def test_deterministic_prefers_deep_over_fast_indicator(self):
        self.assertEqual(
            routing.deterministic_route(
                [
                    {
                        "role": "user",
                        "content": "Traduza este stack trace e explique como corrigir o erro",
                    }
                ]
            ),
            routing.RoutingDecision(
                "sponsored/openai/gpt-5.1-codex-mini", "deterministic"
            ),
        )


class LayaRoutingTests(unittest.TestCase):
    def setUp(self):
        self.config = routing.RoutingConfig()
        self.messages = [{"role": "user", "content": "Escreva um convite cordial"}]

    def test_config_rejects_non_loopback_endpoint_without_echoing_it(self):
        for endpoint in (
            "https://api.typesafe.ai/v1/systemone",
            "http://localhost:8770/v1/systemone",
            "http://127.0.0.1:8770/other",
        ):
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError) as caught:
                    routing.RoutingConfig(endpoint=endpoint)
                self.assertNotIn(endpoint, str(caught.exception) + repr(caught.exception))

    def test_request_uses_loopback_multilingual_without_credentials_and_bounds_message(self):
        seen = []
        response = FakeResponse(laya_payload())

        def opener(request, *, timeout):
            seen.append((request, timeout))
            return response

        messages = [
            {"role": "user", "content": "primeira mensagem privada"},
            {"role": "assistant", "content": "resposta anterior"},
            {"role": "user", "content": "x" * 4_001},
        ]
        decision = routing.select_model(self.config, messages, opener=opener)

        self.assertEqual(
            decision,
            routing.RoutingDecision("sponsored/openai/gpt-5.6-luna", "laya"),
        )
        self.assertEqual(len(seen), 1)
        request, timeout = seen[0]
        self.assertEqual(request.full_url, "http://127.0.0.1:8770/v1/systemone")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertIsNone(request.get_header("Authorization"))
        self.assertEqual(timeout, 2.0)
        payload = json.loads(request.data)
        self.assertEqual(payload["model"], "multilingual")
        self.assertEqual(payload["state"], {"message": "x" * 4_000})
        self.assertNotIn("primeira mensagem privada", request.data.decode())
        self.assertEqual(response.read_sizes, [65_537])
        self.assertTrue(response.closed)

    def test_valid_choices_map_to_exact_sponsoredtokens_models(self):
        cases = {
            "fast": "sponsored/openai/gpt-6-luna",
            "balanced": "sponsored/openai/gpt-5.6-luna",
            "deep": "sponsored/openai/gpt-5.1-codex-mini",
        }
        for choice, model in cases.items():
            with self.subTest(choice=choice):
                probabilities = {"fast": 0.025, "balanced": 0.025, "deep": 0.025}
                probabilities[choice] = 0.95
                decision = routing.select_model(
                    self.config,
                    self.messages,
                    opener=lambda *args, **kwargs: FakeResponse(
                        laya_payload(choice, 0.95, probabilities)
                    ),
                )
                self.assertEqual(decision, routing.RoutingDecision(model, "laya"))

    def test_low_confidence_non_deep_choice_delegates_deterministically(self):
        decision = routing.select_model(
            self.config,
            self.messages,
            opener=lambda *args, **kwargs: FakeResponse(
                laya_payload(
                    "fast",
                    0.69,
                    {"fast": 0.69, "balanced": 0.20, "deep": 0.11},
                )
            ),
        )
        self.assertEqual(
            decision,
            routing.RoutingDecision("sponsored/openai/gpt-5.6-luna", "deterministic"),
        )

    def test_failures_and_invalid_responses_delegate_deterministically(self):
        failures = {
            "timeout": TimeoutError("sentinel-private-message"),
            "refused": urllib.error.URLError("sentinel-private-message"),
            "redirect": urllib.error.HTTPError(
                self.config.endpoint,
                302,
                "sentinel-private-message",
                {"Location": "https://untrusted.example/sentinel-private-message"},
                io.BytesIO(b"sentinel-private-message"),
            ),
        }
        for name, failure in failures.items():
            with self.subTest(name=name):
                def opener(*args, **kwargs):
                    raise failure

                decision = routing.select_model(self.config, self.messages, opener=opener)
                visible = repr(decision) + str(decision)
                self.assertEqual(
                    decision,
                    routing.RoutingDecision(
                        "sponsored/openai/gpt-5.6-luna", "deterministic"
                    ),
                )
                self.assertNotIn("sentinel-private-message", visible)
        self.assertTrue(failures["redirect"].file.closed)

        invalid_bodies = {
            "oversized": b"{" + b"x" * 65_536,
            "malformed": b"not-json sentinel-private-message",
            "non-finite": b'{"answers":{"route":{"choice":"balanced","probabilities":{"fast":0.0,"balanced":NaN,"deep":0.0},"confidence":NaN}}}',
            "unknown": laya_payload("turbo", 0.9, {"fast": 0.03, "balanced": 0.07, "deep": 0.90}),
            "missing-probabilities": {"answers": {"route": {"choice": "balanced", "confidence": 0.9}}},
            "missing-confidence": {"answers": {"route": {"choice": "balanced", "probabilities": {"fast": 0.1, "balanced": 0.8, "deep": 0.1}}}},
        }
        for name, body in invalid_bodies.items():
            with self.subTest(name=name):
                decision = routing.select_model(
                    self.config,
                    self.messages,
                    opener=lambda *args, _body=body, **kwargs: FakeResponse(_body),
                )
                self.assertEqual(
                    decision,
                    routing.RoutingDecision(
                        "sponsored/openai/gpt-5.6-luna", "deterministic"
                    ),
                )

    def test_probe_requires_a_structurally_valid_laya_response(self):
        self.assertTrue(
            routing.probe_router(
                self.config,
                opener=lambda *args, **kwargs: FakeResponse(laya_payload("deep", 0.4)),
            )
        )
        self.assertTrue(
            routing.probe_router(
                self.config,
                opener=lambda *args, **kwargs: FakeResponse(
                    laya_payload("balanced", 0.5)
                ),
            )
        )
        incompatible = lambda *args, **kwargs: FakeResponse({"status": "listening"})
        self.assertFalse(routing.probe_router(self.config, opener=incompatible))


if __name__ == "__main__":
    unittest.main()
