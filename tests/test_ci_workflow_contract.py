from pathlib import Path


WORKFLOW = Path('.github/workflows/engineering-governance.yml')


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding='utf-8')


def test_workflow_keeps_workspace_on_pythonpath():
    text = _workflow_text()
    assert 'PYTHONPATH: ${{ github.workspace }}' in text


def test_workflow_runs_pytest_through_python_module():
    text = _workflow_text()
    assert 'run: python -m pytest -q' in text


def test_workflow_verifies_pipeline_import_contract():
    text = _workflow_text()
    assert 'import pipeline.validate_engineering' in text
    assert 'import pipeline.agents_v4_4' in text


def test_workflow_keeps_minimum_security_and_execution_controls():
    text = _workflow_text()
    assert 'permissions:\n  contents: read' in text
    assert 'timeout-minutes: 10' in text
    assert 'cancel-in-progress: true' in text


def test_dev_dependencies_are_pinned():
    req = Path('requirements-dev.txt').read_text(encoding='utf-8')
    assert 'pytest==' in req
