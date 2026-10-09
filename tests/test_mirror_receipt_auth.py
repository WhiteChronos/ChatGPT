from __future__ import annotations

import hashlib

import pytest

from pipeline.mirror_receipt_auth import (
    sign_receipt_digest,
    verify_receipt_digest_signature,
)

DIGEST = hashlib.sha256(b"trusted receipt binding").hexdigest()
TEST_ONLY_KEY = "local-synthetic-review-only-key-material-00001"


def test_valid_receipt_authentication_is_deterministic():
    signed = sign_receipt_digest(DIGEST, TEST_ONLY_KEY)
    assert len(signed) == 64
    assert verify_receipt_digest_signature(DIGEST, signed, TEST_ONLY_KEY)


@pytest.mark.parametrize("malformed", ["", "a" * 63, "x" * 64, "00"])
def test_malformed_detached_signature_fails_closed(malformed):
    assert not verify_receipt_digest_signature(DIGEST, malformed, TEST_ONLY_KEY)


def test_modified_receipt_and_key_cannot_be_authenticated():
    signature = sign_receipt_digest(DIGEST, TEST_ONLY_KEY)
    another_digest = hashlib.sha256(b"different receipt").hexdigest()
    assert not verify_receipt_digest_signature(another_digest, signature, TEST_ONLY_KEY)
    assert not verify_receipt_digest_signature(
        DIGEST, signature, "other-synthetic-review-only-key-material-0001"
    )


def test_key_must_be_entropy_bearing_and_not_hardcoded_short():
    with pytest.raises(ValueError, match="32 bytes"):
        sign_receipt_digest(DIGEST, "test")


def test_signature_is_not_the_secret_key():
    assert TEST_ONLY_KEY not in sign_receipt_digest(DIGEST, TEST_ONLY_KEY)
