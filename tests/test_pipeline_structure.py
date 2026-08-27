"""Estrutura obrigatória do pipeline v4.6."""

from pathlib import Path


def test_pipeline_has_required_modules():
    required_files = [
        "pipeline/__init__.py",
        "pipeline/validate_engineering.py",
        "pipeline/agents_v4_4.py",
        "pipeline/agents_v4_6.py",
        "pipeline/li_io_standard.py",
        "pipeline/apply_li_io_text_patch.py",
        "pipeline/xlsx_layout_guard.py",
        "pipeline/audit_document_plugins.py",
    ]
    for file_path in required_files:
        path = Path(file_path)
        assert path.is_file(), f"Missing required file: {file_path}"
