# Gate: independent trusted GitLab CI (secretless preparation)

## Scope and authority

GitHub `WhiteChronos/ChatGPT` remains the sole merge authority. GitLab
`chronoswhite-group/ChronosWhite-project` (86465539) is a non-authoritative
mirror/evidence plane. This gate does **not** authorize creating, storing or
retrieving credentials, pushing a mirror ref, running a live pipeline, merging,
deploying, or claiming production readiness.

## Required separation and provider configuration

The verified GitLab project currently has an empty `ci_config_path`. The
existing protected `bootstrap/mirror-controller` branch **inside the mirror**
cannot serve as the independent CI trust boundary. Create/select a **distinct**
GitLab project controlled by trusted CI maintainers, restrict writes and force
pushes, protect the exact review ref, and independently obtain its Git SHA.

GitLab supports a CI config path in a separate project, such as:

```text
ci/trusted-mirror.yml@chronoswhite-group/trusted-ci-verifier:main
```

This path is a **design example, not an existing or configured project**.
The external project must contain the audited job definition and verifier code
with immutable integrity provenance. A protected YAML by itself is insufficient
when it imports modules from the mirrored subject checkout.

**Manual/provider setup gate:** GitLab project `86465539` → Settings →
CI/CD → General pipelines → CI/CD configuration file → select the external
project path. Then read back `ci_config_path` using the authenticated GitLab
Projects API and verify the protected verifier project/ref's permissions and
exact SHA. Do not change the setting until the independent project and access
controls are proven. No such setting change occurred in this gate.

## Template and Python contract

- `docs/gitlab-trusted-ci/trusted-mirror.yml`: fail-closed preflight template,
  `GIT_STRATEGY: none`, no subject checkout or package installations. The
  template **intentionally exits BLOCKED**, since actual verifier bootstrap,
  code integrity, and signing keys are not provisioned.
- `pipeline/trusted_gitlab_ci_gate.py`: Python stdlib-only, side-effect-free
  configuration checks and synthetic authenticated-receipt validation. It
  rejects subject-controlled CI config, missing/unprotected external refs,
  forged worker revision, inconsistent exact SHA, unsigned receipts, API-run
  pseudo-evidence, invalid job identity, bad timestamps and untrusted fields.
- `tests/test_trusted_gitlab_ci_gate.py`: synthetic TDD security tests.
- `.github/workflows/trusted-gitlab-ci-preflight.yml`: secretless CI smoke on
  the dedicated feature branch; **not a live GitLab CI verification**.

`GateState.PREPARED` means a provider snapshot meets preliminary isolation
rules. `GateState.ATTESTED` is only returned by an individual cryptographic
helper given trusted inputs; it is **not evidence of an actual provider run**
and does not grant merge/deploy authority.

## Additional mandatory approval and tests

Before any future live GitLab evidence: independent trusted verifier code
must execute from pinned external code rather than the mirrored subject;
validate authenticated GitLab job identity via `CI_JOB_TOKEN` endpoint,
trusted config SHA and observed provider ref; prevent untrusted input
interpolation into shell or Python execution; prove key exposure boundaries,
worker allowlisting, revocation/replay controls, and same-SHA provenance; and
complete independent security and operation reviews. Separate approval will
be required for any secret provisioning, live mirror, merge or deployment.

## Read-only observed facts / STOP

- GitLab project ID: `86465539`
- Project `ci_config_path`: empty, external CI NOT established.
- Existing mirror default branch: `bootstrap/mirror-controller`
- Independent protected verifier project: NOT_VERIFIED.
- Signer key and target write credential: no provision/change in this gate,
  pre-existing secret state NOT_VERIFIABLE.
- Real GitLab push-sourced evidence: NOT_VERIFIED.
- `TRUSTED_GITLAB_VERIFIER=NO`, `LIVE_MIRROR_BOUND=NO`,
  `PRODUCTION_COMPLETE=NO`.

### References

- GitLab official [Customize pipeline configuration](https://docs.gitlab.com/ci/pipelines/settings/)
- GitLab official [GitLab CI/CD YAML syntax](https://docs.gitlab.com/ci/yaml/)
- GitHub official [Re-running workflows and jobs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
