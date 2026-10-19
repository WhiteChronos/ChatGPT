#!/usr/bin/env python3
"""Validate six-file specifications without executing project code or external tools."""
import argparse
import json
import re
from pathlib import Path

FILES = ("prd.md", "arquitetura.md", "regras.md", "tarefas.md", "memoria.md", "cenario.md")
ID = re.compile(r"\b(?:REQ|AC|TASK|SC)-\d{2}\b")
TRACEABILITY = re.compile(
    r"\|\s*(REQ-\d{2})\s*\|\s*(TASK-\d{2})\s*\|\s*(SC-\d{2})\s*\|"
    r"\s*(TEST-\d{2})\s*\|\s*(EVIDENCE-\d{2})\s*\|"
)

def validate(folder: Path) -> dict:
    findings = []
    bodies = {}
    for name in FILES:
        target = folder / name
        if not target.is_file():
            findings.append({"file": name, "problem": "missing"})
            continue
        body = target.read_text(encoding="utf-8")
        bodies[name] = body
        if not body.strip() or not body.lstrip().startswith("#"):
            findings.append({"file": name, "problem": "missing heading or content"})
    if len(bodies) == len(FILES):
        required = set(re.findall(r"\bREQ-\d{2}\b", bodies["prd.md"]))
        scenarios = set(re.findall(r"\bREQ-\d{2}\b", bodies["cenario.md"]))
        tasks = set(re.findall(r"\bREQ-\d{2}\b", bodies["tarefas.md"]))
        if not required:
            findings.append({"file": "prd.md", "problem": "no requirement IDs"})
        for req in sorted(required - scenarios):
            findings.append({"file": "cenario.md", "problem": f"missing scenario for {req}"})
        for req in sorted(required - tasks):
            findings.append({"file": "tarefas.md", "problem": f"missing task for {req}"})
        expected_ac = set(re.findall(r"\bAC-\d{2}\b", bodies["prd.md"]))
        for ac in sorted(expected_ac - set(re.findall(r"\bAC-\d{2}\b", bodies["cenario.md"]))):
            findings.append({"file": "cenario.md", "problem": f"missing acceptance case {ac}"})
        traceability_rows = TRACEABILITY.findall(bodies["memoria.md"])
        traced_requirements = {row[0] for row in traceability_rows}
        for req in sorted(required - traced_requirements):
            findings.append({
                "file": "memoria.md",
                "problem": f"missing end-to-end traceability for {req} through TEST and EVIDENCE",
            })
        reference_sources = (
            (1, "tarefas.md"),
            (2, "cenario.md"),
            (3, "cenario.md"),
        )
        for row in traceability_rows:
            for position, source in reference_sources:
                identifier = row[position]
                if identifier not in bodies[source]:
                    findings.append({
                        "file": "memoria.md",
                        "problem": f"invalid traceability reference {identifier} for {row[0]}",
                    })
        evidence_ids = set(re.findall(
            r"(?m)^(?:##\s+|-\s+)(EVIDENCE-\d{2})\b",
            bodies["memoria.md"],
        ))
        for row in traceability_rows:
            if row[4] not in evidence_ids:
                findings.append({
                    "file": "memoria.md",
                    "problem": f"invalid traceability reference {row[4]} for {row[0]}",
                })
    return {"files_checked": len(bodies), "status": "PASS" if not findings else "FAIL", "findings": findings}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    result = validate(args.directory)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
