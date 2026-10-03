from pathlib import Path
import re
import yaml

ROOT=Path(__file__).resolve().parents[3]
WORKFLOW=ROOT/'.github/workflows/sync-awesome-llm-apps.yml'


def _load():
    return yaml.load(WORKFLOW.read_text(encoding='utf-8'), Loader=yaml.BaseLoader)


def test_workflow_has_manual_daily_and_relevant_push_triggers():
    data=_load()
    triggers=data['on']
    assert 'workflow_dispatch' in triggers
    assert triggers['schedule'] and triggers['schedule'][0]['cron']
    paths=triggers['push']['paths']
    assert '.github/workflows/sync-awesome-llm-apps.yml' in paths
    assert 'plugins/awesome-llm-apps-controller/**' in paths


def test_workflow_permissions_allow_review_branch_and_pr():
    data=_load()
    assert data['permissions']=={'contents':'write','pull-requests':'write'}


def test_workflow_tests_sync_before_real_upstream_synchronization():
    data=_load()
    steps=data['jobs']['sync']['steps']
    names=[s.get('name','') for s in steps]
    test_i=next(i for i,n in enumerate(names) if 'Test synchronization behavior' in n)
    sync_i=next(i for i,n in enumerate(names) if 'Synchronize Awesome LLM Apps upstream' in n)
    assert test_i < sync_i
    assert 'test_sync_mirror.sh' in steps[test_i]['run']
    assert 'sync_mirror.sh' in steps[sync_i]['run']


def test_workflow_stages_only_generated_owned_paths():
    text=WORKFLOW.read_text(encoding='utf-8')
    assert 'git add vendor/shubhamsaboo-awesome-llm-apps registry/awesome-llm-apps' in text
    assert 'plugins/awesome-llm-apps-controller/upstream.lock.json' in text
    assert '.agents/skills/.awesome-llm-apps-managed.json' in text
    assert 'MANAGED_SKILLS' in text
    assert 'git add .agents/skills' not in text.replace('git add .agents/skills/.awesome-llm-apps-managed.json','')
    assert 'for skill in "${MANAGED_SKILLS[@]}"; do' in text


def test_pr_creation_policy_failure_warns_without_failing_job():
    text=WORKFLOW.read_text(encoding='utf-8')
    assert 'if PR_URL="$(gh pr create' in text
    assert '::warning::' in text
    failure_block=text.split('if PR_URL="$(gh pr create',1)[1]
    assert 'exit 1' not in failure_block
    assert 'GITHUB_STEP_SUMMARY' in failure_block
