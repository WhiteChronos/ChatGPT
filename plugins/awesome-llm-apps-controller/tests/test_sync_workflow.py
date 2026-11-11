from pathlib import Path
import yaml

REPO=Path(__file__).resolve().parents[3]
WF=REPO/'.github/workflows/sync-awesome-llm-apps.yml'

def load():
    return yaml.load(WF.read_text(), Loader=yaml.BaseLoader)

def test_workflow_has_required_triggers_and_permissions():
    data=load()
    on=data['on']
    assert 'workflow_dispatch' in on
    assert 'schedule' in on and on['schedule']
    assert 'push' in on
    paths=on['push']['paths']
    assert '.github/workflows/sync-awesome-llm-apps.yml' in paths
    assert 'plugins/awesome-llm-apps-controller/**' in paths
    assert data['permissions']=={'contents':'write','pull-requests':'write'}

def test_tests_run_before_real_sync_and_staging_is_restricted():
    text=WF.read_text()
    assert text.index('Test synchronizer') < text.index('Synchronize upstream')
    assert 'git add -A -- vendor/shubhamsaboo-awesome-llm-apps/' in text
    assert 'git add -A -- registry/awesome-llm-apps/' in text
    assert 'git add -A -- .agents/skills/.awesome-llm-apps-managed.json' in text
    assert 'git add .agents/skills' not in text
    assert 'git add -A .agents/skills' not in text
    assert 'managed-skill-paths.txt' in text

def test_pr_creation_failure_is_nonfatal_after_branch_push():
    text=WF.read_text()
    assert 'gh pr create' in text
    assert '::warning::' in text
    assert 'PR creation was blocked' in text
    assert 'exit 0' in text
