# WhiteChronos — GitHub-only operations

## Authority and scope

GitHub repository `WhiteChronos/ChatGPT` is the sole source-code, issue-tracker,
CI and merge authority for WhiteChronos. Third-party CI mirroring has been
removed from the current first-party source tree. Historical implementation
and review evidence remain recoverable from Git history and past pull requests;
historical objects are **not** production services.

The active GitHub control-plane ruleset is tracked at
`governance/GITHUB_CONTROL_PLANE_POLICY.json`, and the required check runs in
`.github/workflows/github-control-plane-policy.yml`. Do not weaken the
ruleset, review-thread resolution, linear history or required status checks.

## Tests and verification

From the current checkout:

```bash
python -m pytest -q tests/test_github_only_mode.py
python -m pytest -q
python pipeline/github_control_plane_policy_gate.py --policy governance/GITHUB_CONTROL_PLANE_POLICY.json
```

The runtime, engineering and document-governance workflows remain available
under GitHub Actions. Successful CI verifies only the checked code and the
reported gates; it does not prove that an external Codex host discovered native
or broker subagents.

## Documentation publishing safety

`.github/workflows/deks-pages.yml` is **manual invocation only**.
No push to the default branch automatically launches Pages deployment. Manual
publication is a separate operation subject to explicit authorization,
independent from code merges and routine validations. Reintroducing automatic
publishing requires its own review and approval.

## Runtime separation and STOP

A real Codex host must run the Runtime Doctor against the exact current SHA and
its **observed** host tools before claiming independent-subagent discovery.
Do not forge host inventory from `.codex/config.toml` or CI tests.

These actions remain prohibited without distinct user authorization: deployment,
canary/stable promotion, live smoke, external mirror activation, provisioned
secrets or tokens, and `PRODUCTION_COMPLETE`.

## Reversibility

Restoring a retired provider integration requires a new specification,
security review, tests, and separate authorization. Never restore an external
service or credentials merely by reverting this source change.
