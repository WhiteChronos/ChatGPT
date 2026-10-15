# Continuous Skill Improvement — governance v1

## Scope
GitHub is the versioned source of truth for proposed and approved WhiteChronos skills. The scheduler is an observation mechanism, not an autonomous self-modifying agent.

## Improvement loop
1. Collect reproducible issue evidence, reproduction steps, expected vs actual behavior and privacy-safe metrics.
2. Confirm whether the gap is in an existing skill, tool, host, prompt or upstream provider.
3. Prefer editing an existing skill; create a new skill only when its responsibility is genuinely distinct.
4. Prepare a feature branch and PR including a SKILL.md, UI metadata, tests, threat model, baseline and post-change comparison.
5. Run compatibility, security, repository policy and regression reviews. Fail closed for unknown results.
6. Human reviewer must approve the exact HEAD; never auto-merge or bypass required checks.
7. After authorized merge, install only in hosts supporting a separately authorized installation workflow. Merely committing a skill does not install it in ChatGPT.

## Current implementation
A daily GitHub Actions workflow runs a read-only, no-network skill metadata audit and attaches JSON findings. It neither creates new skills nor changes code, PRs, credentials, deployment or local installations.

The audit excludes upstream vendor trees, dependency environments and paths under
`tests/fixtures/`: these are synthetic test inputs, not installed skill entrypoints.
Other directories named `fixtures`, including an active skill with that name, are
still audited. Regression tests cover both cases so malformed active skills remain
blocking. This lightweight metadata check is not a full YAML or behavioral skill
evaluation, and a successful run does not demonstrate improved model reasoning.

## Next gates
- Confirm current main SHA and action pin allowlist at PR HEAD.
- Add evaluated before/after task datasets and duplicate-skill detection.
- Design a PR proposal generator with restricted token permissions and manual approval.
- Review real Codex host tool inventory; do not infer availability from config files.
- Record failed audits without including sensitive task inputs, keys or logs.

## Security
No self-approval, auto-merge, token provisioning, paid inference, live smoke, deployment or PRODUCTION_COMPLETE. Preserve the GitHub-only ruleset and mandatory checks.
