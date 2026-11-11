from __future__ import annotations

import json
from pathlib import Path

from pipeline import deks_engine

ROOT = Path(__file__).resolve().parents[1]


def test_deks_validation_has_no_errors() -> None:
    errors, _warnings = deks_engine.validate()
    assert errors == []


def test_deks_config_prohibits_github_normative_authority() -> None:
    config = json.loads((ROOT / "datacenter" / "DEKS_CONFIG.json").read_text(encoding="utf-8"))
    assert config["governance"]["github_is_normative_authority"] is False
    assert config["governance"]["auto_promote_technical_content"] is False


def test_deks_required_tool_sources_are_registered() -> None:
    sources = json.loads((ROOT / "datacenter" / "GLOSSARY_SOURCES.json").read_text(encoding="utf-8"))
    source_ids = {item["id"] for item in sources["sources"]}
    assert {"GH-MKDOCS-MATERIAL", "GH-MERMAID"} <= source_ids


def test_mkdocs_config_exists() -> None:
    assert (ROOT / "mkdocs.yml").is_file()
