"""Bounded SponsoredTokens Responses transport for the local-only chat."""

import http.client
import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Callable

from routing import DEFAULT_MODEL, select_model

SPONSOREDTOKENS_ENDPOINT = "https://sponsoredtokens.com/api/v1/responses"
SPONSOREDTOKENS_MODEL = DEFAULT_MODEL
UPSTREAM_TIMEOUT_SECONDS = 30
MAX_RESPONSE_BYTES = 1_048_576

_ERRORS = {
    "configuration_required": (503, "Provider configuration is required"),
    "authentication_failed": (502, "Provider authentication failed"),
    "quota_exhausted": (503, "Provider quota is exhausted"),
    "rate_limited": (429, "Provider rate limit reached"),
    "upstream_timeout": (504, "Provider request timed out"),
    "upstream_unavailable": (502, "Provider is unavailable"),
    "invalid_request": (400, "Provider rejected the request"),
    "invalid_upstream_response": (502, "Provider returned an invalid response"),
}
@dataclass(frozen=True)
class SponsoredTokensConfig:
    api_key: str | None = field(repr=False)
    jev_api_key: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class ProviderResult:
    text: str
    provider: str
    model: str
    router: str = "fixed"


class ProviderError(Exception):
    """Stable local errors; upstream bodies and exception details are discarded."""

    def __init__(self, code: str):
        self.code = code if code in _ERRORS else "upstream_unavailable"
        self.http_status, self.message = _ERRORS[self.code]
        super().__init__(self.message)


def build_upstream_payload(messages: list[dict[str, str]], model: str) -> dict:
    """Copy a previously validated history into Responses input, unchanged."""
    return {"model": model, "input": [dict(message) for message in messages]}


def extract_response_text(payload: object) -> str:
    """Return complete text verbatim, including whitespace and sponsor footer."""
    if isinstance(payload, dict):
        text = payload.get("output_text")
        if isinstance(text, str) and text.strip():
            return text

        output = payload.get("output")
        chunks = []
        if isinstance(output, list):
            for item in output:
                if not isinstance(item, dict) or item.get("type") != "message":
                    continue
                content = item.get("content")
                if not isinstance(content, list):
                    continue
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "output_text":
                        chunk = part.get("text")
                        if not isinstance(chunk, str):
                            raise ProviderError("invalid_upstream_response")
                        chunks.append(chunk)
        text = "".join(chunks)
        if text.strip():
            return text
    raise ProviderError("invalid_upstream_response")


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Never forward a provider credential or message to a redirected URL."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _http_error_code(status: int) -> str:
    if status in (401, 403):
        return "authentication_failed"
    if status == 402:
        return "quota_exhausted"
    if status == 429:
        return "rate_limited"
    if status in (408, 504):
        return "upstream_timeout"
    if 500 <= status <= 599:
        return "upstream_unavailable"
    if 400 <= status <= 499:
        return "invalid_request"
    return "invalid_upstream_response"


def _reject_json_constant(value: str):
    raise ValueError("Non-standard JSON number")


def call_sponsoredtokens(
    config: SponsoredTokensConfig,
    messages: list[dict[str, str]],
    *,
    opener: Callable = urllib.request.urlopen,
    decision_opener: Callable | None = None,
) -> ProviderResult:
    """Make one bounded request using only the SponsoredTokens credential."""
    if not config.api_key or not config.api_key.strip():
        raise ProviderError("configuration_required")

    # urllib's default redirect handling can forward Authorization. Build an
    # isolated opener instead; explicitly injected transports remain testable.
    if opener is urllib.request.urlopen:
        opener = urllib.request.build_opener(_NoRedirectHandler()).open

    decision = select_model(config.jev_api_key, messages, opener=decision_opener)
    error_code = None
    try:
        request = urllib.request.Request(
            SPONSOREDTOKENS_ENDPOINT,
            data=json.dumps(
                build_upstream_payload(messages, decision.model), ensure_ascii=False,
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + config.api_key,
            },
            method="POST",
        )
        with opener(request, timeout=UPSTREAM_TIMEOUT_SECONDS) as response:
            # One extra byte detects oversized responses without an unbounded
            # read; no response larger than MAX_RESPONSE_BYTES is accepted.
            body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            error_code = "invalid_upstream_response"
        else:
            payload = json.loads(body, parse_constant=_reject_json_constant)
            text = extract_response_text(payload)
            if config.api_key in text:
                error_code = "invalid_upstream_response"
            else:
                return ProviderResult(text, "SponsoredTokens", decision.model, decision.router)
    except urllib.error.HTTPError as error:
        error_code = _http_error_code(error.code)
        error.close()
    except TimeoutError:
        error_code = "upstream_timeout"
    except urllib.error.URLError as error:
        error_code = "upstream_timeout" if isinstance(error.reason, TimeoutError) else "upstream_unavailable"
    except (OSError, http.client.HTTPException):
        error_code = "upstream_unavailable"
    except (ValueError, RecursionError):
        error_code = "invalid_upstream_response"
    except ProviderError as error:
        error_code = error.code

    # Raise after leaving the except block: raw exceptions are not retained in
    # __context__, __cause__, display text, or logs.
    raise ProviderError(error_code)
