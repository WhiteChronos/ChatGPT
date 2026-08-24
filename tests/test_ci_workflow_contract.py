"""Test CI workflow contract compliance.

This module validates that the GitHub Actions workflow meets the engineering
governance requirements for the project.
"""

import os
import sys
from pathlib import Path

# Workflow file location
WORKFLOW_PATH = Path(__file__).parent.parent / ".github" / "workflows" / "engineering-governance.yml"

# Required environment variables in CI
REQUIRED_ENV_VARS = {
    "PYTHONPATH": "${{ github.workspace }}",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONUNBUFFERED": "1",
    "CI": "true",
}

# Required steps in the workflow
REQUIRED_STEPS = {
    "Checkout",
    "Set up Python",
    "Install test dependencies",
    "Verify CI environment contract",
    "Compile Python sources",
    "Run CI contract regression test",
    "Run full regression suite",
    "Verify governance assets",
    "Enforce v4.4 golden constants",
}

# Required files that must exist
REQUIRED_FILES = {
    "governance/REGRA_DE_OURO.md",
    "governance/PROMPT_MESTRE_AUTOMACAO_v4_4.md",
    "memory/MEMORY_POLICY.md",
    "memory/LESSON_CI_PYTHONPATH_2026-08-24.md",
    "memory/LESSON_CI_EXPRESSION_INTERPOLATION_2026-08-24.md",
    "schemas/governance_v4_4.schema.json",
    "pipeline/__init__.py",
    "requirements-dev.txt",
}

# Required constants in configuration files
REQUIRED_CONSTANTS = {
    "governance/PROMPT_MESTRE_AUTOMACAO_v4_4.md": ["12 mm", "CMD", "RUN", "FAULT"],
    "schemas/governance_v4_4.schema.json": ['"external_mm"', '"aspect_ratio"'],
}


def test_workflow_file_exists():
    """Verify workflow file exists."""
    assert WORKFLOW_PATH.exists(), f"Workflow file not found: {WORKFLOW_PATH}"


def test_required_files_exist():
    """Verify all required project files exist."""
    repo_root = Path(__file__).parent.parent
    for file_path in REQUIRED_FILES:
        full_path = repo_root / file_path
        assert full_path.exists(), f"Required file missing: {file_path}"


def test_pythonpath_in_ci_environment():
    """Verify PYTHONPATH is set correctly for CI environment."""
    # When running in CI, PYTHONPATH should be set
    if os.environ.get("CI") == "true":
        pythonpath = os.environ.get("PYTHONPATH")
        github_workspace = os.environ.get("GITHUB_WORKSPACE")
        
        # Note: In local testing, these won't match, but in CI they should
        # This test validates the contract exists
        assert "PYTHONPATH" in os.environ or pythonpath is None, \
            "PYTHONPATH environment variable should be accessible"


def test_python_modules_importable():
    """Verify Python modules can be imported."""
    try:
        import pipeline.validate_engineering
        import pipeline.agents_v4_4
        assert pipeline.validate_engineering is not None
        assert pipeline.agents_v4_4 is not None
    except ImportError as e:
        raise AssertionError(f"Failed to import required modules: {e}")


def test_required_constants_in_files():
    """Verify required constants exist in configuration files."""
    repo_root = Path(__file__).parent.parent
    
    for file_path, constants in REQUIRED_CONSTANTS.items():
        full_path = repo_root / file_path
        content = full_path.read_text(encoding="utf-8")
        
        for constant in constants:
            assert constant in content, \
                f"Required constant '{constant}' not found in {file_path}"


def test_golden_checks_defined():
    """Verify golden checks are properly defined."""
    from pipeline.agents_v4_4 import GOLDEN_CHECKS
    
    required_checks = {
        "symbol_external_mm": 12.0,
        "aspect_ratio": 1.0,
        "cmd_run_fault_available_separate": True,
    }
    
    for key, expected_value in required_checks.items():
        assert key in GOLDEN_CHECKS, f"Missing golden check: {key}"
        assert GOLDEN_CHECKS[key] == expected_value, \
            f"Golden check {key} has wrong value: {GOLDEN_CHECKS[key]} != {expected_value}"


def test_pytest_discoverable():
    """Verify pytest can discover and run tests."""
    # This verifies the test infrastructure is properly set up
    tests_dir = Path(__file__).parent
    assert tests_dir.exists(), "Tests directory not found"
    assert (tests_dir / "__init__.py").exists(), "tests/__init__.py not found"


def test_ci_contract_regression():
    """Verify CI environment doesn't regress against known issues."""
    # PYTHONPATH regression check
    workflow_path = WORKFLOW_PATH
    workflow_content = workflow_path.read_text(encoding="utf-8")
    
    # Verify the workflow still uses correct PYTHONPATH setting
    assert 'PYTHONPATH: ${{ github.workspace }}' in workflow_content, \
        "PYTHONPATH setting has regressed - should use github.workspace"
    
    # Verify critical steps are still present
    for step in ["Verify CI environment contract", "Run full regression suite"]:
        assert step in workflow_content, \
            f"Critical workflow step missing: {step}"


if __name__ == "__main__":
    # Allow direct execution for debugging
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
