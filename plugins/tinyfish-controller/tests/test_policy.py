from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PLUGIN = REPO / "plugins" / "tinyfish-controller"
SKILL = PLUGIN / "skills" / "tinyfish-controller" / "SKILL.md"
PROVIDER = PLUGIN / "skills" / "tinyfish-controller" / "references" / "provider-contract.md"
RECOVERY = PLUGIN / "skills" / "tinyfish-controller" / "references" / "recovery-matrix.md"


def _skill_text() -> str:
    assert SKILL.exists(), "TinyFish controller Skill missing"
    return SKILL.read_text()


def test_policy_never_requests_or_persists_credentials():
    text = _skill_text()
    lowered = text.lower()
    assert "never request passwords" in lowered
    assert "never persist" in lowered
    assert "tokens" in lowered
    assert "cookies" in lowered


def test_policy_forbids_automatic_profile_and_paid_health_checks():
    text = _skill_text()
    lowered = text.lower()
    assert "do not create browser profiles" in lowered
    assert "routine health" in lowered
    for term in ("agent runs", "browser runs", "monitors", "top-up", "auto-reload"):
        assert term in lowered


def test_policy_prefers_native_github_gitlab_for_repository_work():
    text = _skill_text()
    assert "native GitHub/GitLab connectors" in text
    assert "repository API" in text


def test_profile_failure_is_degraded_independently_of_service_auth():
    text = _skill_text()
    assert "DEGRADED" in text
    assert "Browser Profile" in text
    assert "service" in text.lower()


def test_host_policy_block_is_not_a_source_bug():
    text = _skill_text()
    assert "HOST_POLICY_BLOCKED" in text
    assert "not a source-code defect" in text


def test_monitor_operations_require_explicit_user_intent():
    text = _skill_text()
    assert "monitor" in text.lower()
    assert "explicit" in text.lower()
    assert "user" in text.lower()


def test_browser_timeout_or_error_reuses_existing_run():
    assert PROVIDER.exists(), "TinyFish provider contract missing"
    text = PROVIDER.read_text().lower()
    assert "timeout" in text
    assert "error" in text
    assert "poll the same run" in text
    assert "do not start a duplicate run" in text


def test_recovery_matrix_keeps_profile_error_separate():
    assert RECOVERY.exists(), "TinyFish recovery matrix missing"
    text = RECOVERY.read_text()
    assert "profile" in text.lower()
    assert "DEGRADED" in text
    assert "HOST_POLICY_BLOCKED" in text
