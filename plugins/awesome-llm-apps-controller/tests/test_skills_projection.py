from pathlib import Path
import json, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from awesome_llm_apps_skills import load_canonical_skills, risk_for_skill, project_skills
FIXTURE=Path(__file__).resolve().parent/'fixtures'/'upstream'

def test_registry_validation_and_projection(tmp_path):
    loaded=load_canonical_skills(FIXTURE)
    assert [x['name'] for x in loaded['skills']] == ['skill-a']
    assert any(i['name']=='missing-skill' and i['kind']=='missing_skill_md' for i in loaded['inconsistencies'])
    dest=tmp_path/'skills'; dest.mkdir()
    manifest=project_skills(FIXTURE,dest,None,None)
    assert (dest/'skill-a'/'SKILL.md').exists()
    assert not (dest/'internal-app').exists()
    assert manifest['managed_skills'][0]['name']=='skill-a'

def test_collision_with_unmanaged_destination_fails(tmp_path):
    dest=tmp_path/'skills'; (dest/'skill-a').mkdir(parents=True); (dest/'skill-a'/'x').write_text('x')
    try:
        project_skills(FIXTURE,dest,None,None)
    except RuntimeError as e:
        assert 'collision' in str(e).lower()
    else:
        raise AssertionError('expected collision')

def test_known_skill_risk_metadata():
    assert risk_for_skill('project-graveyard')['explicit_user_request_required'] is True
    assert risk_for_skill('advisor-orchestrator-worker')['credentials_required'] is True
