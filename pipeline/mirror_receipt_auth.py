"""Detached HMAC receipt authentication for a protected GitLab CI verifier.

The signing key must be provisioned separately to two protected environments
only after independent CI configuration and exact worker revocation are verified.
A public SHA-256 receipt digest alone is not proof of worker identity.
"""
from __future__ import annotations

import hashlib
import hmac
import re

_HEX_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


def sign_receipt_digest(digest: str, key: str) -> str:
    if not isinstance(digest, str) or not _HEX_SHA256.fullmatch(digest):
        raise ValueError("receipt digest must be a SHA-256 hex string")
    if not isinstance(key, str) or len(key.encode("utf-8")) < 32:
        raise ValueError("receipt signing key must contain at least 32 bytes")
    return hmac.new(key.encode("utf-8"), bytes.fromhex(digest), hashlib.sha256).hexdigest()


def verify_receipt_digest_signature(digest: str, signature: str, key: str) -> bool:
    if not isinstance(signature, str) or not _HEX_SHA256.fullmatch(signature):
        return False
    try:
        expected = sign_receipt_digest(digest, key)
    except ValueError:
        return False
    return hmac.compare_digest(expected, signature.lower())
