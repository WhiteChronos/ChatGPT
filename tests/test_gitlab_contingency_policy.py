import json
from pathlib import Path

import jsonschema
import pytest

from pipeline.gitlab_contingency_policy import load_policy

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'governance' / 'GITLAB_CONTINGENCY_CI_POLICY.json'
SCHEMA = ROOT / 'schemas' / 'gitlab_contingency_ci.schema.json'


def test_policy_invariants():
    policy = json.loads(POLICY.read_text(encoding='utf-8'))
    assert policy['schema_version'] == 1
    assert policy['authority_provider'] == 'github'
    assert policy['mirror_direction'] == 'github_to_gitlab'
    assert policy['active_failover'] is False
    assert policy['gitlab_merge_authority'] is False
    assert policy['gitlab_deploy_authority'] is False
    assert policy['source_repository'] == 'WhiteChronos/ChatGPT'
    assert policy['evidence_requires_exact_sha'] is True
    assert policy['mirror_freshness_seconds'] == 3600
    assert policy['max_clock_skew_seconds'] == 300
    assert policy['provisioning_state'] == 'DISABLED'
    assert policy['gitlab_project_id'] is None
    assert policy['gitlab_project_path'] is None
    assert policy['mirror_transport'] is None
    assert policy['mirror_divergence_behavior'] == 'FAIL_CLOSED'
    assert policy['provider_disagreement_behavior'] == 'BLOCK_FOR_INVESTIGATION'
    assert policy['allowed_evidence_providers'] == ['github', 'local']
    assert policy['allowed_mirror_ref_classes'] == [
        'main', 'spec/*', 'plan/*', 'feat/*', 'fix/*', 'release/*'
    ]
    assert policy['infrastructure_retry']['limit'] == 2
    assert policy['infrastructure_retry']['eligible_failures'] == [
        'PROVIDER_INFRA_FAILURE', 'RUNNER_ASSIGNMENT_FAILURE'
    ]


def test_policy_validates_against_schema():
    policy = json.loads(POLICY.read_text(encoding='utf-8'))
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    jsonschema.validate(policy, schema)


def test_loader_rejects_unknown_keys(tmp_path):
    policy = json.loads(POLICY.read_text(encoding='utf-8'))
    policy['unexpected'] = True
    p = tmp_path / 'policy.json'
    p.write_text(json.dumps(policy), encoding='utf-8')
    with pytest.raises(ValueError):
        load_policy(p)


def test_loader_rejects_path_traversal(tmp_path):
    with pytest.raises(ValueError):
        load_policy(tmp_path / '..' / 'policy.json')

from dataclasses import replace
from pipeline.gitlab_contingency_policy import classify_ref


@pytest.mark.parametrize(
    ('ref_name', 'eligible'),
    [
        ('main', True),
        ('spec/example', True),
        ('plan/example', True),
        ('feat/example', True),
        ('fix/example', True),
        ('release/v1', True),
        ('refs/heads/fix/example', True),
        ('subagent/temp', False),
        ('refs/pull/1/merge', False),
        ('../main', False),
        ('', False),
        ('unknown/example', False),
    ],
)
def test_classify_ref(ref_name, eligible):
    # Historic ref-classification cases are explicitly simulated under the
    # former enabled state, never the active disabled repository policy.
    policy = replace(load_policy(POLICY), provisioning_state="PROVISIONED")
    decision = classify_ref(ref_name, policy)
    assert decision.eligible is eligible


def test_loader_rejects_authority_escalation(tmp_path):
    raw = json.loads(POLICY.read_text(encoding='utf-8'))
    raw['gitlab_merge_authority'] = True
    p = tmp_path / 'policy.json'
    p.write_text(json.dumps(raw), encoding='utf-8')
    with pytest.raises(ValueError):
        load_policy(p)
