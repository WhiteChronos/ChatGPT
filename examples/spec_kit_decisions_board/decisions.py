"""Dependency-free decision register used by the six-file Spec Kit example."""
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class Decision:
    id: str
    title: str
    rationale: str
    date: str

    def __post_init__(self):
        if not all(isinstance(v, str) and v.strip() for v in (self.id, self.title, self.rationale, self.date)):
            raise ValueError("decision fields must be nonempty strings")
        try:
            date.fromisoformat(self.date)
        except ValueError as exc:
            raise ValueError("date must be ISO YYYY-MM-DD") from exc

class DecisionsBoard:
    def __init__(self):
        self._items = {}

    def add_decision(self, decision: Decision):
        if not isinstance(decision, Decision):
            raise TypeError("decision must be a Decision")
        if decision.id in self._items:
            raise ValueError("duplicate decision ID")
        self._items[decision.id] = decision

    def list_decisions(self):
        return sorted(self._items.values(), key=lambda item: (item.date, item.id))

    def export_markdown(self):
        lines = ["# Decision register", ""]
        for item in self.list_decisions():
            safe = lambda value: value.replace("\n", " ").replace("\r", " ").replace("|", "\\|")
            lines.extend((f"## {safe(item.id)} - {safe(item.title)}", f"Date: {item.date}", f"Rationale: {safe(item.rationale)}", ""))
        return "\n".join(lines)
