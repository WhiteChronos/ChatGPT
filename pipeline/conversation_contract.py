#!/usr/bin/env python3
"""Contrato de continuidade entre conversas do projeto AUT Panel.

Este utilitário não substitui o motor de engenharia. Ele garante que uma nova
conversa carregue o mesmo Prompt Mestre, Golden Rules, pipeline, Data Center,
Data Sheet, template e memória operacional antes de executar uma tarefa.

Subcomandos:
  validate  - valida vínculos, IDs, hashes e sequência fail-closed.
  bootstrap - imprime o contexto mínimo que a nova conversa deve declarar.
  dispatch  - transforma /explaincode ou /refactor em envelope operacional.
  sync      - atualiza somente o bloco mutável da memória operacional.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML é obrigatório: pip install pyyaml") from exc

EXPECTED_SEQUENCE = [
    "BOOTSTRAP_CONTEXT",
    "DATACENTER",
    "DATASHEET",
    "SELECT",
    "LI_QUANTITY",
    "LOAD_BALANCE",
    "BOM",
    "LAYOUT",
    "RENDER_IMAGE",
    "QA",
    "MEMORY_SYNC",
    "RELEASE",
]

LOCKED_PATHS = {
    "governance/golden_rules.yaml",
    "pipeline/pipeline.yaml",
    "datacenter/datacenter.yaml",
    "datasheet/datasheet.yaml",
    "templates/panel_template.yaml",
    "prompts/PROMPT_MASTER_AUT_PANEL.md",
    "prompts/PROMPT_BOOTSTRAP_NOVA_CONVERSA.md",
    "context/AUT_PANEL_CONVERSATION_MEMORY.yaml",
    "pipeline/conversation_contract.py",
}


class ContractError(RuntimeError):
    """Falha de contrato que deve bloquear avanço."""


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ContractError(f"YAML inválido ou raiz não-mapeamento: {path}")
    return data


def save_yaml(path: Path, data: Mapping[str, Any]) -> None:
    path.write_text(
        yaml.safe_dump(dict(data), allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_object(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise ContractError(f"{code}: {message}")


def project_paths(root: Path) -> dict[str, Path]:
    return {
        "golden": root / "governance/golden_rules.yaml",
        "pipeline": root / "pipeline/pipeline.yaml",
        "datacenter": root / "datacenter/datacenter.yaml",
        "datasheet": root / "datasheet/datasheet.yaml",
        "template": root / "templates/panel_template.yaml",
        "prompt": root / "prompts/PROMPT_MASTER_AUT_PANEL.md",
        "bootstrap_prompt": root / "prompts/PROMPT_BOOTSTRAP_NOVA_CONVERSA.md",
        "memory": root / "context/AUT_PANEL_CONVERSATION_MEMORY.yaml",
        "script": root / "pipeline/conversation_contract.py",
    }


def load_contract(root: Path) -> dict[str, Any]:
    paths = project_paths(root)
    for name, path in paths.items():
        require(path.exists(), "BOOTSTRAP", f"arquivo obrigatório ausente ({name}): {path}")
    return {
        "paths": paths,
        "golden": load_yaml(paths["golden"]),
        "pipeline": load_yaml(paths["pipeline"]),
        "datacenter": load_yaml(paths["datacenter"]),
        "datasheet": load_yaml(paths["datasheet"]),
        "template": load_yaml(paths["template"]),
        "memory": load_yaml(paths["memory"]),
    }


def validate_contract(root: Path) -> dict[str, Any]:
    c = load_contract(root)
    paths = c["paths"]
    golden, pipeline = c["golden"], c["pipeline"]
    datacenter, datasheet = c["datacenter"], c["datasheet"]
    template, memory = c["template"], c["memory"]

    require(golden.get("status") == "LOCKED_APPROVED_STANDARD" and golden.get("immutable") is True,
            "GR-041", "Golden Rules não estão bloqueadas.")
    require(pipeline.get("status") == "LOCKED_APPROVED_STANDARD" and pipeline.get("immutable") is True,
            "GR-041", "pipeline não está bloqueado.")
    require(datacenter.get("status") == "LOCKED_APPROVED_STANDARD" and datacenter.get("immutable") is True,
            "GR-041", "Data Center não está bloqueado.")
    require(datasheet.get("status") == "LOCKED_APPROVED_STANDARD" and datasheet.get("immutable") is True,
            "GR-041", "Data Sheet registry não está bloqueado.")

    immutable = memory.get("immutable_contract") or {}
    require(memory.get("memory_id") == "AUT-PANEL-CONVERSATION-BRIDGE-V1", "GR-047", "memory_id inválido.")
    require(memory.get("status") == "ACTIVE", "GR-047", "memória operacional não está ativa.")

    require(immutable.get("standard_id") == pipeline.get("standard_id") == datacenter.get("standard_id") == datasheet.get("standard_id"),
            "GR-046", "standard_id divergente entre contratos.")
    require(immutable.get("pipeline_id") == pipeline.get("pipeline_id"), "GR-046", "pipeline_id diverge da memória.")
    require(immutable.get("golden_rules_id") == golden.get("registry_id"), "GR-046", "golden_rules_id diverge.")
    require(immutable.get("datacenter_id") == datacenter.get("datacenter_id"), "GR-046", "datacenter_id diverge.")
    require(immutable.get("datasheet_registry_id") == datasheet.get("datasheet_registry_id"), "GR-046", "datasheet_registry_id diverge.")

    rules = {str(x.get("id")) for x in golden.get("required_rules", [])}
    for rule in ("GR-046", "GR-047", "GR-048", "GR-049"):
        require(rule in rules, rule, "regra de continuidade ausente das Golden Rules.")

    sequence = [str(x.get("id")) for x in pipeline.get("sequence", [])]
    require(sequence == EXPECTED_SEQUENCE, "GR-046", f"sequência divergente: {sequence}")

    contracts = pipeline.get("contracts") or {}
    expected_paths = {
        "golden_rules": "governance/golden_rules.yaml",
        "panel_template": "templates/panel_template.yaml",
        "prompt_master": "prompts/PROMPT_MASTER_AUT_PANEL.md",
        "conversation_memory": "context/AUT_PANEL_CONVERSATION_MEMORY.yaml",
        "conversation_contract": "pipeline/conversation_contract.py",
        "datacenter": "datacenter/datacenter.yaml",
        "datasheet": "datasheet/datasheet.yaml",
    }
    for key, value in expected_paths.items():
        require(contracts.get(key) == value, "GR-046", f"pipeline.contracts.{key} divergente.")

    canonical = datacenter.get("canonical_sources") or {}
    for key, value in expected_paths.items():
        alias = {"golden_rules": "golden_rules_yaml", "panel_template": "panel_template_yaml"}.get(key, key)
        require(canonical.get(alias) == value, "GR-049", f"Data Center não aponta para {value}.")

    fingerprints = datacenter.get("conversation_contract_fingerprints") or {}
    require(fingerprints.get("prompt_master_sha256") == sha256_file(paths["prompt"]),
            "GR-046", "SHA-256 do Prompt Mestre não confere.")
    require(fingerprints.get("bootstrap_prompt_sha256") == sha256_file(paths["bootstrap_prompt"]),
            "GR-046", "SHA-256 do prompt de bootstrap não confere.")
    require(fingerprints.get("memory_immutable_contract_sha256") == sha256_object(immutable),
            "GR-047", "hash do immutable_contract da memória não confere.")
    require(fingerprints.get("conversation_contract_script_sha256") == sha256_file(paths["script"]),
            "GR-048", "SHA-256 do script de contrato não confere.")

    prod = datasheet.get("production_contract") or {}
    require(prod.get("pipeline_id") == pipeline.get("pipeline_id"), "GR-046", "Data Sheet aponta pipeline incorreto.")
    require(prod.get("prompt_master_id") == immutable.get("prompt_master_id"), "GR-046", "Prompt Master ID divergente.")
    require(prod.get("memory_id") == memory.get("memory_id"), "GR-047", "Data Sheet não está ligado à memória compartilhada.")
    require(prod.get("conversation_contract_script") == "pipeline/conversation_contract.py", "GR-048", "script de contrato não registrado.")

    command_contract = pipeline.get("conversation_commands") or {}
    require(command_contract.get("/explaincode", {}).get("mode") == "READ_ONLY", "GR-048", "/explaincode sem modo READ_ONLY.")
    require(command_contract.get("/refactor", {}).get("mode") == "BEHAVIOR_PRESERVING_WRITE", "GR-048", "/refactor sem contrato behavior-preserving.")

    dc_panels, ds_panels, tpl_panels = datacenter.get("panels") or {}, datasheet.get("panels") or {}, template.get("panels") or {}
    for panel_id in ("PN-AUT-01", "PN-AUT-02"):
        require(panel_id in dc_panels and panel_id in ds_panels and panel_id in tpl_panels,
                "GR-049", f"{panel_id} não está presente nos três registros.")
        dc, ds, tpl = dc_panels[panel_id], ds_panels[panel_id], tpl_panels[panel_id]
        require(dc.get("li_id") == ds.get("li_id"), "GR-042", f"{panel_id}: li_id divergente.")
        require(dc.get("image_template_id") == ds.get("image_template_id") == tpl.get("image_template_id"),
                "GR-044", f"{panel_id}: image_template_id divergente.")
        require(ds.get("hmi", {}).get("surface") == "door", "GR-037", f"{panel_id}: IHM fora da porta.")

    mutable = memory.get("mutable_state") or {}
    return {
        "status": "PASS",
        "memory_id": memory.get("memory_id"),
        "pipeline_id": pipeline.get("pipeline_id"),
        "standard_id": pipeline.get("standard_id"),
        "prompt_master_id": immutable.get("prompt_master_id"),
        "sync_revision": mutable.get("sync_revision"),
        "branch": (mutable.get("repository") or {}).get("branch"),
        "pull_request": (mutable.get("repository") or {}).get("pull_request"),
        "active_panels": {
            p: {
                "li_id": dc_panels[p].get("li_id"),
                "li_revision": dc_panels[p].get("li_revision"),
                "li_status": dc_panels[p].get("li_status"),
            }
            for p in ("PN-AUT-01", "PN-AUT-02")
        },
    }


def parse_command(text: str) -> tuple[str, str]:
    parts = shlex.split(text, posix=True)
    require(bool(parts), "GR-048", "comando vazio.")
    command = parts[0]
    require(command in {"/explaincode", "/refactor"}, "GR-048", f"comando não suportado: {command}")
    target = " ".join(parts[1:]).strip()
    require(bool(target), "GR-048", f"{command} exige arquivo ou trecho-alvo.")
    return command, target


def dispatch(root: Path, text: str) -> dict[str, Any]:
    bootstrap = validate_contract(root)
    command, target = parse_command(text)
    target_norm = target.replace("\\", "/")
    locked = target_norm in LOCKED_PATHS

    if command == "/explaincode":
        return {
            "status": "PASS",
            "command": command,
            "target": target,
            "mode": "READ_ONLY",
            "may_modify_target": False,
            "required_context": ["pipeline", "datacenter", "datasheet", "memory", "golden_rules"],
            "required_sections": [
                "finalidade",
                "visão geral do fluxo",
                "explicação por bloco/função",
                "entradas e saídas",
                "invariantes e Regras de Ouro",
                "riscos/erros possíveis",
                "vínculo com Data Center/Data Sheet/pipeline",
            ],
            "bootstrap": bootstrap,
        }

    return {
        "status": "PASS",
        "command": command,
        "target": target,
        "mode": "BEHAVIOR_PRESERVING_WRITE",
        "behavior_change_allowed": False,
        "locked_target": locked,
        "explicit_authorization_required_before_edit": locked,
        "mandatory_gates": [
            "capture_before_baseline",
            "compile_or_parse",
            "run_regression_tests",
            "python pipeline/conversation_contract.py validate",
            "review_diff_for_behavior_change",
            "update_memory_after_major_pipeline_change",
        ],
        "prohibited": [
            "silent behavior change",
            "unapproved Golden Rules change",
            "unapproved quantity/catalog_id change",
            "unapproved Data Center/Data Sheet mutation",
            "unapproved pipeline sequence change",
        ],
        "bootstrap": bootstrap,
    }


def sync_memory(root: Path, summary: str, event: str, status: str | None, branch: str | None, head_sha: str | None) -> dict[str, Any]:
    paths = project_paths(root)
    memory = load_yaml(paths["memory"])
    immutable_before = sha256_object(memory.get("immutable_contract") or {})
    mutable = memory.setdefault("mutable_state", {})
    mutable["sync_revision"] = int(mutable.get("sync_revision", 0)) + 1
    mutable["last_sync_at"] = datetime.now().astimezone().replace(microsecond=0).isoformat()
    repo = mutable.setdefault("repository", {})
    if branch:
        repo["branch"] = branch
    if head_sha:
        repo["head_sha"] = head_sha
    if status:
        mutable.setdefault("active_work", {})["status"] = status
    history = memory.setdefault("history", [])
    history.append({
        "revision": mutable["sync_revision"],
        "at": mutable["last_sync_at"],
        "actor": "user+assistant",
        "event": event,
        "summary": summary,
    })
    require(sha256_object(memory.get("immutable_contract") or {}) == immutable_before,
            "GR-047", "tentativa de alterar immutable_contract durante sync.")
    save_yaml(paths["memory"], memory)
    return {
        "status": "PASS",
        "memory_id": memory.get("memory_id"),
        "sync_revision": mutable["sync_revision"],
        "last_sync_at": mutable["last_sync_at"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Raiz do bundle/repositório")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    sub.add_parser("bootstrap")
    p_dispatch = sub.add_parser("dispatch")
    p_dispatch.add_argument("--text", required=True)
    p_sync = sub.add_parser("sync")
    p_sync.add_argument("--summary", required=True)
    p_sync.add_argument("--event", default="CONTEXT_SYNC")
    p_sync.add_argument("--status")
    p_sync.add_argument("--branch")
    p_sync.add_argument("--head-sha")

    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        if args.cmd in {"validate", "bootstrap"}:
            result = validate_contract(root)
        elif args.cmd == "dispatch":
            result = dispatch(root, args.text)
        else:
            validate_contract(root)
            result = sync_memory(root, args.summary, args.event, args.status, args.branch, args.head_sha)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, ContractError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"REPROVADO: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
