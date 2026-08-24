"""Test pipeline structure and modules."""

from pathlib import Path


def test_pipeline_directory_exists():
    """Verify pipeline directory exists."""
    pipeline_dir = Path("pipeline")
    assert pipeline_dir.exists(), "pipeline directory not found"
    assert pipeline_dir.is_dir(), "pipeline is not a directory"


def test_pipeline_has_required_modules():
    """Verify pipeline has required Python modules."""
    required_files = [
        "pipeline/validate_engineering.py",
        "pipeline/agents_v4_4.py",
    ]
    for file_path in required_files:
        path = Path(file_path)
        assert path.exists(), f"Missing required file: {file_path}"
        assert path.is_file(), f"{file_path} is not a file"


def test_pipeline_init_exists():
    """Verify pipeline package has __init__.py."""
    init_path = Path("pipeline/__init__.py")
    assert init_path.exists(), "pipeline/__init__.py not found"
