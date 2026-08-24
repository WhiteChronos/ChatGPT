from pathlib import Path


WORKFLOW = Path('.github/workflows/engineering-governance.yml')


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding='utf-8')


def test_workflow_keeps_workspace_on_pythonpath():
    text = _workflow_text()
    assert 'PYTHONPATH: ${{ github.workspace }}' in text


def test_workflow_runs_pytest_through_python_module():
    text = _workflow_text()
    assert 'python -m pytest -q' in text


def test_workflow_verifies_pipeline_import_contract():
    text = _workflow_text()
    assert 'import pipeline.validate_engineering' in text
    assert 'import pipeline.agents_v4_4' in text


def test_workflow_keeps_minimum_security_and_execution_controls():
    text = _workflow_text()
    assert 'permissions:\n  contents: read' in text
    assert 'timeout-minutes: 10' in text
    assert 'cancel-in-progress: true' in text
    assert 'persist-credentials: false' in text


def test_workflow_uses_current_node24_actions():
    text = _workflow_text()
    assert 'actions/checkout@v7' in text
    assert 'actions/setup-python@v7' in text


def test_workflow_keeps_manual_dispatch_and_dependency_validation():
    text = _workflow_text()
    assert 'workflow_dispatch:' in text
    assert 'python -m pip check' in text
    assert 'python -m compileall -q pipeline tests' in text


def test_workflow_does_not_self_grep_github_expression():
    text = _workflow_text()
    assert "grep -Fq 'PYTHONPATH: ${{ github.workspace }}'" not in text


def test_dev_dependencies_are_pinned():
    req = Path('requirements-dev.txt').read_text(encoding='utf-8')
    assert 'pytest==' in req
