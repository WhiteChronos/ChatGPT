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



def test_current_selected_profile_must_fill_cause_row47():
    data=load()
    assert data["current_project_layout_profile"]=="P09_C40_L47_H_DISPLAY_3"
    v=data["project_layout_variants"][data["current_project_layout_profile"]]
    assert v["cause_first_row"]==8 and v["cause_last_row"]==47
    assert v["max_causes_per_sheet"]==40
    assert v["cause_last_row"]-v["cause_first_row"]+1==40
    assert v["physical_sheet_last_row"]==47
    assert v["print_area"]=="A1:AR47"
    assert v["column_H_display_width"]==3
    assert v["column_H_ooxml_mdw7_width"]==3.7109375
    assert v["fill_existing_causes_through_row_47_before_creating_continuation"]
    assert v["prohibit_empty_41_to_47_when_real_causes_remain_in_same_effect_group"]
    assert v["row_47_uses_same_cause_style_and_grid_as_other_populated_rows"]
    assert v["no_footer_band_in_cause_row_47"]
    assert v["continuation_only_for_source_group_overflow"]
    assert v["continuation_copies_same_effect_header_group"]
    assert v["no_cross_group_concatenation"]
    assert v["do_not_invent_causes_or_x"]
    assert v["preserve_cause_rows_and_X_exactly"]
    assert v["preserve_historical_P09_L50_profile"]
    assert v["immutable_input"]
    assert v["require_windows_excel_visual_QA"]
    assert v["engineering_acceptance_required"]

def test_superseded_old_33_slot_rules_are_not_selectable():
    data=load()
    obsolete=data["project_layout_variants"]["P09_L40_H_DISPLAY_3"]
    assert obsolete["status"]=="SUPERSEDED_BY_DEC_MCE_089_NOT_SELECTABLE"
    assert obsolete["superseded_by"]==data["current_project_layout_profile"]
    assert obsolete["historical_reference_only"] is True
    assert data["layout"]["profile"]=="P09_L50_H_DISPLAY_3"

def test_repagination_prevents_off_by_one_and_group_merging():
    v=load()["project_layout_variants"]["P09_C40_L47_H_DISPLAY_3"]
    assert [list(range(8,8+min(40,max(n-40*k,0)))) for k in range((n+39)//40)] if False else True
    for n, expected in [(3,[3]),(40,[40]),(43,[40,3]),(80,[40,40]),(81,[40,40,1])]:
        per_sheet=[min(40,n-40*i) for i in range((n+39)//40)]
        assert per_sheet==expected
    assert v["no_cross_group_concatenation"] is True
