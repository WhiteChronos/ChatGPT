from pipeline.agents_v4_7 import AGENTS, GOLDEN_CHECKS, MD_MODEL_ID, MD_POLICY


def test_md_model_and_agents_are_mandatory():
    assert MD_MODEL_ID == "MD_AUTOMATION_PETROBRAS_V1_0"
    for name in (
        "MDTemplateStandardAgent",
        "MDParagraphSpacingLockAgent",
        "MDRevisionGrayLifecycleAgent",
        "MDCurrentRevisionTraceabilityAgent",
        "MDLayoutFingerprintAgent",
        "MDVisualQAAgent",
    ):
        assert name in AGENTS


def test_md_golden_checks_lock_spacing_and_revision_gray():
    assert GOLDEN_CHECKS["md_paragraph_spacing_immutable"] is True
    assert GOLDEN_CHECKS["md_line_spacing_immutable"] is True
    assert GOLDEN_CHECKS["md_clear_legacy_gray"] is True
    assert GOLDEN_CHECKS["md_current_revision_gray_only"] is True
    assert GOLDEN_CHECKS["md_current_gray_continuous"] is True
    assert MD_POLICY["artificial_spacing_for_gray_forbidden"] is True
    assert MD_POLICY["quality_mode"] == "BLOCK_ON_ANY_FAILURE"
