import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / 'plugins' / 'awesome-llm-apps-controller' / 'scripts'
sys.path.insert(0, str(SCRIPTS))

from awesome_llm_apps_skills import load_canonical_skills, project_skills, risk_for_skill


def _write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def _registry(root: Path, skills):
    _write(root / 'agent_skills' / 'registry.json', json.dumps({'version': 1, 'skills': skills}))


def test_valid_registry_skill_projects_byte_for_byte(tmp_path):
    upstream = tmp_path / 'upstream'
    _registry(upstream, [{'name':'commit-archaeologist','path':'agent_skills/commit-archaeologist','license':'Apache-2.0'}])
    content='---\nname: commit-archaeologist\n---\nbody\n'
    _write(upstream / 'agent_skills' / 'commit-archaeologist' / 'SKILL.md', content)
    _write(upstream / 'agent_skills' / 'commit-archaeologist' / 'helper.txt', 'helper\n')
    dest=tmp_path / 'skills'
    manifest=project_skills(upstream,dest,None,None)
    assert (dest/'commit-archaeologist'/'SKILL.md').read_text() == content
    assert (dest/'commit-archaeologist'/'helper.txt').read_text() == 'helper\n'
    assert manifest['skills'][0]['name'] == 'commit-archaeologist'


def test_registry_missing_skill_file_is_inconsistency_and_not_installed(tmp_path):
    upstream=tmp_path/'upstream'
    _registry(upstream,[{'name':'dependency-doctor','path':'agent_skills/dependency-doctor','license':'Apache-2.0'}])
    dest=tmp_path/'skills'
    manifest=project_skills(upstream,dest,None,None)
    assert not (dest/'dependency-doctor').exists()
    assert any(x['name']=='dependency-doctor' and x['reason']=='missing_skill_md' for x in manifest['inconsistencies'])


def test_registry_license_inconsistency_is_recorded_without_rewrite(tmp_path):
    upstream=tmp_path/'upstream'
    _registry(upstream,[{'name':'first-reader','path':'agent_skills/first-reader','license':''}])
    _write(upstream/'agent_skills'/'first-reader'/'SKILL.md','---\nname: first-reader\n---\n')
    loaded=load_canonical_skills(upstream)
    assert loaded[0]['license'] == ''
    assert 'invalid_registry_license' in loaded[0]['inconsistencies']
    manifest=project_skills(upstream,tmp_path/'skills',None,None)
    assert any(x['name']=='first-reader' and x['reason']=='invalid_registry_license' for x in manifest['inconsistencies'])


def test_non_registry_internal_skill_is_not_projected(tmp_path):
    upstream=tmp_path/'upstream'
    _registry(upstream,[])
    _write(upstream/'generative_ui_agents'/'demo'/'skills'/'local'/'SKILL.md','---\nname: local\n---\n')
    dest=tmp_path/'skills'
    manifest=project_skills(upstream,dest,None,None)
    assert manifest['skills'] == []
    assert not any(p.is_dir() for p in dest.iterdir())
    assert (dest/'.awesome-llm-apps-managed.json').is_file()


def test_unmanaged_destination_collision_fails(tmp_path):
    upstream=tmp_path/'upstream'
    _registry(upstream,[{'name':'scope-creep-detector','path':'agent_skills/scope-creep-detector','license':'Apache-2.0'}])
    _write(upstream/'agent_skills'/'scope-creep-detector'/'SKILL.md','new')
    dest=tmp_path/'skills'
    _write(dest/'scope-creep-detector'/'SKILL.md','local')
    with pytest.raises(RuntimeError, match='unmanaged.*scope-creep-detector'):
        project_skills(upstream,dest,None,None)


def test_matt_owned_destination_collision_fails_with_controller_name(tmp_path):
    upstream=tmp_path/'upstream'
    _registry(upstream,[{'name':'thinking-out-loud','path':'agent_skills/thinking-out-loud','license':'Apache-2.0'}])
    _write(upstream/'agent_skills'/'thinking-out-loud'/'SKILL.md','new')
    matt={'skills':['thinking-out-loud']}
    with pytest.raises(RuntimeError, match='Matt Pocock.*thinking-out-loud'):
        project_skills(upstream,tmp_path/'skills',None,matt)


def test_previously_awesome_managed_skill_can_be_replaced_and_stale_removed(tmp_path):
    upstream=tmp_path/'upstream'
    _registry(upstream,[{'name':'commit-archaeologist','path':'agent_skills/commit-archaeologist','license':'Apache-2.0'}])
    _write(upstream/'agent_skills'/'commit-archaeologist'/'SKILL.md','new')
    dest=tmp_path/'skills'
    _write(dest/'commit-archaeologist'/'SKILL.md','old')
    _write(dest/'stale-awesome'/'SKILL.md','old stale')
    previous={'skills':[{'name':'commit-archaeologist'},{'name':'stale-awesome'}]}
    manifest=project_skills(upstream,dest,previous,None)
    assert (dest/'commit-archaeologist'/'SKILL.md').read_text() == 'new'
    assert not (dest/'stale-awesome').exists()
    assert [s['name'] for s in manifest['skills']] == ['commit-archaeologist']


def test_risk_metadata_for_all_seven_canonical_skills_matches_spec():
    expected={
      'advisor-orchestrator-worker':('CREDENTIALLED',True,True,False),
      'commit-archaeologist':('LOCAL_READ_ONLY',False,False,False),
      'dependency-doctor':('LOCAL_READ_ONLY',False,False,False),
      'first-reader':('REFERENCE_ONLY',False,False,False),
      'project-graveyard':('LOCAL_READ_ONLY',False,True,True),
      'scope-creep-detector':('LOCAL_READ_ONLY',False,False,False),
      'thinking-out-loud':('REFERENCE_ONLY',False,False,False),
    }
    for name,(klass,credentials,explicit,broad) in expected.items():
        risk=risk_for_skill(name)
        assert risk['execution_class'] == klass
        assert risk['credentials_required'] is credentials
        assert risk['explicit_user_request_required'] is explicit
        assert risk['broad_filesystem_access'] is broad
