from __future__ import annotations

import stat
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.codex_probe import probe_codex_cli


def _make_executable(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def test_fake_codex_reports_broker_compatible_capabilities():
    fake = REPO / "plugins" / "subagent-broker" / "tests" / "fake-codex.mjs"
    caps = probe_codex_cli(str(fake))
    assert caps.version == "codex-cli 99.0.0"
    assert caps.exec is True
    assert caps.json is True
    assert caps.resume is True
    assert caps.sandbox_read_only is True
    assert caps.sandbox_workspace_write is True
    assert caps.approval_never is True


def test_missing_codex_is_unavailable_without_exception(tmp_path):
    caps = probe_codex_cli(str(tmp_path / "does-not-exist"))
    assert caps.version == "unavailable"
    assert caps.exec is False
    assert caps.json is False
    assert caps.resume is False


def test_exec_without_json_is_not_smoke_capable(tmp_path):
    fake = _make_executable(
        tmp_path / "codex-no-json",
        "#!/bin/sh\nif [ \"$1\" = \"--version\" ]; then echo 'codex-cli 1'; exit 0; fi\nif [ \"$1\" = \"exec\" ]; then echo 'Usage: codex exec [--sandbox MODE]'; exit 0; fi\nexit 1\n",
    )
    caps = probe_codex_cli(str(fake))
    assert caps.exec is True
    assert caps.json is False


def test_probe_never_runs_a_model_task(tmp_path):
    fake = _make_executable(
        tmp_path / "codex-recording",
        "#!/usr/bin/env python3\nimport pathlib,sys\np=pathlib.Path(__file__).with_name('calls.txt')\nwith p.open('a') as f:f.write(' '.join(sys.argv[1:])+'\\n')\na=sys.argv[1:]\nif a==['--version']: print('codex-cli test'); raise SystemExit(0)\nif a==['exec','--help']: print('Usage: codex exec [--json]'); raise SystemExit(0)\nif a==['exec','resume','--help']: print('Usage: codex exec resume SESSION -'); raise SystemExit(0)\nraise SystemExit(99)\n",
    )
    caps = probe_codex_cli(str(fake))
    assert caps.exec is True
    calls = (tmp_path / "calls.txt").read_text().splitlines()
    assert calls == ["--version", "exec --help", "exec resume --help"]
