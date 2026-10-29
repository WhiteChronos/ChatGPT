from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_portable_plugin_identity_and_skills():
    plugin = json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8'))
    assert plugin['$schema'] == 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
    assert plugin['name'] == 'rea-independent'
    assert plugin['version']
    assert plugin['extensions']['com.openai']['interface']['capabilities'] == ['Read']
    assert plugin['extensions']['com.openai']['onboardingSkill'] == './skills/rea-setup/SKILL.md'
    for name in ('rea-setup','rea-operacao'):
        skill = ROOT / 'skills' / name / 'SKILL.md'
        assert skill.is_file()
        assert skill.read_text(encoding='utf-8').startswith('---\nname: ' + name + '\n')


def test_legacy_codex_overlay_has_no_unsafe_mcp_deployment():
    overlay = json.loads((ROOT / '.codex-plugin' / 'plugin.json').read_text(encoding='utf-8'))
    assert overlay['name'] == 'rea-independent'
    assert overlay['skills'] == './skills/'
    assert not (ROOT / 'mcp.json').exists()
    assert not (ROOT / '.mcp.json').exists()


def test_web_onboarding_stops_without_observed_tunnel():
    s = (ROOT / 'skills/rea-setup/SKILL.md').read_text(encoding='utf-8')
    assert 'tunnel-client doctor' in s
    assert 'tools/list' in s
    assert 'HOST_DISCOVERED' in s
    assert 'LIVE_VERIFIED' in s
    assert 'Desktop Commander' not in s
    assert 'PRODUCTION_COMPLETE=NO' in s


def test_read_only_engine_contract_preserved():
    s = (ROOT / 'skills/rea-operacao/SKILL.md').read_text(encoding='utf-8')
    assert 'read-only' in s
    assert 'MCE' in s
    assert 'rea_bridge_status' in s
    assert 'morluto/rea' in s
    assert 'never' in s.lower()
    engine = (ROOT/'src/sdk_server.py').read_text(encoding='utf-8')
    assert "SAFE_HOSTS = frozenset({'127.0.0.1', 'localhost', '::1'})" in engine
