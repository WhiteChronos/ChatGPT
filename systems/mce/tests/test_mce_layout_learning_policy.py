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


def test_selected_l40_variant_has_33_cause_slots_and_preserves_legacy_l50():
    data = load()
    selected = data["project_layout_variants"]["P09_L40_H_DISPLAY_3"]
    assert selected["physical_sheet_last_row"] == 47
    assert selected["cause_first_row"] == 8
    assert selected["cause_last_row"] == 40
    assert selected["max_causes_per_sheet"] == 33
    assert selected["cause_last_row"] - selected["cause_first_row"] + 1 == 33
    assert selected["print_area"] == "A1:AR47"
    assert selected["column_H_display_width"] == 3
    assert selected["column_H_ooxml_mdw7_width"] == 3.7109375
    assert selected["legacy_P09_L50_profile_unchanged"] is True
    assert selected["keep_distinct_effect_header_groups_on_separate_sheets"] is True
    assert selected["never_merge_effect_headers_only_to_reduce_page_count"] is True
    assert selected["preserve_existing_causes_and_x"] is True
    assert selected["no_new_functional_relations"] is True
    assert selected["original_immutable"] is True
    assert selected["no_automatic_project_approval"] is True
    assert data["layout"]["profile"] == "P09_L50_H_DISPLAY_3"


def test_l40_cause_zone_and_physical_footer_row47():
    variant = load()["project_layout_variants"]["P09_L40_H_DISPLAY_3"]
    assert variant["cause_last_row"] == 40
    assert variant["physical_sheet_last_row"] == 47
    assert variant["blank_tail_rows"] == list(range(41, 47))
    assert variant["footer_band_row"] == 47
    assert variant["footer_band_column_start"] == "B"
    assert variant["footer_band_column_end"] == "AR"
    assert variant["footer_band_fill_rgb"] == "D9D9D9"
    assert variant["layout_end_distinct_from_cause_end"] is True
    assert variant["windows_excel_visual_check_required"] is True
