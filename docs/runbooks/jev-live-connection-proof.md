# Jev live connection proof — TypeSafe AI + DefAPI

## Evidence levels

Offline CI verifies only local contracts. An unauthenticated HTTPS HEAD (even HTTP 401) demonstrates reachability from the executing host but NOT valid API credentials. A true live pass requires independent authenticated evaluations through the real TypeSafe and DefAPI clients. A connected ChatGPT/Codex plugin is a separate requirement.

## Observed in this execution environment on 2026-10-12

Both API keys were unavailable. DNS lookups for api.typesafe.ai and api.defapi.org failed in this container. Live authenticated inference was NOT run or verified. These restrictions do not establish that either provider is globally unavailable.

## Reproduce from an authorized host

Check out the reviewed PR SHA, then run the free, uncredentialed HTTPS preflight:

    python plugins/jev-decisions/scripts/verify_live.py

After a human explicitly authorizes potentially billable synthetic inference, provisions distinct TYPESAFE_API_KEY and DEFAPI_API_KEY through a secure secret manager and approves installation of the official TypeSafe Python SDK in that host, run:

    export JEV_LIVE_SMOKE_APPROVED=YES
    python plugins/jev-decisions/scripts/verify_live.py --execute --output /secure/jev-proof.json

The script sends only synthetic data, no customer data, source code or private engineering documents. It makes one logical evaluation call per provider; the upstream TypeSafe SDK may retry internally. No secrets, Authorization headers, raw model responses or full DefAPI task IDs are emitted. Evidence files have owner-only permissions and are never overwritten.

Accept live proof only if the resulting JSON reports LIVE_VERIFIED_BOTH, both individual inference statuses are AUTHENTICATED_INFERENCE_PASS, the model IDs match, and the token usage is valid. A recorded checkout SHA, timestamp and reviewed redacted evidence file should accompany the PR review. Never infer success from fixture values or 401 responses.

The tests/test_jev_verify_live.py suite uses fake clients and never makes live network requests. Do not run this script with --execute automatically in CI. No merge, deployment, secret provisioning, host discovery, scheduled paid calls or PRODUCTION_COMPLETE is authorized by these instructions.

References: https://docs.typesafe.ai/api ; https://docs.typesafe.ai/models ; https://defapi.org/api/model/en/typesafe/jev-1.13 .
