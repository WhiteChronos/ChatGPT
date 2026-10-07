from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / '.gitlab-ci.yml'


def text():
    return PIPELINE.read_text(encoding='utf-8')


def test_pipeline_exists_and_parses():
    assert PIPELINE.exists()
    data = yaml.safe_load(text())
    assert isinstance(data, dict)


def test_required_jobs_and_stages_present():
    data = yaml.safe_load(text())
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
    assert 'pipeline/git_mirror_observation.py' in body
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


def test_non_push_pipeline_cannot_fabricate_fresh_mirror_receipt():
    body = PIPELINE.read_text(encoding='utf-8')
    assert 'CI_PIPELINE_SOURCE' in body
    assert '1970-01-01T00:00:00+00:00' in body
