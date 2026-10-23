#!/usr/bin/env python3
"""Search the local Colorion catalog by effect name, type, or sample text."""
from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import re


def tokens(text: str) -> set[str]:
    return {x for x in re.split(r"[^a-z0-9]+", text.lower()) if x}


def score(query: str, effect: dict) -> float:
    hay = " ".join(str(effect.get(k, "")) for k in ("index", "name", "type", "text", "markup_mode")).lower()
    q = query.lower().strip()
    if not q:
        return 0.0
    overlap = len(tokens(q) & tokens(hay))
    contains = 2.0 if q in hay else 0.0
    fuzzy = difflib.SequenceMatcher(None, q, hay).ratio()
    return overlap * 3.0 + contains + fuzzy


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="+", help="Search words, e.g. blueprint circuit neon")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--catalog",
        default=str(pathlib.Path(__file__).resolve().parents[1] / "references" / "effects-catalog.json"),
    )
    args = parser.parse_args()

    data = json.loads(pathlib.Path(args.catalog).read_text(encoding="utf-8"))
    query = " ".join(args.query)
    ranked = sorted(((score(query, e), e) for e in data["effects"]), key=lambda x: x[0], reverse=True)
    for s, effect in ranked[: max(args.limit, 1)]:
        print(
            f"{effect['index']}  {effect['name']:<18} type={effect['type']:<12} "
            f"markup={effect.get('markup_mode','?'):<10} sample={effect['text']!r} score={s:.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
