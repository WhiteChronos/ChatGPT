#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "whitechronos-github-control-plane/v1"
REQUIRED_PROTECTED_REFS = (
    "~DEFAULT_BRANCH",
    "refs/heads/spec/**",
    "refs/heads/release/**",
)
REQUIRED_CHECK = "github-control-plane-policy"
FORBIDDEN_PHASE1_RULES = {
    "creation",
    "update",
    "required_signatures",
    "required_deployments",
}
DESIRED_PHASE1_RULES = {
    "deletion",
    "non_fast_forward",
    "required_linear_history",
    "pull_request",
    "required_status_checks",
}


def load_policy(path: Path) -> dict[str, object]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("policy must be a JSON object")
    return data


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def validate_policy(policy: dict[str, object]) -> list[str]:
    errors: list[str] = []

    if policy.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION}")

    ruleset = policy.get("ruleset")
    if not isinstance(ruleset, dict):
        errors.append("ruleset must be an object")
        ruleset = {}
    if ruleset.get("id") != 21770911:
        errors.append("ruleset.id must equal 21770911")
    if ruleset.get("name") != "Chronos":
        errors.append("ruleset.name must equal Chronos")
    if ruleset.get("target") != "branch":
        errors.append("ruleset.target must equal branch")
    if ruleset.get("enforcement") != "active":
        errors.append("ruleset.enforcement must equal active")

    protected_refs = policy.get("protected_refs")
    if not isinstance(protected_refs, list) or not protected_refs:
        errors.append("protected_refs must be a non-empty list")
        protected_refs = []
    elif not all(isinstance(item, str) for item in protected_refs):
        errors.append("protected_refs entries must be strings")
        protected_refs = []

    if "~ALL" in protected_refs:
        errors.append("~ALL is forbidden for phase-1 protected refs")
    for duplicate in sorted(_duplicates(protected_refs)):
        errors.append(f"duplicate protected ref: {duplicate}")
    for required in REQUIRED_PROTECTED_REFS:
        if required not in protected_refs:
            errors.append(f"protected_refs must include {required}")

    if policy.get("review_mode") != "solo":
        errors.append("review_mode must equal solo")

    pr = policy.get("pull_request")
    if not isinstance(pr, dict):
        errors.append("pull_request must be an object")
        pr = {}
    if pr.get("required_approving_review_count") != 0:
        errors.append("required_approving_review_count must equal 0 in solo mode")
    if pr.get("require_code_owner_review") is not False:
        errors.append("require_code_owner_review must be false in solo mode")
    if pr.get("require_last_push_approval") is not False:
        errors.append("require_last_push_approval must be false in solo mode")
    if pr.get("require_extra_approval_for_unattributed_changes") is not False:
        errors.append(
            "require_extra_approval_for_unattributed_changes must be false in solo mode"
        )
    if pr.get("required_review_thread_resolution") is not True:
        errors.append("required_review_thread_resolution must be true")
    if pr.get("dismiss_stale_reviews_on_push") is not False:
        errors.append("dismiss_stale_reviews_on_push must be false in solo mode")

    merge_methods = pr.get("allowed_merge_methods")
    if not isinstance(merge_methods, list) or not merge_methods:
        errors.append("allowed_merge_methods must be a non-empty list")
    else:
        if "merge" in merge_methods:
            errors.append("merge commit method is forbidden with linear history")
        invalid = sorted(set(merge_methods) - {"squash", "rebase"})
        if invalid:
            errors.append(f"invalid allowed_merge_methods: {invalid}")

    required_checks = policy.get("required_status_checks")
    if not isinstance(required_checks, list) or REQUIRED_CHECK not in required_checks:
        errors.append(f"required_status_checks must include {REQUIRED_CHECK}")

    desired_rules = policy.get("desired_rules")
    if not isinstance(desired_rules, list):
        errors.append("desired_rules must be a list")
        desired_rules = []
    forbidden_present = sorted(set(desired_rules) & FORBIDDEN_PHASE1_RULES)
    for rule in forbidden_present:
        errors.append(f"forbidden rule present in desired_rules: {rule}")
    missing_desired = sorted(DESIRED_PHASE1_RULES - set(desired_rules))
    if missing_desired:
        errors.append(f"desired_rules missing phase-1 rules: {missing_desired}")

    forbidden_rules = policy.get("forbidden_rules")
    if not isinstance(forbidden_rules, list):
        errors.append("forbidden_rules must be a list")
    elif set(forbidden_rules) != FORBIDDEN_PHASE1_RULES:
        errors.append("forbidden_rules must exactly match phase-1 deferred/forbidden rules")

    excluded_refs = policy.get("excluded_refs")
    if not isinstance(excluded_refs, list):
        errors.append("excluded_refs must be a list")

    bypass_actors = policy.get("bypass_actors")
    if not isinstance(bypass_actors, list):
        errors.append("bypass_actors must be a list")
    elif bypass_actors:
        errors.append("bypass_actors must be empty in phase 1")

    return errors


