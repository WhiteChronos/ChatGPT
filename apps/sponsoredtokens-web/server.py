"""Shared request validation for the local SponsoredTokens chat server."""

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
