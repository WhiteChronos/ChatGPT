import copy
import http.client
import io
import json
import sys
import traceback
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server import (
    MAX_CONTENT_CHARS,
    RequestValidationError,
    validate_bind_host,
    validate_messages,
)

import providers


class FakeResponse:
    def __init__(self, body):
        self.body = body
        self.read_sizes = []
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def read(self, size):
        self.read_sizes.append(size)
        return self.body[:size]


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.messages = validate_messages([
            {"role": "user", "content": "Olá 🌍"},
            {"role": "assistant", "content": "こんにちは"},
        ])
        self.config = providers.SponsoredTokensConfig("sentinel-sponsored-secret")

    def assert_safe_error(self, error, code, status):
        self.assertEqual(error.code, code)
        self.assertEqual(error.http_status, status)
        visible = str(error) + repr(error) + "".join(traceback.format_exception(error))
        for sensitive in (
            "sentinel-sponsored-secret",
            "private-upstream-body", "private-header", "raw-upstream-exception",
        ):
            self.assertNotIn(sensitive, visible)
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)

    def test_payload_preserves_validated_messages_without_aliasing(self):
        original = copy.deepcopy(self.messages)
        payload = providers.build_upstream_payload(self.messages, providers.SPONSOREDTOKENS_MODEL)
        self.assertEqual(payload, {
            "model": "sponsored/openai/gpt-5.1-codex-mini",
            "input": [
                {"role": "user", "content": "Olá 🌍"},
                {"role": "assistant", "content": "こんにちは"},
            ],
        })
        payload["input"][0]["content"] = "changed"
        self.assertEqual(self.messages, original)

    def test_adapter_sends_fixed_endpoint_model_bearer_and_bounded_request(self):
        seen = []
        response = FakeResponse(json.dumps({"output_text": "Resposta 🌍"}).encode())

        def opener(request, *, timeout):
            seen.append((request, timeout))
            return response

        result = providers.call_sponsoredtokens(self.config, self.messages, opener=opener)
        self.assertEqual(result, providers.ProviderResult(
            "Resposta 🌍", "SponsoredTokens", "sponsored/openai/gpt-5.1-codex-mini",
        ))
        self.assertEqual(len(seen), 1)
        request, timeout = seen[0]
        self.assertEqual(request.full_url, "https://sponsoredtokens.com/api/v1/responses")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(request.get_header("Authorization"), "Bearer sentinel-sponsored-secret")
        self.assertEqual(timeout, 30)
        self.assertEqual(json.loads(request.data), {
            "model": "sponsored/openai/gpt-5.1-codex-mini", "input": self.messages,
        })
        self.assertEqual(response.read_sizes, [1_048_577])
        self.assertTrue(response.closed)

    def test_configuration_repr_omits_credential(self):
        self.assertNotIn("sentinel-sponsored-secret", repr(self.config))

    def test_default_transport_refuses_credential_forwarding_on_redirect(self):
        response = FakeResponse(b'{"output_text":"ok"}')

        class FakeOpener:
            def open(self, request, *, timeout):
                self.request = request
                return response

        transport = FakeOpener()
        with patch("urllib.request.build_opener", return_value=transport) as builder:
            result = providers.call_sponsoredtokens(self.config, self.messages)
        self.assertEqual(result.text, "ok")
        handlers = builder.call_args.args
        self.assertEqual(len(handlers), 1)
        for status in (301, 302, 303, 307, 308):
            with self.subTest(status=status):
                self.assertIsNone(handlers[0].redirect_request(
                    transport.request, None, status, "redirect", {},
                    "https://untrusted.example/collect",
                ))

    def test_missing_or_blank_key_never_opens_a_connection(self):
        def opener(*args, **kwargs):
            self.fail("Network attempted without a key")

        for key in (None, "", " \t\n"):
            with self.subTest(key=key):
                missing = providers.SponsoredTokensConfig(key)
                with self.assertRaises(providers.ProviderError) as caught:
                    providers.call_sponsoredtokens(missing, self.messages, opener=opener)
                self.assert_safe_error(caught.exception, "configuration_required", 503)

    def test_http_failures_map_to_safe_codes(self):
        cases = (
            (400, "invalid_request", 400),
            (401, "authentication_failed", 502),
            (403, "authentication_failed", 502),
            (402, "quota_exhausted", 503),
            (429, "rate_limited", 429),
            (408, "upstream_timeout", 504),
            (500, "upstream_unavailable", 502),
            (502, "upstream_unavailable", 502),
            (503, "upstream_unavailable", 502),
            (504, "upstream_timeout", 504),
            (302, "invalid_upstream_response", 502),
        )
        for status, code, local_status in cases:
            with self.subTest(status=status):
                body = io.BytesIO(b"private-upstream-body sentinel-sponsored-secret")

                def opener(*args, **kwargs):
                    raise urllib.error.HTTPError(
                        providers.SPONSOREDTOKENS_ENDPOINT, status, "raw-upstream-exception",
                        {"private-header": "sentinel-sponsored-secret"}, body,
                    )

                with self.assertRaises(providers.ProviderError) as caught:
                    providers.call_sponsoredtokens(self.config, self.messages, opener=opener)
                self.assert_safe_error(caught.exception, code, local_status)
                self.assertTrue(body.closed)

    def test_network_and_timeout_errors_do_not_expose_raw_exception(self):
        cases = (
            (urllib.error.URLError("raw-upstream-exception sentinel-sponsored-secret"), "upstream_unavailable", 502),
            (TimeoutError("raw-upstream-exception sentinel-sponsored-secret"), "upstream_timeout", 504),
            (urllib.error.URLError(TimeoutError("sentinel-sponsored-secret")), "upstream_timeout", 504),
            (OSError("raw-upstream-exception sentinel-sponsored-secret"), "upstream_unavailable", 502),
        )
        for failure, code, status in cases:
            with self.subTest(failure=type(failure).__name__):
                def opener(*args, **kwargs):
                    raise failure

                with self.assertRaises(providers.ProviderError) as caught:
                    providers.call_sponsoredtokens(self.config, self.messages, opener=opener)
                self.assert_safe_error(caught.exception, code, status)

    def test_protocol_and_partial_read_failures_are_normalized(self):
        cases = (
            (http.client.IncompleteRead(b"sentinel-sponsored-secret"), "upstream_unavailable", 502),
            (http.client.BadStatusLine("raw-upstream-exception sentinel-sponsored-secret"), "upstream_unavailable", 502),
            (TimeoutError("sentinel-sponsored-secret"), "upstream_timeout", 504),
        )
        for failure, code, status in cases:
            with self.subTest(failure=type(failure).__name__):
                class BrokenResponse(FakeResponse):
                    def read(self, size):
                        raise failure

                response = BrokenResponse(b"")
                with self.assertRaises(providers.ProviderError) as caught:
                    providers.call_sponsoredtokens(
                        self.config, self.messages, opener=lambda *args, **kwargs: response,
                    )
                self.assert_safe_error(caught.exception, code, status)
                self.assertTrue(response.closed)

    def test_malformed_and_oversized_responses_are_safe_errors(self):
        for body in (
            b"private-upstream-body sentinel-sponsored-secret",
            b"\xff", b"[]", b"null", b"{}", b'{"output_text":42}',
            b'{"output_text":"  "}', b'{"output":null}',
            b'{"output_text":"ok","value":NaN}',
            b"x" * 1_048_577,
        ):
            with self.subTest(body_length=len(body)):
                response = FakeResponse(body)
                with self.assertRaises(providers.ProviderError) as caught:
                    providers.call_sponsoredtokens(
                        self.config, self.messages, opener=lambda *args, **kwargs: response,
                    )
                self.assert_safe_error(caught.exception, "invalid_upstream_response", 502)
                self.assertTrue(response.closed)

    def test_accepts_a_response_at_exact_read_limit(self):
        body = b'{"output_text":"ok"}'
        body += b" " * (1_048_576 - len(body))
        self.assertEqual(providers.call_sponsoredtokens(
            self.config, self.messages, opener=lambda *args, **kwargs: FakeResponse(body),
        ).text, "ok")

    def test_extracts_top_level_unicode_and_exact_sponsor_footer(self):
        text = "  Olá 🌍\n\nSponsored by Example — https://example.test\n "
        self.assertEqual(providers.extract_response_text({"output_text": text}), text)

    def test_extracts_nested_responses_output_without_adding_or_removing_text(self):
        self.assertEqual(providers.extract_response_text({
            "output": [
                {"type": "reasoning", "summary": []},
                {"type": "message", "role": "assistant", "content": [
                    {"type": "output_text", "text": "Olá 🌍\n"},
                    {"type": "output_text", "text": "\nSponsored by Example\n "},
                ]},
            ],
        }), "Olá 🌍\n\nSponsored by Example\n ")

    def test_extraction_rejects_missing_non_text_or_empty_output(self):
        for payload in (
            None, [], "text", {}, {"output_text": 7},
            {"output": [{"type": "message", "content": [{"type": "refusal", "refusal": "no"}]}]},
            {"output": [{"type": "message", "content": [{"type": "output_text", "text": 7}]}]},
            {"output": [{"type": "message", "content": [{"type": "output_text", "text": " \t"}]}]},
            {"output": [None]}, {"output": [{"content": None}]},
        ):
            with self.subTest(payload=payload):
                with self.assertRaises(providers.ProviderError) as caught:
                    providers.extract_response_text(payload)
                self.assert_safe_error(caught.exception, "invalid_upstream_response", 502)

    def test_success_echoing_the_configured_key_is_rejected(self):
        body = json.dumps({
            "output_text": "Resposta sentinel-sponsored-secret\n\nSponsored by Example\n ",
        }).encode()
        with self.assertRaises(providers.ProviderError) as caught:
            providers.call_sponsoredtokens(
                self.config, self.messages,
                opener=lambda *args, **kwargs: FakeResponse(body),
            )
        self.assert_safe_error(caught.exception, "invalid_upstream_response", 502)