def _rule_map(ruleset: dict[str, object]) -> dict[str, dict[str, Any]]:
    rules = ruleset.get("rules")
    if not isinstance(rules, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in rules:
        if isinstance(item, dict) and isinstance(item.get("type"), str):
            result[item["type"]] = item
    return result


def _status_contexts(rule: dict[str, Any]) -> list[str]:
    parameters = rule.get("parameters")
    if not isinstance(parameters, dict):
        return []
    raw = parameters.get("required_status_checks")
    if not isinstance(raw, list):
        return []
    contexts: list[str] = []
    for item in raw:
        if isinstance(item, dict) and isinstance(item.get("context"), str):
            contexts.append(item["context"])
    return contexts


def verify_live_ruleset(
    policy: dict[str, object],
    ruleset: dict[str, object],
) -> list[str]:
    errors = validate_policy(policy)
    if errors:
        return [f"desired policy invalid: {error}" for error in errors]

    desired_ruleset = policy["ruleset"]
    assert isinstance(desired_ruleset, dict)

    for key in ("id", "name", "target", "enforcement"):
        expected = desired_ruleset.get(key)
        observed = ruleset.get(key)
        if observed != expected:
            errors.append(
                f"live ruleset {key} mismatch: expected {expected!r}, observed {observed!r}"
            )

    conditions = ruleset.get("conditions")
    ref_name = conditions.get("ref_name") if isinstance(conditions, dict) else None
    includes = ref_name.get("include") if isinstance(ref_name, dict) else None
    excludes = ref_name.get("exclude") if isinstance(ref_name, dict) else None
    expected_includes = policy["protected_refs"]
    expected_excludes = policy["excluded_refs"]
    if includes != expected_includes:
        errors.append(
            f"live protected refs mismatch: expected {expected_includes!r}, observed {includes!r}"
        )
    if excludes != expected_excludes:
        errors.append(
            f"live excluded refs mismatch: expected {expected_excludes!r}, observed {excludes!r}"
        )

    if ruleset.get("bypass_actors") != policy["bypass_actors"]:
        errors.append("live bypass actors do not match desired empty phase-1 list")

    rule_map = _rule_map(ruleset)
    observed_rule_types = set(rule_map)
    expected_rule_types = set(policy["desired_rules"])
    missing = sorted(expected_rule_types - observed_rule_types)
    extra = sorted(observed_rule_types - expected_rule_types)
    if missing:
        errors.append(f"live ruleset missing desired rules: {missing}")
    for rule in extra:
        if rule in FORBIDDEN_PHASE1_RULES:
            errors.append(f"live ruleset contains forbidden/deferred rule: {rule}")
        else:
            errors.append(f"live ruleset contains unexpected rule: {rule}")

    pr_rule = rule_map.get("pull_request", {})
    pr_parameters = pr_rule.get("parameters")
    if not isinstance(pr_parameters, dict):
        pr_parameters = {}
    desired_pr = policy["pull_request"]
    assert isinstance(desired_pr, dict)
    for key, expected in desired_pr.items():
        observed = pr_parameters.get(key)
        if observed != expected:
            errors.append(
                f"live pull_request parameter {key} mismatch: "
                f"expected {expected!r}, observed {observed!r}"
            )

    status_rule = rule_map.get("required_status_checks", {})
    status_parameters = status_rule.get("parameters")
    if not isinstance(status_parameters, dict):
        status_parameters = {}
    if status_parameters.get("strict_required_status_checks_policy") is not True:
        errors.append("live required status checks must use strict policy")
    if status_parameters.get("do_not_enforce_on_create") is not True:
        errors.append("live required status checks must not enforce on create")

    observed_contexts = _status_contexts(status_rule)
    expected_contexts = policy["required_status_checks"]
    if observed_contexts != expected_contexts:
        errors.append(
            f"live required status checks mismatch: "
            f"expected {expected_contexts!r}, observed {observed_contexts!r}"
        )

    return errors


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--ruleset-json", type=Path)
    parser.add_argument("--require-live", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        policy = load_policy(args.policy)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"GITHUB_CONTROL_PLANE_POLICY=FAIL")
        print(f"ERROR: {exc}")
        return 1

    errors = validate_policy(policy)

    if args.require_live and args.ruleset_json is None:
        errors.append("--require-live requires --ruleset-json")

    if args.ruleset_json is not None:
        try:
            ruleset = json.loads(args.ruleset_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot load live ruleset JSON: {exc}")
        else:
            if not isinstance(ruleset, dict):
                errors.append("live ruleset JSON must be an object")
            else:
                errors.extend(verify_live_ruleset(policy, ruleset))

    if errors:
        print("GITHUB_CONTROL_PLANE_POLICY=FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("GITHUB_CONTROL_PLANE_POLICY=PASS")
    if args.ruleset_json is not None:
        print("CHRONOS_ENFORCEMENT=ACTIVE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
