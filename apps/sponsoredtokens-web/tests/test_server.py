import copy
import contextlib
import http.client
import io
import json
import re
import socket
import sys
import threading
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


class HttpBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.config = providers.SponsoredTokensConfig("sentinel-sponsored-secret")

        def transport(config, messages):
            self.calls.append((config, copy.deepcopy(messages)))
            return providers.ProviderResult(
                "Resposta 🌍\n\nSponsored by Example\n ",
                "SponsoredTokens",
                providers.SPONSOREDTOKENS_MODEL,
            )

        self.server = __import__("server").create_server(self.config, transport=transport)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        payload = response.read()
        result = response.status, dict(response.getheaders()), payload
        connection.close()
        return result

    def assert_security_headers(self, headers):
        lowered = {key.lower(): value for key, value in headers.items()}
        self.assertIn("default-src 'self'", lowered["content-security-policy"])
        self.assertEqual(lowered["x-content-type-options"], "nosniff")
        self.assertEqual(lowered["referrer-policy"], "no-referrer")
        self.assertEqual(lowered["cache-control"], "no-store")
        self.assertNotIn("access-control-allow-origin", lowered)

    def test_health_reports_fixed_metadata_and_key_readiness(self):
        status, headers, body = self.request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {
            "ready": True,
            "provider": "SponsoredTokens",
            "model": providers.SPONSOREDTOKENS_MODEL,
        })
        self.assert_security_headers(headers)
        self.assertNotIn(b"sentinel-sponsored-secret", body)

        other = __import__("server").create_server(providers.SponsoredTokensConfig(None))
        thread = threading.Thread(target=other.serve_forever, daemon=True)
        thread.start()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", other.server_address[1], timeout=2)
            connection.request("GET", "/api/health")
            response = connection.getresponse()
            payload = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertFalse(payload["ready"])
            connection.close()
        finally:
            other.shutdown()
            other.server_close()
            thread.join(timeout=2)

    def test_chat_returns_exact_result_and_invokes_transport_once(self):
        messages = [{"role": "user", "content": "Olá"}]
        status, headers, body = self.request(
            "POST", "/api/chat",
            json.dumps({"messages": messages}, ensure_ascii=False).encode("utf-8"),
            {"Content-Type": "application/json"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {
            "text": "Resposta 🌍\n\nSponsored by Example\n ",
            "provider": "SponsoredTokens",
            "model": providers.SPONSOREDTOKENS_MODEL,
        })
        self.assertEqual(self.calls, [(self.config, messages)])
        self.assert_security_headers(headers)

    def test_provider_errors_keep_stable_code_and_status(self):
        for code, expected_status in (
            ("configuration_required", 503), ("authentication_failed", 502),
            ("quota_exhausted", 503), ("rate_limited", 429),
            ("upstream_timeout", 504), ("upstream_unavailable", 502),
            ("invalid_request", 400), ("invalid_upstream_response", 502),
        ):
            with self.subTest(code=code):
                server = __import__("server").create_server(
                    self.config,
                    transport=lambda *args, error_code=code: (_ for _ in ()).throw(
                        providers.ProviderError(error_code)
                    ),
                )
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    connection = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=2)
                    body = b'{"messages":[{"role":"user","content":"hi"}]}'
                    connection.request("POST", "/api/chat", body, {"Content-Type": "application/json"})
                    response = connection.getresponse()
                    response_body = response.read()
                    self.assertEqual(response.status, expected_status)
                    self.assertEqual(json.loads(response_body), {"error": code})
                    self.assertNotIn(b"sentinel-sponsored-secret", response_body)
                    connection.close()
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=2)

    def test_rejects_invalid_missing_and_oversized_request_bodies(self):
        cases = (
            (b"not-json", {}, 400),
            (b"\xff", {}, 400),
            (b"{}", {}, 400),
            (b'{"messages":[]}', {}, 400),
            (b"{}", {"Content-Length": str(1_048_577)}, 413),
        )
        for body, headers, expected in cases:
            with self.subTest(body=body[:12], expected=expected):
                supplied = {"Content-Type": "application/json", **headers}
                status, response_headers, response_body = self.request("POST", "/api/chat", body, supplied)
                self.assertEqual(status, expected)
                self.assert_security_headers(response_headers)
                self.assertNotIn(b"sentinel-sponsored-secret", response_body)
        self.assertEqual(self.calls, [])

    def test_rejects_missing_content_length_without_waiting(self):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        connection.putrequest("POST", "/api/chat", skip_host=True)
        connection.putheader("Host", f"127.0.0.1:{self.port}")
        connection.putheader("Content-Type", "application/json")
        connection.endheaders()
        response = connection.getresponse()
        self.assertEqual(response.status, 411)
        self.assertNotIn(b"sentinel-sponsored-secret", response.read())
        connection.close()

    def test_rejects_partial_body(self):
        raw = socket.create_connection(("127.0.0.1", self.port), timeout=2)
        raw.sendall((
            f"POST /api/chat HTTP/1.1\r\nHost: 127.0.0.1:{self.port}\r\n"
            "Content-Type: application/json\r\nContent-Length: 99\r\n\r\n{}"
        ).encode("ascii"))
        raw.shutdown(socket.SHUT_WR)
        response = raw.recv(4096)
        raw.close()
        self.assertIn(b" 400 ", response)
        self.assertNotIn(b"sentinel-sponsored-secret", response)

    def test_rejects_unsupported_method_host_absolute_target_and_traversal(self):
        status, headers, _ = self.request("PUT", "/api/chat")
        self.assertEqual(status, 405)
        self.assert_security_headers(headers)

        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        connection.putrequest("GET", "/api/health", skip_host=True)
        connection.putheader("Host", "evil.example")
        connection.endheaders()
        response = connection.getresponse()
        self.assertEqual(response.status, 400)
        response.read()
        connection.close()

        self.assertEqual(self.request("GET", "http://evil.example/api/health")[0], 400)
        self.assertEqual(self.request("GET", "/%2e%2e/server.py")[0], 404)
        self.assertEqual(self.request("GET", "/unknown")[0], 404)

    def test_static_allowlist_uses_fixed_mime_types(self):
        for path, content_type in (
            ("/", "text/html; charset=utf-8"),
            ("/index.html", "text/html; charset=utf-8"),
            ("/app.css", "text/css; charset=utf-8"),
            ("/app.js", "text/javascript; charset=utf-8"),
        ):
            with self.subTest(path=path):
                status, headers, body = self.request("GET", path)
                self.assertEqual(status, 200)
                self.assertEqual(headers["Content-Type"], content_type)
                self.assertTrue(body)
                self.assert_security_headers(headers)


class AssetPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        static = Path(__file__).resolve().parents[1] / "static"
        cls.html = (static / "index.html").read_text(encoding="utf-8")
        cls.css = (static / "app.css").read_text(encoding="utf-8")
        cls.js = (static / "app.js").read_text(encoding="utf-8")

    def test_html_has_accessible_named_chat_controls(self):
        for element_id in (
            "status", "provider", "model", "messages", "composer",
            "message-input", "send", "retry", "clear",
        ):
            self.assertRegex(self.html, rf'id=["\']{re.escape(element_id)}["\']')
        self.assertIn('aria-live="polite"', self.html)
        self.assertIn('for="message-input"', self.html)
        self.assertIn('type="submit"', self.html)
        self.assertIn('type="button"', self.html)

    def test_assets_are_local_only_and_do_not_offer_provider_selection(self):
        combined = "\n".join((self.html, self.css, self.js))
        for forbidden in (
            "http://", "https://", "OPENAI_API_KEY", "api.openai.com",
            "gpt-5-mini", "provider-select", "fallback", "localStorage",
            "sessionStorage", "document.cookie", "innerHTML",
        ):
            self.assertNotIn(forbidden, combined)
        self.assertIn('href="/app.css"', self.html)
        self.assertIn('src="/app.js"', self.html)

    def test_javascript_keeps_one_in_memory_history_and_renders_text_only(self):
        declarations = re.findall(r"\b(?:const|let)\s+messages\s*=\s*\[\]", self.js)
        self.assertEqual(len(declarations), 1)
        self.assertIn("textContent", self.js)
        self.assertIn("document.createTextNode", self.js)
        self.assertIn("fetch('/api/health'", self.js)
        self.assertIn("fetch('/api/chat'", self.js)
        self.assertIn("JSON.stringify({ messages })", self.js)
        self.assertRegex(self.js, r"\bsubmitting\b")
        self.assertRegex(self.js, r"\bretry\b")
        self.assertRegex(self.js, r"messages\.splice\(0\)")


