from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.build_interactive_glossary import (
    MASTER,
    REGISTRY,
    build_page,
    iter_staging_records,
    load_json,
)

OUTPUT = ROOT / "docs" / "glossario-interativo.md"


def main() -> int:
    master = load_json(MASTER)
    registry = load_json(REGISTRY, {"sources": []})
    staging = iter_staging_records()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_page(master, registry, staging).rstrip() + "\n", encoding="utf-8")
    print(
        "PUBLIC_INTERACTIVE_GLOSSARY_BUILT "
        f"canonical={len(master.get('entries', []))} staging={len(staging)} "
        f"output={OUTPUT.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
