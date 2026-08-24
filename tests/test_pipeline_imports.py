"""Test pipeline module imports."""


def test_import_validate_engineering():
    """Verify validate_engineering module can be imported."""
    try:
        import pipeline.validate_engineering
        assert pipeline.validate_engineering is not None
    except ImportError as e:
        raise AssertionError(f"Failed to import pipeline.validate_engineering: {e}")


def test_import_agents_v4_4():
    """Verify agents_v4_4 module can be imported."""
    try:
        import pipeline.agents_v4_4
        assert pipeline.agents_v4_4 is not None
    except ImportError as e:
        raise AssertionError(f"Failed to import pipeline.agents_v4_4: {e}")


def test_agents_v4_4_golden_checks():
    """Verify agents_v4_4 has correct golden constants."""
    import pipeline.agents_v4_4 as agents
    
    # Check GOLDEN_CHECKS dictionary
    assert hasattr(agents, "GOLDEN_CHECKS")
    golden = agents.GOLDEN_CHECKS
    
    assert golden.get("symbol_external_mm") == 12.0, "symbol_external_mm should be 12.0"
    assert golden.get("aspect_ratio") == 1.0, "aspect_ratio should be 1.0"
    assert golden.get("cmd_run_fault_available_separate") is True
