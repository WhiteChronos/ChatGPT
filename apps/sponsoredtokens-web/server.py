"""Secure loopback HTTP boundary for the local SponsoredTokens chat."""

import argparse
import json
import os
import webbrowser
from collections.abc import Mapping, Sequence
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

from providers import (
    SPONSOREDTOKENS_MODEL,
    ProviderError,
    ProviderResult,
    SponsoredTokensConfig,
    call_sponsoredtokens,
)

MAX_BODY_BYTES = 1_048_576
MAX_MESSAGES = 100
MAX_CONTENT_CHARS = 20_000


class RequestValidationError(ValueError):
    """A safe-to-display request validation failure."""

    def __init__(self, code: str = "invalid_request", message: str = "Invalid request"):
        self.code = code
        self.message = message
        super().__init__(message)


def validate_bind_host(host: str) -> str:
    """Return the only permitted bind host: IPv4 loopback."""
    if host != "127.0.0.1":
        raise RequestValidationError("invalid_bind_host", "Bind host must be 127.0.0.1")
    return host


def validate_messages(value: object) -> list[dict[str, str]]:
    """Validate and return a bounded user/assistant message history."""
    if not isinstance(value, list) or not value:
        raise RequestValidationError("invalid_messages", "Messages must be a non-empty list")
    if len(value) > MAX_MESSAGES:
        raise RequestValidationError("too_many_messages", "Message history exceeds the limit")

    validated: list[dict[str, str]] = []
    for message in value:
        if not isinstance(message, dict) or set(message) != {"role", "content"}:
            raise RequestValidationError("invalid_message", "Each message must contain role and content")

        role = message["role"]
        if role not in ("user", "assistant"):
            raise RequestValidationError("invalid_role", "Message role is not supported")

        content = message["content"]
        if not isinstance(content, str):
            raise RequestValidationError("invalid_content", "Message content must be text")
        if not content.strip():
            raise RequestValidationError("blank_content", "Message content must not be blank")
        if len(content) > MAX_CONTENT_CHARS:
            raise RequestValidationError("content_too_long", "Message content exceeds the limit")

        validated.append({"role": role, "content": content})

    return validated


_STATIC_DIR = Path(__file__).resolve().parent / "static"
_STATIC_ROUTES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.css": ("app.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}
_SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; connect-src 'self'; img-src 'self'; "
        "style-src 'self'; script-src 'self'; base-uri 'none'; "
        "form-action 'self'; frame-ancestors 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}


