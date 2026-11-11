"""MCE: test configurable display H=3 and nonautonomous improvement."""
import json
from pathlib import Path
DATA=Path(__file__).resolve().parents[1] / "datacenter" / "MCE_LAYOUT_LEARNING_POLICY.json"

def load():
    return json.loads(DATA.read_text(encoding="utf-8"))

def test_h_display3_ooxml_mdw7():
    x=load()["layout"]
    assert x["column"]=="H"
    assert x["display_width"]==3
    assert x["ooxml_width_mdw7"]==3.7109375
    assert x["other_columns_unchanged"] is True
    assert int(((3*7+5)/7)*256)/256==x["ooxml_width_mdw7"]

def test_profile_requires_contract_and_windows_qa():
    x=load()
    assert x["state"]=="PROFILE_CANDIDATE_REQUIRES_APPROVAL"
    assert x["layout"]["application_scope"]=="PROJECT_CONTRACT_ONLY"
    assert x["layout"]["windows_excel_qa_required"] is True

def test_learning_enabled_only_on_explicit_execution():
    x=load()["learning"]
    assert x["enabled_on_each_explicit_workflow_execution"] is True
    assert x["background_agent"] is False
    assert x["always_running"] is False
    assert x["changes_model_weights"] is False
    assert x["autonomous_edits"] is False

def test_question_and_x_safety():
    x=load()
    assert x["deliverables"]["word_columns"]==["Localização","Folha","Pergunta"]
    assert x["deliverables"]["spreadsheet_yellow_only_no_comments"] is True
    assert x["deliverables"]["preserve_distinct_functional_decisions"] is True
    assert x["deliverables"]["word_excel_pv_independent"] is True
    assert x["safety"]["no_x_without_functional_evidence"] is True
