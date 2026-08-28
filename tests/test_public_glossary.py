import os
import subprocess
import sys
from pathlib import Path

from pipeline.build_interactive_glossary import MASTER, REGISTRY, build_page, iter_staging_records, load_json
from pipeline.build_public_glossary import OUTPUT

ROOT = Path(__file__).resolve().parents[1]


def test_public_glossary_has_stable_route_and_interactive_content():
    assert OUTPUT.as_posix().endswith("docs/glossario-interativo.md")

    master = load_json(MASTER)
    registry = load_json(REGISTRY)
    staging = iter_staging_records()
    page = build_page(master, registry, staging)

    assert "Glossário técnico interativo" in page
    assert "BASE APROVADA" in page
    assert "STAGING — NÃO APROVADO" in page
    assert 'id="deks-glossary-search"' in page
    assert 'id="deks-glossary-grid"' in page
    assert len(staging) == 40


def test_public_builder_runs_as_script_without_pythonpath():
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, "pipeline/build_public_glossary.py"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "PUBLIC_INTERACTIVE_GLOSSARY_BUILT" in result.stdout
    assert OUTPUT.exists()
