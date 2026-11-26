"""Self-contained adversarial tests for SHA-bound read-only evidence inventory."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "rea_mce_review_inventory.py"
SPEC = importlib.util.spec_from_file_location("rea_mce_review_inventory", SCRIPT)
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)

HEAD = "a" * 40


def fixture(product=118, valid=True, state="open", draft=False, approvals=()):
    _, required = REVIEW.TARGETS[product]
    results = {
        "head": {"sha": HEAD}, "state": state, "draft": draft, "user": {"login": "author"},
    }
    checks = [{"name": name, "head_sha": HEAD, "status": "completed",
               "conclusion": "success"} for name in required]
    if not valid:
        checks[0]["conclusion"] = "failure"
    reviews = [{"state": "APPROVED", "commit_id": sha, "user": {"login": who}}
               for who, sha in approvals]

    def fetch(path):
        if path.endswith("/pulls/" + str(product)):
            return results
        if path.endswith("/check-runs?per_page=100"):
            return {"total_count": len(checks), "check_runs": checks}
        if path.endswith("/reviews?per_page=100"):
            return reviews
        raise AssertionError("Unexpected path " + path)
    return fetch, checks, results


class ReviewInventoryTests(unittest.TestCase):
    def test_both_products_are_current_sha_pass_not_production(self):
        for number in (118, 119):
            with self.subTest(number=number):
                fetch, _, _ = fixture(number)
                row = REVIEW.inspect_one(fetch, number)
                self.assertEqual(row["code_ci"], "PASS")
                self.assertEqual(row["review"], "PENDING")
                self.assertFalse(row["merge_authorized"])
                self.assertFalse(row["production_complete"])
                self.assertEqual(row["host_live"], "NOT_VERIFIED")

    def test_failing_or_missing_check_blocks(self):
        fetch, _, _ = fixture(valid=False)
        self.assertEqual(REVIEW.inspect_one(fetch, 118)["code_ci"], "BLOCKED")
        fetch, checks, _ = fixture()
        checks.pop()
        self.assertEqual(REVIEW.inspect_one(fetch, 118)["code_ci"], "BLOCKED")

    def test_stale_or_forged_check_sha_blocks(self):
        fetch, checks, _ = fixture()
        checks[0]["head_sha"] = "b" * 40
        self.assertEqual(REVIEW.inspect_one(fetch, 118)["code_ci"], "BLOCKED")

    def test_in_progress_check_blocks(self):
        fetch, checks, _ = fixture()
        checks[0]["status"] = "in_progress"
        checks[0]["conclusion"] = None
        self.assertEqual(REVIEW.inspect_one(fetch, 118)["code_ci"], "BLOCKED")

    def test_only_fresh_other_party_approval_counts(self):
        fetch, _, _ = fixture(approvals=(("human", "b" * 40), ("author", HEAD)))
        self.assertEqual(REVIEW.inspect_one(fetch, 118)["sha_bound_formal_approvals"], 0)
        fetch, _, _ = fixture(approvals=(("human", HEAD),))
        self.assertEqual(REVIEW.inspect_one(fetch, 118)["sha_bound_formal_approvals"], 1)

    def test_draft_is_not_review_ready(self):
        fetch, _, _ = fixture(draft=True)
        self.assertFalse(REVIEW.inspect_one(fetch, 118)["pr_open_ready_for_review"])

    def test_invalid_head_is_rejected(self):
        fetch, _, pr = fixture()
        pr["head"]["sha"] = "not-a-hash"
        with self.assertRaises(REVIEW.EvidenceError):
            REVIEW.inspect_one(fetch, 118)

    def test_unauthorized_product_is_rejected(self):
        with self.assertRaises(REVIEW.EvidenceError):
            REVIEW.inspect_one(lambda _: {}, 120)

    def test_missing_or_paginated_checks_fail_closed(self):
        fetch, checks, _ = fixture()
        checks.clear()
        with self.assertRaises(REVIEW.EvidenceError):
            REVIEW.inspect_one(fetch, 118)

    def test_read_api_rejects_unsafe_path_without_http(self):
        with self.assertRaises(REVIEW.EvidenceError):
            REVIEW.request_json("/repos/WhiteChronos/OtherRepo/pulls/1", "fake")
        with self.assertRaises(REVIEW.EvidenceError):
            REVIEW.request_json("/repos/" + REVIEW.REPO + "/../other", "fake")
        with self.assertRaises(REVIEW.EvidenceError):
            REVIEW.request_json("/repos/" + REVIEW.REPO + "/pulls/118", "")

    def test_report_never_claims_approval_or_production(self):
        fetch, _, _ = fixture()
        markdown = REVIEW.render([REVIEW.inspect_one(fetch, 118)])
        self.assertIn("NOT approval", markdown)
        self.assertIn("No merge, deploy or PRODUCTION_COMPLETE", markdown)


if __name__ == "__main__":
    unittest.main()
