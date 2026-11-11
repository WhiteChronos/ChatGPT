# Focused security evidence

The package adds implicit invocation metadata for 44 original adapters. The metadata does not grant tools, permissions or executable commands. `tests/test_security.py` enforces the exact allowed metadata keys across all 44 entries and validates all 516 plans are declarative with no executed/background state. It also checks that the plan function does not reference code evaluation, file access, subprocess or networking primitives. This is a focused regression, not a general security scanner or an assurance of upstream runtime safety.

`tests/test_workflows.py` additionally covers unknown commands/modes, path escape rejection, installation preflight preserving human changes, distinct portable package identities, and registry consistency. Run both suites with `python -B -m unittest discover -s plugins/repository-workflows/tests -v`. CI runs the same command on Windows with read-only contents permission.

No ECC application permissions are modified. No branch protection is disabled. No upstream skill bodies, credentials, private conversation data or local runtime configuration are distributed.
