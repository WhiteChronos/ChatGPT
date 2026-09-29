from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_auto_engineering_prompt_enforces_candidate_only_and_forbidden_actions():
    p = ROOT / 'prompts/PROMPT_CODEX_AUT_PANEL_AUTO_ENGINEERING_V1.md'
    assert p.exists()
    text = p.read_text(encoding='utf-8')
    required = [
        'aut_panel_candidate_revision.py',
        'CANDIDATE_READY_FOR_HUMAN_REVIEW',
        'historical R02',
        'auto-merge',
        'production PLC',
        'deterministic',
        'rollback',
        'canonical input hashes',
    ]
    for token in required:
        assert token in text
    assert 'must not weaken' in text.lower()
    assert 'must not overwrite' in text.lower()


def test_auto_engineering_prompt_requires_evidence_and_test_report():
    text = (ROOT / 'prompts/PROMPT_CODEX_AUT_PANEL_AUTO_ENGINEERING_V1.md').read_text(encoding='utf-8')
    for token in ['files changed', 'source evidence', 'candidate delta', 'tests run', 'engineering HOLDs', 'rollback path']:
        assert token.lower() in text.lower()


def test_candidate_review_prompt_cannot_release_or_self_waive():
    p = ROOT / "prompts/PROMPT_CODEX_AUT_PANEL_CANDIDATE_REVIEW_V1.md"
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    for token in ["artifact hashes", "deterministic", "human approval", "Aprovado para emissão", "auto-merge", "waive"]:
        assert token.lower() in text.lower()
    assert "must not declare" in text.lower()
    assert "must not merge" in text.lower()
    assert "must not waive" in text.lower()
