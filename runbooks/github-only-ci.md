# WhiteChronos — GitHub-only CI mode

## Status

**Proposed on feature branch; not merged or deployed.**

WhiteChronos runs CI, policy validation, code reviews and release gating
exclusively through GitHub. GitLab contingency mirroring is retired from
the *active* provider policy because the independently protected CI configuration
and external trusted execution could not be verified.

## Canonical mode

- GitHub repository: `WhiteChronos/ChatGPT`, sole source/merge authority.
- GitHub control-plane ruleset: `governance/GITHUB_CONTROL_PLANE_POLICY.json`.
- GitHub required check: `github-control-plane-policy`.
- GitLab policy: `governance/GITLAB_CONTINGENCY_CI_POLICY.json`, `provisioning_state: DISABLED`.
- No GitLab mirror project, ref or transport is provisioned *in the active configuration*.
  This is a logical retirement **not deletion of existing GitLab projects**.
- Allowed evidence providers in active contingency policy: `github`, `local`.
- `sync_gitlab_mirror.py` rejects any network source/target while disabled,
  before Git subprocesses or any credential helper activity. Purely local test
  fixtures remain available for historical regression only.

## How to validate

```bash
python -m pytest -q tests/test_github_only_mode.py
python -m pytest -q tests/test_gitlab_contingency_policy.py
python -m pytest -q plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py
python -m pytest -q
python pipeline/github_control_plane_policy_gate.py --policy governance/GITHUB_CONTROL_PLANE_POLICY.json
```

The GitHub Actions `WhiteChronos Runtime Foundation`, `Engineering Governance`
and `GitHub Control Plane Policy` remain the active CI surfaces where triggered.
The historical `.gitlab-ci.yml` and previous runbooks are retained as
source-controlled evidence; they are **not** required GitHub release checks.

## Boundaries and STOP

- Do not merge or deploy until the required GitHub checks and ordinary
  repository review/ruleset gates pass and explicit authorization is given.
- Do not infer Codex host discovery, independent subagents, live smoke or
  `PRODUCTION_COMPLETE` from green GitHub CI; these require their own evidence.
- GitLab projects `86465539` and `87364758` are *not deleted, modified or
  considered connected* by this GitHub-only change.
- Never provision/rotate GitLab secrets, run a live mirror or trigger GitLab
  pipelines to validate this mode.
- GitLab-related findings from historical PRs #78/#79 are **not resolved**; the
  corresponding feature remains retired/out of scope unless separately
  reauthorized and re-reviewed.

## Rollback

Revert this GitHub-only change via normal reviewed PR. Re-enabling a live
GitLab mirror is **not** achieved by rollback alone: it requires an independent
trusted CI source, strict permissions, authenticated provider evidence,
security review and separate authorization.
