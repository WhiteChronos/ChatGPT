"""Windows-only quality gate for MCE workflow, Skill and three references."""
from pathlib import Path
import subprocess
import sys
import re
import yaml

ROOT = Path(__file__).resolve().parents[3]
MCE = ROOT / "systems" / "mce"
WORKFLOWS = (
    "mce-github-memory.yml", "mce-independent-qa.yml",
    "mce-matriz-tool-qa.yml", "mce-memory-qa.yml", "mce-security-qa.yml",
)


def test_mce_workflows_never_run_linux():
    for workflow in WORKFLOWS:
        text = (ROOT / ".github" / "workflows" / workflow).read_text(encoding="utf-8")
        assert not re.search(r"ubuntu-latest|shell:\s*bash|runs-on:\s*.*linux", text, re.I), workflow
        jobs = yaml.safe_load(text)["jobs"]
        assert jobs
        for job in jobs.values():
            assert job["runs-on"] == "windows-latest", workflow
            assert job["defaults"]["run"]["shell"] == "pwsh", workflow


def test_runtime_guard_blocks_non_windows():
    script = (MCE / "scripts" / "matriz_causa_efeito_tool.py").read_text(encoding="utf-8")
    assert script.count("    _require_windows()") >= 2
    assert "WINDOWS_ONLY" in script


def test_skill_supports_three_repositories_and_windows_commands():
    path = MCE / ".agents" / "skills" / "matriz-causa-efeito"
    for text in ((path / "SKILL.md").read_text(encoding="utf-8"),
                 (path / "references" / "operacao-ferramenta.md").read_text(encoding="utf-8")):
        assert "Windows" in text and "PowerShell" in text
        assert "```powershell" in text and "```bash" not in text
    script = (MCE / "scripts" / "matriz_causa_efeito_tool.py").read_text(encoding="utf-8")
    for repo in ("Azure-Samples/digitization-of-piping-and-instrument-diagrams",
                 "S-Houston/digitised-pid-mlops", "ZzzJjt/Industrial-Control"):
        assert repo in script


def test_python_mirror_verification_runs_on_windows():
    p = subprocess.run([sys.executable, str(MCE / "scripts" / "verify_mce_skill_mirrors.py")],
                       capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stdout or p.stderr
    assert "MCE_SKILLS_SYNC=PASS" in p.stdout


def test_skill_package_generated_in_windows_ci():
    ci = (ROOT / ".github" / "workflows" / "mce-matriz-tool-qa.yml").read_text(encoding="utf-8")
    assert "Compress-Archive" in ci
    assert "actions/upload-artifact@v4" in ci
    assert "matriz-causa-efeito-windows-skill" in ci
