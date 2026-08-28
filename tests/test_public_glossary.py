from pipeline.build_interactive_glossary import MASTER, REGISTRY, build_page, iter_staging_records, load_json
from pipeline.build_public_glossary import OUTPUT


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
