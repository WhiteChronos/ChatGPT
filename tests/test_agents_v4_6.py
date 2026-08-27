import pipeline.agents_v4_6 as agents


def test_li_agent_and_plugin_security_are_registered():
    assert "LIInputOutputStandardAgent" in agents.AGENTS
    assert "DocumentToolingDiscoveryAgent" in agents.AGENTS
    assert "PluginSecurityAgent" in agents.AGENTS


def test_v46_golden_document_rules():
    checks = agents.GOLDEN_CHECKS
    assert checks["document_layout_immutable"] is True
    assert checks["sheet_count_target_driven"] is True
    assert checks["font_size_immutable"] is True
    assert checks["notes_sheet_only"] is True
    assert checks["plugin_auto_install_forbidden"] is True
