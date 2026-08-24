#!/usr/bin/env bash
# Debug script to identify workflow failures locally

set -x  # Print all commands
set -e  # Exit on first error

echo "=========================================="
echo "Engineering Governance Debug Script"
echo "=========================================="

echo ""
echo "Step 1: Verify Python environment"
python --version
echo "PYTHONPATH: $PYTHONPATH"
echo "GITHUB_WORKSPACE: $GITHUB_WORKSPACE"

echo ""
echo "Step 2: Verify CI dependencies"
python -m pip list | grep pytest

echo ""
echo "Step 3: Test Python imports"
python -c "import pipeline.validate_engineering; print('✓ pipeline.validate_engineering imported')"
python -c "import pipeline.agents_v4_4; print('✓ pipeline.agents_v4_4 imported')"

echo ""
echo "Step 4: Compile Python sources"
python -m compileall -v pipeline tests

echo ""
echo "Step 5: List all tests"
find tests -name "test_*.py" -type f | sort
python -m pytest --collect-only -q

echo ""
echo "Step 6: Run CI contract tests with verbose output"
python -m pytest -vv tests/test_ci_workflow_contract.py 2>&1 | head -100

echo ""
echo "Step 7: Verify governance files"
echo "Checking governance files:"
ls -la governance/
ls -la memory/
ls -la schemas/

echo ""
echo "Step 8: Test grep patterns"
echo "Searching for '12 mm':"
grep "12 mm" governance/PROMPT_MESTRE_AUTOMACAO_v4_4.md || echo "NOT FOUND"

echo ""
echo "Searching for 'CMD, RUN, FAULT':"
grep "CMD, RUN, FAULT" governance/PROMPT_MESTRE_AUTOMACAO_v4_4.md || echo "NOT FOUND"

echo ""
echo "=========================================="
echo "Debug script complete"
echo "=========================================="