def make_handler(
    config: SponsoredTokensConfig,
    transport: Callable = call_sponsoredtokens,
):
    """Build a request handler closed over one immutable provider config."""

    class LocalChatHandler(BaseHTTPRequestHandler):
        server_version = "SponsoredTokensLocalChat"
        sys_version = ""

        def log_message(self, format, *args):
            return

        def _valid_request_authority(self) -> bool:
            if self.path.startswith(("http://", "https://", "//")):
                return False
            host_values = self.headers.get_all("Host", failobj=[])
            expected = f"127.0.0.1:{self.server.server_address[1]}"
            return host_values == [expected]

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            for name, value in _SECURITY_HEADERS.items():
                self.send_header(name, value)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def _send_json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            self._send(status, body, "application/json; charset=utf-8")

        def _error(self, status: int, code: str) -> None:
            self._send_json(status, {"error": code})

        def _require_authority(self) -> bool:
            if self._valid_request_authority():
                return True
            self.close_connection = True
            self._error(400, "invalid_request")
            return False

        def do_GET(self):
            if not self._require_authority():
                return
            if self.path == "/api/health":
                ready = bool(config.api_key and config.api_key.strip())
                self._send_json(200, {
                    "ready": ready,
                    "provider": "SponsoredTokens",
                    "model": SPONSOREDTOKENS_MODEL,
                })
                return
            asset = _STATIC_ROUTES.get(self.path)
            if asset is None:
                self._error(404, "not_found")
                return
            filename, content_type = asset
            self._send(200, (_STATIC_DIR / filename).read_bytes(), content_type)

        def do_POST(self):
            if not self._require_authority():
                return
            if self.path != "/api/chat":
                self._error(404, "not_found")
                return
            lengths = self.headers.get_all("Content-Length", failobj=[])
            if len(lengths) != 1:
                self.close_connection = True
                self._error(411, "length_required")
                return
            try:
                length = int(lengths[0])
            except (TypeError, ValueError):
                self.close_connection = True
                self._error(400, "invalid_request")
                return
            if length < 0:
                self.close_connection = True
                self._error(400, "invalid_request")
                return
            if length > MAX_BODY_BYTES:
                self.close_connection = True
                self._error(413, "body_too_large")
                return
            body = self.rfile.read(length)
            if len(body) != length:
                self.close_connection = True
                self._error(400, "invalid_request")
                return
            try:
                payload = json.loads(body.decode("utf-8"))
                if not isinstance(payload, dict) or set(payload) != {"messages"}:
                    raise RequestValidationError()
                messages = validate_messages(payload["messages"])
            except (UnicodeDecodeError, json.JSONDecodeError, RequestValidationError):
                self._error(400, "invalid_request")
                return
            try:
                result: ProviderResult = transport(config, messages)
            except ProviderError as error:
                self._error(error.http_status, error.code)
                return
            except Exception:
                self._error(502, "upstream_unavailable")
                return
            self._send_json(200, {
                "text": result.text,
                "provider": result.provider,
                "model": result.model,
            })

        def _method_not_allowed(self):
            if not self._require_authority():
                return
            self._error(405, "method_not_allowed")

        do_DELETE = _method_not_allowed
        do_HEAD = _method_not_allowed
        do_OPTIONS = _method_not_allowed
        do_PATCH = _method_not_allowed
        do_PUT = _method_not_allowed
        do_TRACE = _method_not_allowed

    return LocalChatHandler


def create_server(
    config: SponsoredTokensConfig,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    transport: Callable = call_sponsoredtokens,
) -> ThreadingHTTPServer:
    """Create, but do not start, an IPv4 loopback-only threaded server."""
    validated_host = validate_bind_host(host)
    server = ThreadingHTTPServer((validated_host, port), make_handler(config, transport))
    server.daemon_threads = True
    return server


def load_config_from_environment(environ: Mapping[str, str]) -> SponsoredTokensConfig:
    """Read the one credential owned by this application."""
    return SponsoredTokensConfig(environ.get("SPONSOREDTOKENS_API_KEY"))


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("port must be an integer") from error
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chat local privado via SponsoredTokens")
    parser.add_argument("--port", type=_port, default=8765, help="porta local (padrao: 8765)")
    parser.add_argument("--open", action="store_true", help="abrir o navegador apos iniciar")
    parser.add_argument(
        "--live-smoke", action="store_true",
        help="executar uma unica chamada real e sair",
    )
    return parser.parse_args(argv)


def run_live_smoke(config: SponsoredTokensConfig) -> bool:
    """Run one explicit live request and print only safe status metadata."""
    if not config.api_key or not config.api_key.strip():
        print("LIVE_SMOKE=FAIL code=configuration_required")
        return False
    try:
        result = call_sponsoredtokens(
            config, [{"role": "user", "content": "Responda apenas: OK"}],
        )
    except ProviderError as error:
        print(f"LIVE_SMOKE=FAIL code={error.code}")
        return False
    print(f"LIVE_SMOKE=PASS provider={result.provider} model={result.model}")
    return True


def main(argv: Sequence[str] | None = None) -> int:
    options = parse_args(argv)
    config = load_config_from_environment(os.environ)
    if options.live_smoke:
        return 0 if run_live_smoke(config) else 1

    server = create_server(config, port=options.port)
    actual_port = server.server_address[1]
    url = f"http://127.0.0.1:{actual_port}/"
    readiness = "ready" if config.api_key and config.api_key.strip() else "configuration_required"
    print(f"URL={url}")
    print(f"provider=SponsoredTokens model={SPONSOREDTOKENS_MODEL} readiness={readiness}")
    if options.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
