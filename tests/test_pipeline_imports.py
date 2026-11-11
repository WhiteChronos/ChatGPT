"""Importabilidade dos módulos ativos e do shim de compatibilidade."""


def test_pipeline_modules_importable():
    import pipeline.agents_v4_4
    import pipeline.agents_v4_6
    import pipeline.apply_li_io_text_patch
    import pipeline.audit_document_plugins
    import pipeline.li_io_standard
    import pipeline.validate_engineering
    import pipeline.xlsx_layout_guard

    assert pipeline.agents_v4_6.GOLDEN_CHECKS["sheet_count_target_driven"] is True
    assert pipeline.agents_v4_4.GOLDEN_CHECKS["document_layout_immutable"] is True
