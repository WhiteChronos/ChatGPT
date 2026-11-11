from pathlib import Path

REA = Path(__file__).resolve().parents[1]


def test_persistent_tunnel_runbook_uses_managed_runtime():
    recovery = REA / "scripts" / "recover_tunnel.ps1"
    assert recovery.is_file(), "missing Windows tunnel recovery script"

    private_doc = (REA / "docs" / "PRIVATE_MCP_TUNNEL.md").read_text(encoding="utf-8")
    setup_skill = (REA / "skills" / "rea-setup" / "SKILL.md").read_text(encoding="utf-8")
    script = recovery.read_text(encoding="utf-8")

    for text in (private_doc, setup_skill, script):
        assert "tunnel-client runtimes connect" in text
        assert "tunnel-client runtimes status" in text

    assert "--runtime-api-key" in script
    assert "env:CONTROL_PLANE_API_KEY" in script
    assert "--mcp-command" in script
    assert "process_running" in script
    assert "healthy" in script
    assert "ready" in script
    assert "sk-" not in script
