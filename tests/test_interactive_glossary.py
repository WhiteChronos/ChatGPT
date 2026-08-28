from pipeline.build_interactive_glossary import (
    MASTER,
    REGISTRY,
    build_page,
    iter_staging_records,
    load_json,
    symbol_svg,
)


def test_interactive_glossary_separates_canonical_and_staging():
    master = load_json(MASTER)
    registry = load_json(REGISTRY)
    staging = iter_staging_records()
    page = build_page(master, registry, staging)

    assert 'data-scope="canonical"' in page
    assert 'data-scope="staging"' in page
    assert "BASE APROVADA" in page
    assert "STAGING — NÃO APROVADO" in page
    assert "INGESTÃO NÃO É APROVAÇÃO" in page
    assert len(staging) == 40


def test_symbol_dimension_is_explicit_only_for_discrete_field_cell():
    staging = iter_staging_records()
    symbols = [item for item in staging if item.get("entity_type") == "symbol"]
    explicit = [
        item
        for item in symbols
        if (item.get("payload") or {}).get("explicit_dimension_mm") is not None
    ]

    assert len(symbols) == 16
    assert len(explicit) == 1
    assert explicit[0]["external_id"] == "DM-INSTRUMENTO_DISCRETO-CAMPO"
    assert explicit[0]["payload"]["explicit_dimension_mm"] == 12


def test_symbol_svg_preserves_location_marking_semantics():
    svg = symbol_svg(
        {
            "base_geometry": "circle",
            "location_marking": "one_dashed_horizontal_bar",
        }
    )
    assert "<circle" in svg
    assert "stroke-dasharray" in svg
