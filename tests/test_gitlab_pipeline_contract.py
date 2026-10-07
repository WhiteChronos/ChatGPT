from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / '.gitlab-ci.yml'
RUNBOOK = ROOT / 'docs' / 'runbooks' / 'gitlab-contingency-ci.md'
REVIEW = ROOT / 'docs' / 'superpowers' / 'reviews' / '2026-10-05-whitechronos-gitlab-contingency-ci-review.md'


def text():
    return PIPELINE.read_text(encoding='utf-8')


def pipeline_data():
    merged = {}
    for document in yaml.safe_load_all(text()):
        if isinstance(document, dict):
            merged.update(document)
    return merged


def test_pipeline_exists_and_parses():
    assert PIPELINE.exists()
    data = pipeline_data()
    assert isinstance(data, dict)


def test_required_jobs_and_stages_present():
    data = pipeline_data()
    assert data['stages'] == ['parity', 'validate', 'evidence']
    for job in ('mirror-parity', 'python-governance', 'broker', 'contingency-evidence'):
        assert job in data


def test_pipeline_contains_no_authority_or_deployment_actions():
    lowered = text().lower()
    forbidden = [
        'environment:',
        'git push --force',
        'git merge ',
        'kubectl ',
        'helm ',
        'deploy',
        'canary',
        'stable promotion',
        'live smoke',
        'production_complete',
    ]
    for token in forbidden:
        assert token not in lowered


def test_pipeline_uses_parity_and_contingency_modules_and_artifacts():
    body = text()
    assert 'from pipeline.git_mirror_observation import observe_remote_ref' in body
    assert 'pipeline/git_mirror_parity.py' in body
    assert 'pipeline/contingency_ci_gate.py' in body
    for artifact in ('mirror-parity.json', 'contingency-gate.json', 'ci-provider-evidence.json'):
        assert artifact in body


def test_custom_variables_are_bounded_and_non_secret():
    body = text()
    variables = set(re.findall(r'\$([A-Z][A-Z0-9_]*)', body))
    custom = {name for name in variables if not name.startswith('CI_')}
    assert custom <= {
        'WHITECHRONOS_GITHUB_REMOTE',
        'WHITECHRONOS_SOURCE_REPOSITORY',
        'WHITECHRONOS_GITLAB_PROJECT_ID',
        'WHITECHRONOS_GITLAB_PROJECT_PATH',
    }
    assert all(word not in body.upper() for word in ('PASSWORD=', 'TOKEN=', 'SECRET='))


def test_all_container_images_are_digest_pinned():
    image_lines = [line.strip() for line in text().splitlines() if line.strip().startswith('image:')]
    assert image_lines
    assert all('@sha256:' in line for line in image_lines)


def test_broker_job_installs_git_for_repository_tests():
    body = PIPELINE.read_text(encoding='utf-8')
    broker_block = body.split('\nbroker:\n', 1)[1].split('\ncontingency-evidence:\n', 1)[0]
    assert 'apt-get install -y --no-install-recommends git' in broker_block


def test_freshness_requires_live_dual_provider_ref_observation():
    body = PIPELINE.read_text(encoding='utf-8')
    mirror_block = body.split('mirror-parity:', 1)[1].split('\npython-governance:', 1)[0]
    assert 'observe_remote_ref(' in mirror_block
    assert 'gitlab_remote_sha' in mirror_block
    assert '"gitlab_sha": gitlab_remote_sha' in mirror_block
    assert '"receipt_timestamp": receipt["timestamp"]' in mirror_block
    assert '"observed_at": observed_at' in mirror_block
    assert 'job_source != "push"' in mirror_block
    assert '1970-01-01T00:00:00+00:00' not in mirror_block

def test_python_governance_job_installs_git_for_root_regression():
    body = text()
    block = body.split('\npython-governance:\n', 1)[1].split('\nbroker:\n', 1)[0]
    assert 'apt-get install -y --no-install-recommends git' in block


def test_pipeline_binds_observed_gitlab_project_identity():
    body = text()
    assert 'git remote get-url origin' in body
    assert 'urlsplit' in body
    assert 'governance/GITLAB_CONTINGENCY_CI_POLICY.json' in body
    assert 'observed_project_path != expected_project_path' in body
    assert '"gitlab_project_path": observed_project_path' in body
    assert '"repository_identity": runtime_identity["gitlab_project_path"]' in body
    assert 'os.environ["CI_PROJECT_PATH"]' not in body
    assert 'os.environ["CI_PROJECT_ID"]' not in body


def test_pipeline_canonical_github_remote_is_not_user_overridable():
    body = text()
    assert 'observe_remote_ref(' in body
    assert '"https://github.com/WhiteChronos/ChatGPT.git"' in body
    assert '$WHITECHRONOS_GITHUB_REMOTE' not in body


