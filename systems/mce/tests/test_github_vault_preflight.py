"""Fail-closed tests for GitHub-only MCE vault preflight (synthetic inputs only)."""
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = "WhiteChronos/mce-document-vault"


@pytest.fixture
def mod():
    path = ROOT / "scripts" / "github_vault_preflight.py"
    assert path.is_file(), "GH-01 implementation missing: github_vault_preflight.py"
    spec = importlib.util.spec_from_file_location("github_vault_preflight", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _metadata(**overrides):
    base = {
        "full_name": EXPECTED,
        "private": True,
        "default_branch": "main",
        "permissions": {"pull": True, "push": True},
    }
    base.update(overrides)
    return base


def test_private_repo_with_push_is_eligible_but_not_a_backup(mod):
    result = mod.evaluate_repository(_metadata(), EXPECTED)
    assert result == {"status": "PASS", "reason": "PRIVATE_REPO_ACCESSIBLE"}


@pytest.mark.parametrize("data,reason", [
    (_metadata(private=False), "REPO_NOT_PRIVATE"),
    (_metadata(full_name="WhiteChronos/ChatGPT"), "WRONG_REPOSITORY"),
    (_metadata(permissions={"pull": True}), "NO_WRITE_PERMISSION"),
    (_metadata(default_branch=""), "NO_DEFAULT_BRANCH"),
    ({"full_name": EXPECTED, "private": True}, "NO_WRITE_PERMISSION"),
])
def test_untrusted_or_incomplete_metadata_blocks(mod, data, reason):
    assert mod.evaluate_repository(data, EXPECTED) == {"status": "BLOCKED", "reason": reason}


def test_missing_token_does_not_call_network(mod):
    def should_not_fetch(*args, **kwargs):
        raise AssertionError("network should never be called without a token")
    result = mod.check_vault(EXPECTED, "", fetcher=should_not_fetch)
    assert result == {"status": "BLOCKED", "reason": "MISSING_TOKEN"}


def test_invalid_slug_does_not_call_network(mod):
    result = mod.check_vault("../secrets", "token", fetcher=lambda *a: (_ for _ in ()).throw(AssertionError("network called")))
    assert result == {"status": "BLOCKED", "reason": "INVALID_REPOSITORY"}


def test_404_is_not_reported_as_repository_absent(mod):
    def missing(*args, **kwargs):
        raise FileNotFoundError("API 404")
    result = mod.check_vault(EXPECTED, "secret-never-print", fetcher=missing)
    assert result == {"status": "BLOCKED", "reason": "VAULT_NOT_ACCESSIBLE"}
    assert "secret-never-print" not in str(result)


def test_fetch_exception_fails_closed_without_secrets(mod):
    def broken(*args, **kwargs):
        raise RuntimeError("Authorization: secret-never-print")
    result = mod.check_vault(EXPECTED, "secret-never-print", fetcher=broken)
    assert result == {"status": "BLOCKED", "reason": "VAULT_CHECK_FAILED"}
    assert "secret-never-print" not in str(result)

def test_fixed_https_origin_and_reject_redirect_without_following(mod, monkeypatch):
    import json

    observed = []

    class Response:
        status = 200

        def read(self, max_bytes):
            assert max_bytes <= 524288
            return json.dumps(_metadata()).encode("utf-8")

    class Connection:
        def __init__(self, host, timeout):
            assert host == "api.github.com"
            assert timeout == 15
            self.requested = False
            self.response = Response()
            observed.append(self)

        def request(self, method, path, headers):
            assert method == "GET"
            assert path == "/repos/" + EXPECTED
            assert headers["Authorization"] == "Bearer a-secret"
            self.requested = True

        def getresponse(self):
            assert self.requested
            return self.response

        def close(self):
            pass

    monkeypatch.setattr(mod.http.client, "HTTPSConnection", Connection)
    assert mod.check_vault(EXPECTED, "a-secret") == {
        "status": "PASS", "reason": "PRIVATE_REPO_ACCESSIBLE"
    }
    assert len(observed) == 1
    Response.status = 302  # next HTTPSConnection receives a redirect response
    assert mod.check_vault(EXPECTED, "a-secret") == {
        "status": "BLOCKED", "reason": "VAULT_CHECK_FAILED"
    }
    assert len(observed) == 2
    assert observed[1].response.status == 302


def test_http_404_is_inaccessible_not_confirmed_nonexistent(mod, monkeypatch):
    class Response:
        status = 404

    class Connection:
        def __init__(self, host, timeout):
            pass

        def request(self, method, path, headers):
            pass

        def getresponse(self):
            return Response()

        def close(self):
            pass

    monkeypatch.setattr(mod.http.client, "HTTPSConnection", Connection)
    assert mod.check_vault(EXPECTED, "a-secret") == {
        "status": "BLOCKED", "reason": "VAULT_NOT_ACCESSIBLE"
    }
