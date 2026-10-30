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