def test_gate_failures_propagate_to_pipeline_status():
    body = text()
    assert 'then true; else true' not in body
    assert body.count('exit "$status"') >= 2
    assert 'exit 1' in body


def test_pipeline_emits_provenance_sha256():
    assert 'provenance_sha256' in text()


def test_runbook_protects_every_mirror_ref_class():
    body = RUNBOOK.read_text(encoding='utf-8')
    for pattern in ('main', 'spec/*', 'plan/*', 'feat/*', 'fix/*', 'release/*'):
        assert pattern in body
    assert 'transport-only write' in body.lower()


def test_review_records_external_workflow_run_provenance():
    body = REVIEW.read_text(encoding='utf-8')
    assert '| Run ID |' in body
    assert 'https://github.com/WhiteChronos/ChatGPT/actions/runs/' in body

def test_ineligible_evidence_fails_final_job():
    body = text()
    evidence_block = body.split('\ncontingency-evidence:\n', 1)[1]
    assert 'evidence_eligible' in evidence_block
    assert 'not gate.get("evidence_eligible")' in evidence_block

def test_pipeline_uses_job_token_identity_endpoint():
    body = text()
    assert 'https://gitlab.com/api/v4/job' in body
    assert 'JOB-TOKEN' in body
    assert 'pipeline.get("project_id"' in body
    assert 'commit.get("id"' in body
    assert 'gitlab-runtime-identity.json' in body

def test_gitlab_ref_probe_uses_remote_name_not_credential_bearing_url():
    body = text()
    mirror_block = body.split('mirror-parity:', 1)[1].split('\npython-governance:', 1)[0]
    assert '["git", "ls-remote", "--exit-code", "origin", full_ref]' in mirror_block
    assert '["git", "ls-remote", "--exit-code", origin_url, full_ref]' not in mirror_block

def test_pipeline_uses_bounded_infrastructure_retry_policy():
    data = pipeline_data()
    retry = data['default']['retry']
    assert retry['max'] == 1
    assert set(retry['when']) == {'api_failure', 'runner_system_failure', 'scheduler_failure'}


def test_broker_clears_node_control_environment():
    body = text()
    broker_block = body.split('\nbroker:\n', 1)[1].split('\ncontingency-evidence:\n', 1)[0]
    assert 'unset NODE_OPTIONS' in broker_block
    assert 'unset NODE_PATH' in broker_block


def test_pipeline_requires_neutral_worker_receipt_contract():
    body = text()
    mirror_block = body.split('mirror-parity:', 1)[1].split('\npython-governance:', 1)[0]
    for name in (
        'WHITECHRONOS_MIRROR_TRANSPORT',
        'WHITECHRONOS_MIRROR_SOURCE_REPOSITORY',
        'WHITECHRONOS_MIRROR_TARGET_PROJECT',
        'WHITECHRONOS_MIRROR_REF',
        'WHITECHRONOS_MIRROR_SOURCE_SHA',
        'WHITECHRONOS_MIRROR_TARGET_SHA',
        'WHITECHRONOS_MIRROR_TIMESTAMP',
        'WHITECHRONOS_MIRROR_RECEIPT_SHA256',
    ):
        assert name in mirror_block
    assert 'job_source != "push"' in mirror_block
    assert '"receipt_timestamp": receipt["timestamp"]' in mirror_block
    assert 'mirror receipt digest mismatch' in mirror_block

def test_pipeline_only_accepts_neutral_worker_push_trigger():
    data = pipeline_data()
    rules = data['workflow']['rules']
    assert rules == [
        {'if': '$CI_PIPELINE_SOURCE == "push"'},
        {'when': 'never'},
    ]

def test_pipeline_declares_typed_mirror_receipt_inputs():
    data = pipeline_data()
    inputs = data['spec']['inputs']
    assert set(inputs) == {
        'mirror_transport',
        'mirror_source_repository',
        'mirror_target_project',
        'mirror_ref',
        'mirror_source_sha',
        'mirror_target_sha',
        'mirror_timestamp',
        'mirror_receipt_sha256',
    }
    assert inputs['mirror_transport']['options'] == ['neutral_worker']
    assert inputs['mirror_source_sha']['regex'] == '^[0-9a-fA-F]{40}$'
    assert inputs['mirror_target_sha']['regex'] == '^[0-9a-fA-F]{40}$'
    assert inputs['mirror_receipt_sha256']['regex'] == '^[0-9a-fA-F]{64}$'
    body = text()
    assert '$[[ inputs.mirror_transport ]]' in body
    assert '$[[ inputs.mirror_receipt_sha256 ]]' in body
