from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.cloud_model import (
    CloudEnvironmentProfile,
    CloudNetworkPolicy,
    CloudRepositorySpec,
    CloudToolchainSpec,
)


def _profile(role2: str = "broker") -> CloudEnvironmentProfile:
    return CloudEnvironmentProfile(
        "whitechronos-codex-cloud/v1",
        "whitechronos-control-plane",
        "codex_cloud",
        (
            CloudRepositorySpec("WhiteChronos/ChatGPT", "consumer", True),
            CloudRepositorySpec(
                "WhiteChronos/subagent-broker-runtime",
                role2,
                True,
            ),
        ),
        CloudToolchainSpec((3, 11), 22, True, True, True, True, True),
        CloudNetworkPolicy("explicit_allowlist", ("registry.npmjs.org",)),
        (),
    )


def _paths(tmp_path: Path) -> dict[str, Path]:
    consumer = tmp_path / "consumer"
    broker = tmp_path / "broker"
    consumer.mkdir()
    broker.mkdir()
    (consumer / "requirements-dev.txt").write_text("pytest==8.4.1\n")
    (broker / "package-lock.json").write_text("{}\n")
    (broker / "package.json").write_text('{"name":"broker"}\n')
    return {
        "WhiteChronos/ChatGPT": consumer,
        "WhiteChronos/subagent-broker-runtime": broker,
    }


def test_bootstrap_plan_contains_only_approved_role_commands(tmp_path):
    from runtime.cloud_bootstrap import build_bootstrap_plan

    steps = build_bootstrap_plan(_profile(), _paths(tmp_path))
    assert tuple(step.argv for step in steps) == (
        (sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"),
        ("npm", "ci"),
    )


def test_unknown_repository_role_fails_closed(tmp_path):
    from runtime.cloud_bootstrap import build_bootstrap_plan

    with pytest.raises(ValueError, match="unknown repository role"):
        build_bootstrap_plan(_profile("untrusted"), _paths(tmp_path))


def test_dry_run_executes_nothing(tmp_path, monkeypatch):
    import runtime.cloud_bootstrap as cb

    steps = cb.build_bootstrap_plan(_profile(), _paths(tmp_path))
    monkeypatch.setattr(
        cb.subprocess,
        "run",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("executed")),
    )
    results = cb.execute_bootstrap_plan(steps, apply=False)
    assert [r.returncode for r in results] == [0, 0]
    assert all(r.stdout_tail == "DRY_RUN" for r in results)


def test_apply_uses_shell_false_and_expected_cwd(tmp_path, monkeypatch):
    import runtime.cloud_bootstrap as cb

    steps = cb.build_bootstrap_plan(_profile(), _paths(tmp_path))
    calls = []

    class R:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(argv, **kwargs):
        calls.append((tuple(argv), kwargs))
        return R()

    monkeypatch.setattr(cb.subprocess, "run", fake_run)
    results = cb.execute_bootstrap_plan(steps, apply=True)
    assert len(results) == 2
    assert [call[1]["shell"] for call in calls] == [False, False]
    assert [Path(call[1]["cwd"]) for call in calls] == [steps[0].cwd, steps[1].cwd]


def test_failed_step_stops_later_steps(tmp_path, monkeypatch):
    import runtime.cloud_bootstrap as cb

    steps = cb.build_bootstrap_plan(_profile(), _paths(tmp_path))
    calls = []

    class R:
        def __init__(self, code):
            self.returncode = code
            self.stdout = ""
            self.stderr = "boom"

    def fake_run(argv, **kwargs):
        calls.append(tuple(argv))
        return R(7)

    monkeypatch.setattr(cb.subprocess, "run", fake_run)
    results = cb.execute_bootstrap_plan(steps, apply=True)
    assert len(calls) == 1
    assert len(results) == 1
    assert results[0].returncode == 7


def test_output_is_bounded_and_does_not_include_environment_dump(tmp_path, monkeypatch):
    import runtime.cloud_bootstrap as cb

    steps = cb.build_bootstrap_plan(_profile(), _paths(tmp_path))[:1]

    class R:
        returncode = 0
        stdout = "x" * 12000
        stderr = "SECRET_SHOULD_NOT_BE_IN_ENV" * 500

    monkeypatch.setattr(cb.subprocess, "run", lambda *a, **k: R())
    result = cb.execute_bootstrap_plan(steps, apply=True)[0]
    assert len(result.stdout_tail) <= 4096
    assert len(result.stderr_tail) <= 4096
    assert not hasattr(result, "environment")
