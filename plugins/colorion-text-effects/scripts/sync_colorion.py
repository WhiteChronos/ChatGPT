#!/usr/bin/env python3
"""Synchronize the local Colorion effect catalog from the official upstream.

Uses Python's standard library only. By default it downloads effects.ts from the
official GitHub raw URL. For reproducible/offline tests, pass --effects-file.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
import urllib.request

DEFAULT_URL = "https://raw.githubusercontent.com/ckissi/colorion-text-effects/main/src/data/effects.ts"

EFFECT_RE = re.compile(
    r"\{\s*index:\s*'(?P<index>\d+)'\s*,\s*"
    r"name:\s*'(?P<name>(?:\\'|[^'])*)'\s*,\s*"
    r"type:\s*'(?P<type>(?:\\'|[^'])*)'\s*,\s*"
    r"text:\s*'(?P<text>(?:\\'|[^'])*)'\s*,?\s*\}",
    re.DOTALL,
)

SET_RE_TEMPLATE = r"export const {name} = new Set<EffectType>\(\[(?P<body>.*?)\]\);"
STRING_RE = re.compile(r"'((?:\\'|[^'])*)'")


def _decode_ts_string(value: str) -> str:
    mapping = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", "'": "'"}

    def repl(match: re.Match[str]) -> str:
        token = match.group(1)
        if token.startswith("u"):
            return chr(int(token[1:], 16))
        return mapping.get(token, token)

    return re.sub(r"\\(u[0-9a-fA-F]{4}|n|r|t|\\|')", repl, value)


def parse_effects(source: str) -> dict:
    effects = []
    for m in EFFECT_RE.finditer(source):
        effects.append(
            {
                "index": m.group("index"),
                "name": _decode_ts_string(m.group("name")),
                "type": _decode_ts_string(m.group("type")),
                "text": _decode_ts_string(m.group("text")),
            }
        )

    if not effects:
        raise ValueError("No effects were parsed from effects.ts")

    def parse_set(name: str) -> list[str]:
        m = re.search(SET_RE_TEMPLATE.format(name=re.escape(name)), source, re.DOTALL)
        if not m:
            return []
        return [_decode_ts_string(x) for x in STRING_RE.findall(m.group("body"))]

    per_letter = set(parse_set("perLetter"))
    data_text = set(parse_set("usesDataText"))

    for effect in effects:
        effect["markup_mode"] = (
            "svg" if effect["type"] == "contour"
            else "special" if effect["type"] == "decoder"
            else "per-letter" if effect["type"] in per_letter
            else "data-text" if effect["type"] in data_text
            else "plain"
        )

    return {
        "source": DEFAULT_URL,
        "synced_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "effect_count": len(effects),
        "effects": effects,
        "per_letter_types": sorted(per_letter),
        "data_text_types": sorted(data_text),
    }


def read_source(url: str, effects_file: str | None) -> str:
    if effects_file:
        return pathlib.Path(effects_file).read_text(encoding="utf-8")
    request = urllib.request.Request(url, headers={"User-Agent": "colorion-text-effects-skill/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="Raw effects.ts URL")
    parser.add_argument("--effects-file", help="Parse a local effects.ts instead of downloading")
    parser.add_argument(
        "--output",
        default=str(pathlib.Path(__file__).resolve().parents[1] / "references" / "effects-catalog.json"),
        help="Catalog JSON output path",
    )
    args = parser.parse_args()

    try:
        source = read_source(args.url, args.effects_file)
        payload = parse_effects(source)
        payload["source"] = args.url
        payload["source_mode"] = "local-file" if args.effects_file else "download"
        output = pathlib.Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {payload['effect_count']} effects to {output}")
        return 0
    except Exception as exc:
        print(f"sync failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
