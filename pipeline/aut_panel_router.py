#!/usr/bin/env python3
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

ROUTES = {
    "research": "TECHNICAL_RESEARCH",
    "source_validation": "SOURCE_VALIDATOR_A",
    "normative": "NORMATIVE",
    "datacenter": "DATACENTER_CURATOR",
    "electrical_sizing": "ELECTRICAL_SIZING",
    "automation_io": "AUTOMATION_IO",
    "li_bom": "LI_BOM",
    "layout": "LAYOUT_OPTIMIZER",
    "render": "RENDERER",
    "qa": "QA",
    "memory": "MEMORY_CURATOR",
    "ml_quality": "ML_QUALITY",
    "evolution": "EVOLUTION_PROPOSER",
}

ALIASES = {
    "pesquisa": "research",
    "pesquisa tecnica": "research",
    "fonte": "source_validation",
    "validacao de fonte": "source_validation",
    "norma": "normative",
    "normativa": "normative",
    "dimensionamento": "electrical_sizing",
    "io": "automation_io",
    "i o": "automation_io",
    "clp": "automation_io",
    "automacao": "automation_io",
    "li": "li_bom",
    "bom": "li_bom",
    "lista de material": "li_bom",
    "layout": "layout",
    "render": "render",
    "imagem": "render",
    "qa": "qa",
    "qualidade": "qa",
    "memoria": "memory",
    "ml": "ml_quality",
    "evolucao": "evolution",
}


@dataclass(frozen=True)
class RouteDecision:
    intent: str
    agent: str
    mode: str
    confidence: float
    reasons: tuple[str, ...]


def _normalize(text: str) -> str:
    raw = unicodedata.normalize("NFKD", str(text))
    raw = "".join(ch for ch in raw if not unicodedata.combining(ch))
    raw = raw.lower().replace("_", " ").replace("/", " ")
    return " ".join(re.findall(r"[a-z0-9]+", raw))


def _contains_phrase(corpus: str, phrase: str) -> bool:
    hay = f" {corpus} "
    needle = f" {_normalize(phrase)} "
    return needle in hay


def route_intent(intent: str, hints: Iterable[str] = ()) -> RouteDecision:
    raw = _normalize(intent)
    hint_text = " ".join(_normalize(x) for x in hints)
    corpus = f"{raw} {hint_text}".strip()

    direct = raw.replace(" ", "_")
    if direct in ROUTES:
        return RouteDecision(direct, ROUTES[direct], "DETERMINISTIC", 1.0, ("exact_intent",))

    scores: dict[str, int] = {k: 0 for k in ROUTES}
    matched: dict[str, list[str]] = {k: [] for k in ROUTES}
    for phrase, target in ALIASES.items():
        if _contains_phrase(corpus, phrase):
            scores[target] += 1
            matched[target].append(phrase)

    best = max(scores.values(), default=0)
    winners = sorted(k for k, v in scores.items() if v == best and v > 0)

    if len(winners) == 1:
        key = winners[0]
        confidence = min(0.95, 0.70 + 0.05 * best)
        reasons = tuple(f"keyword:{x}" for x in matched[key]) or ("keyword_match",)
        return RouteDecision(key, ROUTES[key], "DETERMINISTIC", confidence, reasons)

    return RouteDecision(
        intent="ambiguous",
        agent="ORCHESTRATOR",
        mode="ML_ROUTE_HINT",
        confidence=0.0,
        reasons=("no_unique_deterministic_route",),
    )
