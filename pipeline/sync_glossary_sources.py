from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "datacenter" / "GLOSSARY_SOURCES.json"
STATE = ROOT / "datacenter" / "GLOSSARY_SOURCE_STATE.json"
CANDIDATES = ROOT / "datacenter" / "GLOSSARY_CANDIDATES.json"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def github_json(url: str) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "WhiteChronos-GlossaryEngine/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    registry = load_json(REGISTRY, {"sources": []})
    previous = load_json(STATE, {"sources": {}})
    candidates = load_json(CANDIDATES, {"items": []})
    old_map = previous.get("sources", {})
    items = candidates.get("items", [])
    now = datetime.now(timezone.utc).isoformat()
    new_map: dict[str, Any] = {}
    failures: list[str] = []

    for source in registry.get("sources", []):
        if not source.get("enabled", True):
            continue
        source_id = source["id"]
        repo = source["repository"]
        branch = source.get("default_branch", "main")
        url = f"https://api.github.com/repos/{repo}/commits/{branch}"
        try:
            commit = github_json(url)
            sha = commit["sha"]
            html_url = commit.get("html_url", "")
            previous_sha = old_map.get(source_id, {}).get("sha")
            changed = bool(previous_sha and previous_sha != sha)
            new_map[source_id] = {
                "repository": repo,
                "branch": branch,
                "sha": sha,
                "commit_url": html_url,
                "checked_at": now,
                "changed_since_previous_check": changed,
            }
            if changed:
                candidate_id = f"{source_id}:{sha}"
                if not any(x.get("candidate_id") == candidate_id for x in items):
                    items.append(
                        {
                            "candidate_id": candidate_id,
                            "source_id": source_id,
                            "repository": repo,
                            "from_sha": previous_sha,
                            "to_sha": sha,
                            "detected_at": now,
                            "status": "PENDING_TECHNICAL_REVIEW",
                            "auto_promote": False,
                            "note": "Mudança upstream detectada. Revisar impacto no glossário; não promover automaticamente conteúdo normativo/técnico.",
                        }
                    )
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
            failures.append(f"{source_id}: {exc}")
            if source_id in old_map:
                new_map[source_id] = old_map[source_id]
                new_map[source_id]["last_check_error"] = str(exc)
                new_map[source_id]["checked_at"] = now

    write_json(
        STATE,
        {
            "schema_version": "1.0",
            "checked_at": now,
            "ok": not failures,
            "failures": failures,
            "sources": new_map,
        },
    )
    write_json(
        CANDIDATES,
        {
            "schema_version": "1.0",
            "updated_at": now,
            "items": items,
        },
    )

    if failures:
        for failure in failures:
            print(f"SOURCE_SYNC_WARNING: {failure}")
    print("GLOSSARY_SOURCE_SYNC_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
