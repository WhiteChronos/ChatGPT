"""Exercise the real recovery script with a local, non-network CLI fixture."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

REA = Path(__file__).resolve().parents[1]
PWSH = shutil.which("pwsh") or shutil.which("powershell")
pytestmark = pytest.mark.skipif(not PWSH, reason="PowerShell is required")


@pytest.mark.parametrize("stage", ["existing", "connected", "stale"])
@pytest.mark.parametrize("identity", ["match", "other-tunnel", "other-process-tunnel", "other-root", "double-root", "other-kind", "missing-tunnel", "missing-process", "missing-command"])
def test_recovery_requires_expected_runtime_identity(tmp_path, stage, identity):
    root = tmp_path / "authorized source"
    root.mkdir()
    command = f'"{sys.executable}" "{REA / "src" / "sdk_server.py"}" --root "{root}" --transport stdio'
    status = {
        "process_running": True, "healthy": True, "ready": True,
        "tunnel_id": "tunnel_expected",
        "process": {"tunnel_id": "tunnel_expected", "target_kind": "command", "target_value": command},
    }
    if identity == "other-tunnel":
        status["tunnel_id"] = "tunnel_other"
    elif identity == "other-process-tunnel":
        status["process"]["tunnel_id"] = "tunnel_other"
    elif identity == "other-root":
        status["process"]["target_value"] = command.replace(str(root), str(tmp_path / "other source"))
    elif identity == "double-root":
        status["process"]["target_value"] += ' --root "C:\\other"'
    elif identity == "other-kind":
        status["process"]["target_kind"] = "url"
    elif identity == "missing-tunnel":
        del status["tunnel_id"]
    elif identity == "missing-process":
        del status["process"]
    elif identity == "missing-command":
        del status["process"]["target_value"]
    fixture = tmp_path / "status.json"
    fixture.write_text(json.dumps(status), encoding="utf-8")
    calls = tmp_path / "calls.txt"
    client = tmp_path / "fake-client.ps1"
    client.write_text('''
Add-Content -LiteralPath $env:REA_TEST_CALLS -Value ($args -join " ")
if ($args[1] -eq "status") {
    if ($env:REA_TEST_STAGE -eq "connected" -and -not (Test-Path ($env:REA_TEST_CALLS + ".connected"))) { exit 1 }
    $status = Get-Content -LiteralPath $env:REA_TEST_STATUS -Raw | ConvertFrom-Json
    if ($env:REA_TEST_STAGE -eq "stale" -and -not (Test-Path ($env:REA_TEST_CALLS + ".connected"))) { $status.process_running = $false }
    $status | ConvertTo-Json -Depth 8
}
if ($args[1] -eq "connect") { Set-Content -LiteralPath ($env:REA_TEST_CALLS + ".connected") -Value yes }
exit 0
''', encoding="utf-8")
    env = dict(os.environ, CONTROL_PLANE_API_KEY="synthetic-test-only", REA_TEST_CALLS=str(calls),
               REA_TEST_STATUS=str(fixture), REA_TEST_STAGE=stage)
    result = subprocess.run([PWSH, "-NoProfile", "-File", str(REA / "scripts" / "recover_tunnel.ps1"),
                             "-TunnelClient", str(client), "-TunnelId", "tunnel_expected",
                             "-CodeRoot", str(root), "-Python", sys.executable],
                            capture_output=True, text=True, env=env, timeout=30)
    if identity == "match":
        assert result.returncode == 0, result.stderr
    else:
        assert result.returncode != 0, "accepted an unrelated or unidentified healthy runtime"
        assert "identity" in result.stderr.lower(), result.stderr
    commands = calls.read_text(encoding="utf-8-sig").splitlines()
    expected_connects = stage == "connected" or (stage == "stale" and identity == "match")
    assert sum(line.startswith("runtimes connect") for line in commands) == expected_connects
    assert "synthetic-test-only" not in result.stdout + result.stderr + "\n".join(commands)
