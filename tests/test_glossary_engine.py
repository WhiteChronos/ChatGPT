from pipeline.glossary_engine import validate


def test_glossary_engine_validates_seed_data():
    assert validate() == []


def test_github_source_cannot_be_normative_authority():
    # The canonical seed data must never classify an E7 GitHub-only source as normative.
    assert all("GitHub não pode, sozinho, confirmar conteúdo normativo" not in e for e in validate())