class ValidateBindHostTests(unittest.TestCase):
    def test_accepts_only_ipv4_loopback(self):
        self.assertEqual(validate_bind_host("127.0.0.1"), "127.0.0.1")

    def test_rejects_non_loopback_hosts_without_echoing_input(self):
        for host in ("0.0.0.0", "localhost", "::1", "192.168.1.5", "secret-host"):
            with self.subTest(host=host):
                with self.assertRaises(RequestValidationError) as caught:
                    validate_bind_host(host)
                self.assertNotIn(host, str(caught.exception))
                self.assertNotIn(host, caught.exception.code)


class ValidateMessagesTests(unittest.TestCase):
    def test_preserves_a_unicode_conversation(self):
        messages = [
            {"role": "user", "content": "Olá, mundo 🌍"},
            {"role": "assistant", "content": "こんにちは"},
        ]
        self.assertEqual(validate_messages(messages), messages)

    def test_rejects_empty_history(self):
        with self.assertRaises(RequestValidationError):
            validate_messages([])

    def test_rejects_non_list_history(self):
        for value in (None, {}, "conversation", ()):
            with self.subTest(value=type(value).__name__):
                with self.assertRaises(RequestValidationError):
                    validate_messages(value)

    def test_rejects_more_than_one_hundred_messages(self):
        history = [{"role": "user", "content": "hi"}] * 101
        with self.assertRaises(RequestValidationError):
            validate_messages(history)

    def test_accepts_exactly_one_hundred_messages(self):
        history = [{"role": "user", "content": "hi"}] * 100
        self.assertEqual(validate_messages(history), history)

    def test_accepts_content_at_limit_without_normalizing(self):
        content = " " + "á" * (MAX_CONTENT_CHARS - 2) + " "
        self.assertEqual(
            validate_messages([{"role": "user", "content": content}]),
            [{"role": "user", "content": content}],
        )

    def test_rejects_malformed_messages(self):
        for message in (None, [], "message", {}, {"role": "user"}, {"content": "hi"}):
            with self.subTest(message=message):
                with self.assertRaises(RequestValidationError):
                    validate_messages([message])

    def test_rejects_unknown_roles(self):
        for role in ("system", "tool", "", None, 42, [], {}):
            with self.subTest(role=role):
                with self.assertRaises(RequestValidationError) as caught:
                    validate_messages([{"role": role, "content": "hidden"}])
                self.assertNotIn("hidden", caught.exception.message)
                self.assertNotIn("hidden", caught.exception.code)

    def test_rejects_unknown_message_fields_without_echoing_submitted_text(self):
        secret = "private-token-value"
        with self.assertRaises(RequestValidationError) as caught:
            validate_messages([{"role": "user", "content": "hello", "token": secret}])
        self.assertNotIn(secret, str(caught.exception))
        self.assertNotIn(secret, caught.exception.code)

    def test_rejects_blank_content(self):
        for content in ("", " \t\n"):
            with self.subTest(content=repr(content)):
                with self.assertRaises(RequestValidationError):
                    validate_messages([{"role": "user", "content": content}])

    def test_rejects_non_string_content(self):
        with self.assertRaises(RequestValidationError):
            validate_messages([{"role": "user", "content": 42}])

    def test_rejects_content_above_limit_without_truncating_or_echoing(self):
        too_long = "x" * (MAX_CONTENT_CHARS + 1)
        with self.assertRaises(RequestValidationError) as caught:
            validate_messages([{"role": "user", "content": too_long}])
        self.assertNotIn(too_long, str(caught.exception))
        self.assertNotIn(too_long, caught.exception.code)


if __name__ == "__main__":
    unittest.main()
