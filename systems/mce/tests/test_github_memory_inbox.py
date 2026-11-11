"""MCE GitHub Issue inbox adversarial tests."""
import importlib.util,json,subprocess,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"scripts"/"github_memory_inbox.py"
SPEC=importlib.util.spec_from_file_location("mce_inbox_test",SOURCE)
INBOX=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INBOX)

def event(**overrides):
    payload={"schema":1,"system":"MCE_INDEPENDENTE","kind":"DECISION","id":"DEC-MCE-014",
             "date":"2026-10-29","title":"Public decision","summary":"Metadata only",
             "origin":"USER_REQUEST","approval":"NOT_ENG_APPROVED"}
    payload.update(overrides)
    fence=chr(96)*3
    return {"id":123,"user":{"login":"WhiteChronos"},
            "body":"<!-- WC_MEMORY_EVENT_V1 -->\n"+fence+"json\n"+json.dumps(payload)+"\n"+fence}

def test_valid_event_unapproved():
    assert INBOX.parse_comment(event())["approval"]=="NOT_ENG_APPROVED"

def test_mirror_and_pending():
    assert INBOX.inspect([event()],"")["pending_mirror"]==1
    assert INBOX.inspect([event()],"| DEC-MCE-014 | text |")["pending_mirror"]==0

def test_cross_product_and_untrusted_rejected():
    with pytest.raises(INBOX.IntakeError,match="product"):
        INBOX.parse_comment(event(system="REA_INDEPENDENTE"))
    x=event()
    x["user"]["login"]="outsider"
    with pytest.raises(INBOX.IntakeError,match="Untrusted"):
        INBOX.parse_comment(x)

def test_false_approval_sensitive_and_collision_blocked():
    with pytest.raises(INBOX.IntakeError,match="Unapproved"):
        INBOX.parse_comment(event(approval="APPROVED"))
    with pytest.raises(INBOX.IntakeError,match="Sensitive"):
        INBOX.parse_comment(event(summary="Authorization: Bearer fake"))
    with pytest.raises(INBOX.IntakeError,match="Duplicate"):
        INBOX.inspect([event(),event()],"")

def test_invalid_id_and_date_blocked():
    with pytest.raises(INBOX.IntakeError,match="ID"):
        INBOX.parse_comment(event(kind="PENDENCY"))
    with pytest.raises(INBOX.IntakeError,match="calendar"):
        INBOX.parse_comment(event(date="2026-02-30"))

def test_offline_cli(tmp_path):
    p=tmp_path/"comments.json"
    p.write_text(json.dumps([event()]))
    r=subprocess.run([sys.executable,str(SOURCE),"--comments-json",str(p)],capture_output=True,text=True)
    assert r.returncode==0 and json.loads(r.stdout)["system"]=="MCE_INDEPENDENTE"

def test_real_issue_event_061_metadata_accepted():
    e=event(id="DEC-MCE-061", date="2026-11-10",
            origin="USER_EXPLICIT_REQUEST",
            approval="NOT_ENGINEERING_APPROVED",
            production_complete=False)
    e["body"]=e["body"].replace("Metadata only", "A" * 1221)
    assert INBOX.parse_comment(e)["id"] == "DEC-MCE-061"

def test_legacy_metadata_allowed_but_production_or_unknown_rejected():
    e=event(origin="USER_CORRECTION",
            approval="VISUAL_LAYOUT_ONLY; ENGINEERING_NOT_APPROVED",
            supersedes="DEC-MCE-036",commit="a" * 40,production_complete=False)
    assert INBOX.parse_comment(e)["kind"] == "DECISION"
    with pytest.raises(INBOX.IntakeError,match="Production"):
        INBOX.parse_comment(event(production_complete=True))
    with pytest.raises(INBOX.IntakeError,match="fields"):
        INBOX.parse_comment(event(secret_payload="not allowed"))
    with pytest.raises(INBOX.IntakeError,match="Unapproved"):
        INBOX.parse_comment(event(approval="ENGINEERING_APPROVED"))

def test_issue_061_keeps_append_only_pending_until_mirrored():
    e=event(id="DEC-MCE-061",date="2026-11-10",
            origin="USER_EXPLICIT_REQUEST",approval="NOT_ENGINEERING_APPROVED",
            production_complete=False)
    assert INBOX.inspect([e],"not yet mirrored")["pending_mirror"] == 1

def test_historical_kind_id_mismatch_only_allowlisted():
    for kind, identifier in [
        ("CORRECTION","DEC-MCE-039"), ("CORRECTION","DEC-MCE-040"),
        ("EVIDENCE","DEC-MCE-057"), ("EVIDENCE","DEC-MCE-058"),
    ]:
        assert INBOX.parse_comment(event(kind=kind,id=identifier))["id"] == identifier
    with pytest.raises(INBOX.IntakeError, match="kind"):
        INBOX.parse_comment(event(kind="CORRECTION",id="DEC-MCE-062"))
    with pytest.raises(INBOX.IntakeError, match="ID"):
        INBOX.parse_comment(event(kind="EVIDENCE",id="DEC-MCE-062"))
