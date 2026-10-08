from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))


def _api():
    assert importlib.util.find_spec("runtime.connection_models") is not None, "connection_models module missing"
    assert importlib.util.find_spec("runtime.connections") is not None, "connections module missing"
    models = importlib.import_module("runtime.connection_models")
    connections = importlib.import_module("runtime.connections")
    return models, connections


def _signals(models, **overrides):
    values = {
        "configured": True,
        "host_visible": True,
        "authenticated": None,
        "target_accessible": None,
        "live_verified": None,
        "authentication_required": False,
        "target_required": False,
        "live_verification_required": False,
        "host_absence_status": models.ConnectionStatus.UNAVAILABLE,
        "required_blocker": None,
        "optional_degradations": (),
    }
    values.update(overrides)
    return models.ConnectionSignals(**values)


def test_configured_does_not_imply_host_visible():
    models, connections = _api()
    result = connections.evaluate_connection(
        "github",
        _signals(models, configured=True, host_visible=None),
    )
    assert result.configured is True
    assert result.host_visible is None
    assert result.status is models.ConnectionStatus.UNAVAILABLE


def test_missing_observed_host_can_be_host_reload_required():
    models, connections = _api()
    result = connections.evaluate_connection(
        "github",
        _signals(
            models,
            host_visible=False,
            host_absence_status=models.ConnectionStatus.HOST_RELOAD_REQUIRED,
        ),
    )
    assert result.status is models.ConnectionStatus.HOST_RELOAD_REQUIRED


def test_auth_failure_requires_user_action():
    models, connections = _api()
    result = connections.evaluate_connection(
        "github",
        _signals(
            models,
            authentication_required=True,
            authenticated=False,
        ),
    )
    assert result.status is models.ConnectionStatus.USER_ACTION_REQUIRED


def test_target_failure_is_fail_closed():
    models, connections = _api()
    result = connections.evaluate_connection(
        "github",
        _signals(
            models,
            authentication_required=True,
            authenticated=True,
            target_required=True,
            target_accessible=False,
        ),
    )
    assert result.status is models.ConnectionStatus.FAIL


def test_optional_degradation_returns_degraded_without_blocking_base_capability():
    models, connections = _api()
    result = connections.evaluate_connection(
        "tinyfish",
        _signals(
            models,
            authentication_required=True,
            authenticated=True,
            optional_degradations=("profile_api_error",),
        ),
    )
    assert result.status is models.ConnectionStatus.DEGRADED
    assert result.authenticated is True


def test_required_host_policy_block_wins_over_optional_degradation():
    models, connections = _api()
    result = connections.evaluate_connection(
        "tinyfish",
        _signals(
            models,
            authentication_required=True,
            authenticated=True,
            required_blocker=models.ConnectionStatus.HOST_POLICY_BLOCKED,
            optional_degradations=("profile_api_error",),
        ),
    )
    assert result.status is models.ConnectionStatus.HOST_POLICY_BLOCKED


def test_live_verification_is_required_only_when_requested():
    models, connections = _api()
    optional = connections.evaluate_connection(
        "github",
        _signals(models, live_verified=False, live_verification_required=False),
    )
    required = connections.evaluate_connection(
        "github",
        _signals(models, live_verified=False, live_verification_required=True),
    )
    assert optional.status is models.ConnectionStatus.PASS
    assert required.status is models.ConnectionStatus.FAIL
