# PR #78 — Trusted GitHub Neutral Mirror: corrective review gate

**Scope:** Reconcile PR #78 with GitHub main after PR #76 and address five P1
and two P2 review findings. **No authorization** for merge, secrets, live
mirror, deployment, canary, stable, R2/R3 or production completion.

## Source and verification evidence

- Original PR head: \`a181697174caff0420c809323f430ad617d5c666\`
- Reviewed main baseline: \`c02f697fba858f64b7432b7b078d3a40192d754c\`
- In-branch integration commit (two parents, no force push):
  \`01178b488e26b980f72a233dfe363548541500d3\`
- Initial regression/RED test commit: \`4b7d3e4d53acabc39eb8d8d220017b3e7efb7873\`.
  The initial CI suite was blocked by an inherited outdated test call before
  all new RED assertions could be evaluated. Do not report seven separately
  verified failing RED tests.
- Verified green CI example: \`12d1cb31e97b0021fb8a9bd5672b3688dd0e5888\`:
  Runtime Foundation 123 passed, full repository 305 passed (five regex
  warnings subsequently repaired), awesome integration 3 passed, engineering
  governance 39 passed, Protocol Zero 4 passed. Five GitHub workflows were
  successful at that exact commit.
- Revalidate **again on the last HEAD** after all changes. Historical success
  does not establish success for another SHA.

## Finding matrix

| Finding | Code-level action | Status / acceptance boundary |
| --- | --- | --- |
| P1 subject-owned CI | Runbook and approved design require protected external GitLab CI config | **BLOCKED** until GitLab \`ci_config_path\` is explicitly configured and verified |
| P1 mutable installs | Removed runtime \`pip install\` from secret-bearing GH runner; dependency probe fails closed | Code changed; reviewed hermetic runner/dependency provenance needed before activation |
| P1 forged worker revision | Detached HMAC-SHA256 receipt proof and independent GitLab verifier; key never in push argv | Code/test prepared, but no signing key provisioned; protected CI prerequisite |
| P1 obsolete reruns | Exact-SHA GitHub Environment, rerun rejection, main-head check, mandatory external retirement | Code/test prepared; old Environment secrets must be revoked separately |
| P1 retained v1 evidence | v1 hashes/schema preserved; explicit v2 worker binding | Regression test added and CI tested |
| P2 recovery CLI | Documented \`--worker-revision "$(git rev-parse --verify HEAD)"\` | Regression test added and CI tested |
| P2 uppercase worker SHA | Lowercase canonicalization before provenance digest | Regression test added and CI tested |

## TinyFish and connected GitLab evidence

- TinyFish read the GitLab official CI configuration documentation and GitHub
  official rerun documentation in a **read-only** observer role.
- GitLab project \`chronoswhite-group/ChronosWhite-project\` (ID \`86465539\`)
  returned **empty** \`ci_config_path\`.
- Its five most recently listed pipelines were API-triggered, not eligible
  \`source=push\` parity evidence.
- No GitLab setting, token, branch, repository file, or pipeline was mutated.
- GitLab operator setup requires a separately protected independent CI config
  in a different protected project; subject-owned \`include:\` is not enough.

## Superpowers execution boundary

Official Superpowers was **not independently invoked** in this ChatGPT runtime;
the installed routing controller and task-by-task inline execution were used.
No native Codex subagent/worktree lifecycle was observed. Github feature branch
isolation, real CI, and SHA-bound commits provide the recorded execution
evidence; they do not pretend to be independent implementer/reviewer children.

## Full Arena — 16 sequential strategy perspectives

Adapter: \`plugins/github-arena/scripts/arena_review.py plan --agents 16\`
and \`cards --agents 16 --seed 78\`. Four reduction rounds
(\`16 -> 8 -> 4 -> 2 -> 1\`), **without isolated agents**.

1. Socratic / test-first / fewest parts: receipt proof cannot be a bare hash.
2. Dialectical / research / user focus: mirror success is not evidence authority.
3. Expert panel / minimal / speed: isolate credentialed runner from mutable installs.
4. Expert panel / outline / built-to-last: revision-scoped secret release and revocation.
5. Expert panel / restructure / completeness: preserve v1 historical verification.
6. Expert panel / options / clarity: provider setting changes require separate authority.
7. Analogy / research / edge cases: \`include:local\` cannot secure subject-owned YAML.
8. Contrarian / open questions / speed: malicious contributor can alter GitLab CI files.
9. Working backwards / explicit tradeoffs: exact SHA does not authenticate worker identity.
10. Probabilistic / outline / built-to-last: rotation and replay undermine shared environments.
11. Socratic / minimal / maximal rigor: missing HMAC key must block evidence, not downgrade.
12. Contrarian / iterative / speed: prior GitHub run SHA/ref persist on reruns.
13. Analogy / restructure / specificity: tests must not confuse GitHub CI with live mirror.
14. Working backwards / three drafts / built-to-last: protected external CI beats subject includes.
15. Decomposition / outline / maximal rigor: canonical v2 hash must preserve v1 digests.
16. Inversion / outline / fewest parts: GitLab must never gain merge/deploy authority.

**Winning safe architecture:** independent protected GitLab CI + authenticated
receipt + revision-scoped GitHub Environment + backward-compatible v2 evidence.
**Rejected:** hash-only claim, subject-controlled YAML, dynamic installs on
secret-bearing runner, permanent reusable Environment without revocation,
fabricated API-source parity, force push.

## Final disposition

Security and external-provider readiness: **BLOCKED / fail closed**.
TDD and GitHub CI may be marked PASS only for a tested exact HEAD.
PR merge is **not authorized**, no secret is provisioned, no live mirror or
deploy executed. Leave unresolved provider-authentication threads open where
their external enforcement has not been proven. STOP.
