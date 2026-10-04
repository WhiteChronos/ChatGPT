from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
MODULE = REPO / "pipeline" / "github_path_policy.py"
CODEOWNERS = REPO / ".github" / "CODEOWNERS"


def _load_module():
    spec = importlib.util.spec_from_file_location("github_path_policy", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GitHub path policy module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (".github/workflows/test.yml", "CONTROL_PLANE_CRITICAL"),
        (".github/CODEOWNERS", "CONTROL_PLANE_CRITICAL"),
        ("AGENTS.md", "CONTROL_PLANE_CRITICAL"),
        ("governance/policy.md", "CONTROL_PLANE_CRITICAL"),
        ("pipeline/gate.py", "CONTROL_PLANE_CRITICAL"),
        ("schemas/x.schema.json", "CONTROL_PLANE_CRITICAL"),
        (
            "plugins/whitechronos-control-plane/runtime/doctor.py",
            "RUNTIME_CONTROL",
        ),
        ("plugins/subagent-broker/server.mjs", "RUNTIME_CONTROL"),
        (".codex/config.toml", "RUNTIME_CONTROL"),
        (".agents/plugins/marketplace.json", "RUNTIME_CONTROL"),
        ("memory/state.md", "DURABLE_STATE"),
        ("history/runtime/event.json", "DURABLE_STATE"),
        ("registry/integrations/x.json", "DURABLE_STATE"),
        ("datacenter/x.json", "DURABLE_STATE"),
        ("datasheet/x.json", "DURABLE_STATE"),
        ("docs/guide.md", "DOCUMENTATION"),
        ("mkdocs.yml", "DOCUMENTATION"),
        ("README.md", "OTHER"),
    ],
)
def test_classify_path(path, expected):
    module = _load_module()
    assert module.classify_path(path) == expected


def test_windows_separators_are_normalized():
    module = _load_module()
    assert (
        module.classify_path(r"plugins\whitechronos-control-plane\runtime\doctor.py")
        == "RUNTIME_CONTROL"
    )


@pytest.mark.parametrize(
    "path",
    (
        "/absolute/path.txt",
        "../escape.txt",
        "docs/../../escape.txt",
        "C:/absolute/path.txt",
    ),
)
def test_unsafe_paths_are_rejected(path):
    module = _load_module()
    with pytest.raises(ValueError, match="unsafe|absolute|parent"):
        module.classify_path(path)


def test_classify_paths_is_deterministic_and_sorted():
    module = _load_module()
    result = module.classify_paths(
        [
            "README.md",
            "memory/z.md",
            "pipeline/b.py",
            "memory/a.md",
            "docs/x.md",
        ]
    )
    assert list(result) == [
        "CONTROL_PLANE_CRITICAL",
        "RUNTIME_CONTROL",
        "DURABLE_STATE",
        "DOCUMENTATION",
        "OTHER",
    ]
    assert result["DURABLE_STATE"] == ["memory/a.md", "memory/z.md"]


def test_codeowners_covers_every_critical_root():
    text = CODEOWNERS.read_text(encoding="utf-8")
    required_lines = {
        "/datacenter/ @WhiteChronos",
        "/datasheet/ @WhiteChronos",
        "/schemas/ @WhiteChronos",
        "/governance/ @WhiteChronos",
        "/pipeline/ @WhiteChronos",
        "/memory/ @WhiteChronos",
        "/history/ @WhiteChronos",
        "/registry/ @WhiteChronos",
        "/plugins/whitechronos-control-plane/ @WhiteChronos",
        "/plugins/subagent-broker/ @WhiteChronos",
        "/.codex/ @WhiteChronos",
        "/.agents/ @WhiteChronos",
        "/AGENTS.md @WhiteChronos",
        "/.github/workflows/ @WhiteChronos",
        "/.github/CODEOWNERS @WhiteChronos",
    }
    lines = {line.strip() for line in text.splitlines() if line.strip()}
    assert required_lines <= lines