class CliTests(unittest.TestCase):
    def setUp(self):
        self.module = __import__("server")
        self.key = "sentinel-sponsored-secret"

    def test_environment_loader_reads_only_sponsoredtokens_key(self):
        class TrackedEnvironment(dict):
            def __init__(self):
                super().__init__({"SPONSOREDTOKENS_API_KEY": self_key})
                self.accessed = []

            def get(self, key, default=None):
                self.accessed.append(key)
                return super().get(key, default)

        self_key = self.key
        environ = TrackedEnvironment()
        config = self.module.load_config_from_environment(environ)
        self.assertEqual(config.api_key, self.key)
        self.assertEqual(environ.accessed, ["SPONSOREDTOKENS_API_KEY"])
        self.assertNotIn(self.key, repr(config))

    def test_cli_defaults_and_explicit_options(self):
        defaults = self.module.parse_args([])
        self.assertEqual(defaults.port, 8765)
        self.assertFalse(defaults.open)
        self.assertFalse(defaults.live_smoke)
        options = self.module.parse_args(["--port", "43210", "--open", "--live-smoke"])
        self.assertEqual(options.port, 43210)
        self.assertTrue(options.open)
        self.assertTrue(options.live_smoke)

    def test_cli_refuses_host_override_and_invalid_ports(self):
        for argv in (["--host", "0.0.0.0"], ["--port", "0"], ["--port", "65536"]):
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    self.module.parse_args(argv)

    def test_live_smoke_refuses_missing_key_without_transport(self):
        output = io.StringIO()
        with patch.object(self.module, "call_sponsoredtokens") as transport:
            with contextlib.redirect_stdout(output):
                result = self.module.run_live_smoke(providers.SponsoredTokensConfig(None))
        self.assertFalse(result)
        transport.assert_not_called()
        self.assertEqual(output.getvalue().strip(), "LIVE_SMOKE=FAIL code=configuration_required")

    def test_live_smoke_reports_only_safe_success_metadata(self):
        config = providers.SponsoredTokensConfig(self.key)
        expected = providers.ProviderResult("private response", "SponsoredTokens", providers.SPONSOREDTOKENS_MODEL)
        output = io.StringIO()
        with patch.object(self.module, "call_sponsoredtokens", return_value=expected) as transport:
            with contextlib.redirect_stdout(output):
                result = self.module.run_live_smoke(config)
        self.assertTrue(result)
        messages = transport.call_args.args[1]
        self.assertEqual(messages, [{"role": "user", "content": "Responda apenas: OK"}])
        visible = output.getvalue()
        self.assertIn("LIVE_SMOKE=PASS", visible)
        self.assertIn("provider=SponsoredTokens", visible)
        self.assertIn("model=" + providers.SPONSOREDTOKENS_MODEL, visible)
        self.assertNotIn(self.key, visible)
        self.assertNotIn("private response", visible)

    def test_live_smoke_reports_safe_provider_failure(self):
        output = io.StringIO()
        with patch.object(
            self.module, "call_sponsoredtokens",
            side_effect=providers.ProviderError("upstream_unavailable"),
        ):
            with contextlib.redirect_stdout(output):
                result = self.module.run_live_smoke(providers.SponsoredTokensConfig(self.key))
        self.assertFalse(result)
        self.assertEqual(output.getvalue().strip(), "LIVE_SMOKE=FAIL code=upstream_unavailable")
        self.assertNotIn(self.key, output.getvalue())

    def test_main_opens_browser_only_after_server_is_created(self):
        events = []

        class FakeServer:
            server_address = ("127.0.0.1", 45678)

            def serve_forever(self):
                events.append("serve")
                raise KeyboardInterrupt

            def server_close(self):
                events.append("close")

        def create(*args, **kwargs):
            events.append("bind")
            return FakeServer()

        output = io.StringIO()
        with patch.object(self.module, "load_config_from_environment", return_value=providers.SponsoredTokensConfig(self.key)):
            with patch.object(self.module, "create_server", side_effect=create):
                with patch("webbrowser.open", side_effect=lambda url: events.append(("open", url))):
                    with contextlib.redirect_stdout(output):
                        result = self.module.main(["--port", "45678", "--open"])
        self.assertEqual(result, 0)
        self.assertEqual(events, ["bind", ("open", "http://127.0.0.1:45678/"), "serve", "close"])
        self.assertNotIn(self.key, output.getvalue())


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
