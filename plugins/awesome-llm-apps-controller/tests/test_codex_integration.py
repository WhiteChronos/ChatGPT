import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[3]


def test_marketplace_registers_controller():
    data=json.loads((ROOT/'.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
    plugin=next((p for p in data['plugins'] if p.get('name')=='awesome-llm-apps-controller'), None)
    assert plugin is not None
    assert plugin['source']=={'source':'local','path':'./plugins/awesome-llm-apps-controller'}
    assert plugin['policy']['installation']=='INSTALLED_BY_DEFAULT'
    assert plugin['policy']['products']==['CODEX']


def test_codex_config_enables_controller_and_preserves_existing_plugins():
    with (ROOT/'.codex/config.toml').open('rb') as f:
        cfg=tomllib.load(f)
    assert cfg['features']['multi_agent'] is True
    plugins=cfg['plugins']
    for name in [
        'github-arena@whitechronos-repo','superpowers@openai-curated',
        'superpowers-controller@whitechronos-repo','matt-pocock-controller@whitechronos-repo',
        'ecc@whitechronos-repo','ecc-controller@whitechronos-repo','subagent-broker@whitechronos-repo',
        'awesome-llm-apps-controller@whitechronos-repo',
    ]:
        assert plugins[name]['enabled'] is True


def test_agents_md_defines_awesome_layer_after_matt_and_before_github_arena():
    text=(ROOT/'AGENTS.md').read_text(encoding='utf-8')
    matt=text.index('## Matt Pocock complementary skills layer')
    awesome=text.index('## Awesome LLM Apps controlled example layer')
    assert matt < awesome
    assert 'Superpowers -> ECC -> Matt Pocock -> Awesome LLM Apps -> GitHub -> GitHub Arena' in text


def test_agents_md_forbids_auto_execution_of_gated_classes():
    text=(ROOT/'AGENTS.md').read_text(encoding='utf-8').lower()
    assert 'credentialled' in text
    assert 'background_autonomous' in text
    assert 'self_modifying' in text
    assert 'external_reference' in text
    assert 'never auto-run' in text or 'do not auto-run' in text
    assert 'native codex subagent' in text
