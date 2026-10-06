from pathlib import Path
import json, tomllib
REPO=Path(__file__).resolve().parents[3]

def test_marketplace_registers_controller():
    data=json.loads((REPO/'.agents/plugins/marketplace.json').read_text())
    item=next(p for p in data['plugins'] if p['name']=='awesome-llm-apps-controller')
    assert item['source']=={'source':'local','path':'./plugins/awesome-llm-apps-controller'}
    assert item['policy']['installation']=='INSTALLED_BY_DEFAULT'
    assert item['policy']['products']==['CODEX']

def test_codex_config_enables_controller_and_preserves_existing_plugins():
    with open(REPO/'.codex/config.toml','rb') as f: cfg=tomllib.load(f)
    assert cfg['agents']['enabled'] is True
    assert cfg['features']['multi_agent'] is True
    for name in ['github-arena@whitechronos-repo','superpowers@openai-curated','superpowers-controller@whitechronos-repo','matt-pocock-controller@whitechronos-repo','ecc@whitechronos-repo','ecc-controller@whitechronos-repo','subagent-broker@whitechronos-repo','awesome-llm-apps-controller@whitechronos-repo']:
        assert cfg['plugins'][name]['enabled'] is True

def test_agents_md_defines_routing_and_execution_gates():
    text=(REPO/'AGENTS.md').read_text()
    assert 'Awesome LLM Apps' in text
    assert 'Superpowers -> ECC -> Matt Pocock -> Awesome LLM Apps -> GitHub -> GitHub Arena' in text
    for term in ['CREDENTIALLED','BACKGROUND_AUTONOMOUS','SELF_MODIFYING','external_reference']:
        assert term in text
    assert 'project-graveyard' in text and 'explicit' in text.lower()
