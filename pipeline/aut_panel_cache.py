#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CACHE_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class CacheLookup:
    status: str
    key: str
    path: str
    payload: dict[str, Any] | None


class ContentAddressedCache:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def _path(self, key: str) -> Path:
        if len(key) != 64 or any(c not in "0123456789abcdef" for c in key.lower()):
            raise ValueError("cache key must be a SHA-256 hex digest")
        return self.root / key[:2] / f"{key}.json"

    def lookup(self, key: str) -> CacheLookup:
        path = self._path(key)
        if not path.is_file():
            return CacheLookup("MISS", key, str(path), None)
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return CacheLookup("INVALID", key, str(path), None)
        if data.get("cache_key") != key or data.get("schema_version") != CACHE_SCHEMA_VERSION:
            return CacheLookup("INVALID", key, str(path), data)
        return CacheLookup("HIT", key, str(path), data)

    def store(
        self,
        *,
        key: str,
        material: dict[str, Any],
        result: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": CACHE_SCHEMA_VERSION,
            "cache_key": key,
            "material": material,
            "result": result,
            "metadata": metadata or {},
        }
        tmp = path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp.replace(path)
        return path

    def invalidate(self, key: str) -> bool:
        path = self._path(key)
        if not path.exists():
            return False
        path.unlink()
        parent = path.parent
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
        return True
