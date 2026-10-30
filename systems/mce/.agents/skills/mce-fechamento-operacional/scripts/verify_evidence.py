#!/usr/bin/env python3
"""Read-only evidence inventory verifier for the independent MCE.

Verifies bytes against caller-provided expected SHA-256 values. No signature,
review, engineering release, model approval, FAT/SAT or production is implied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
MAX_FILES = 512
MAX_FILE_SIZE = 32 * 1024 * 1024
MAX_TOTAL_SIZE = 160 * 1024 * 1024


def blocked(reason: str, checked: int = 0) -> dict:
    return {
        "product": "MCE_INDEPENDENTE",
        "status": "BLOCKED",
        "files_verified": checked,
        "production_complete": False,
        "external_gates": {
            "github_merge_and_ci": "EXTERNAL_VERIFICATION_REQUIRED",
            "official_model_and_project": "USER_ACTION_REQUIRED",
            "engineering_acceptance": "USER_ACTION_REQUIRED",
            "fat_sat_and_rollback": "USER_ACTION_REQUIRED",
        },
        "reason": reason,
        "note": "File hashes are not engineering approval or a trusted signature.",
    }


def _valid_path(path: str) -> bool:
    if not isinstance(path, str) or not path or "\\" in path:
        return False
    if path.startswith("/") or path.startswith("./") or "//" in path:
        return False
    parts = path.split("/")
    if any(p in ("", ".", "..") for p in parts):
        return False
    return PurePosixPath(path).as_posix() == path


def assess(root: Path, manifest: dict) -> dict:
    """Fail closed; never write files or infer production acceptance."""
    report = blocked("Evidence not verified")
    try:
        root = Path(root)
        if not root.is_dir() or root.is_symlink():
            raise ValueError("Root must be an existing non-symlink directory")
        if not isinstance(manifest, dict) or manifest.get("product") != "MCE_INDEPENDENTE":
            raise ValueError("Wrong evidence product or format")
        files = manifest.get("files")
        if not isinstance(files, list) or not 1 <= len(files) <= MAX_FILES:
            raise ValueError("Nonempty bounded evidence inventory required")
        known = set()
        total = 0
        for item in files:
            if not isinstance(item, dict):
                raise ValueError("Invalid evidence item")
            rel = item.get("path")
            digest = item.get("sha256")
            if not _valid_path(rel) or not isinstance(digest, str) or not SHA256.fullmatch(digest):
                raise ValueError("Invalid relative path or SHA-256")
            if rel in known:
                raise ValueError("Repeated evidence item")
            known.add(rel)
            current = root
            for part in rel.split("/"):
                current = current / part
                if current.is_symlink():
                    raise ValueError("Symlink in evidence path is forbidden")
            if not current.is_file():
                raise ValueError("Evidence file is unavailable")
            size = current.stat().st_size
            if size > MAX_FILE_SIZE or total + size > MAX_TOTAL_SIZE:
                raise ValueError("Evidence size exceeds policy")
            total += size
            hasher = hashlib.sha256()
            with current.open("rb") as file:
                for chunk in iter(lambda: file.read(262144), b""):
                    hasher.update(chunk)
            if hasher.hexdigest() != digest.lower():
                raise ValueError("Evidence SHA-256 mismatch")
            report["files_verified"] += 1
        report["status"] = "ARTIFACT_INTEGRITY_PASS"
        report["reason"] = "All files matched caller-supplied hashes (origin not attested)"
    except (ValueError, OSError, TypeError, KeyError) as exc:
        report["status"] = "BLOCKED"
        report["reason"] = str(exc)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        manifest = None
    result = assess(args.root, manifest)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ARTIFACT_INTEGRITY_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
