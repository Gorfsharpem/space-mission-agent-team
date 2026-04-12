"""
Session State
-------------
Persists the current mission baseline so that when you start from
any agent, the rest of the team has the existing context to work from.

Saved as JSON in outputs/session_state.json
"""

from __future__ import annotations
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime


SESSION_FILE = "outputs/session_state.json"


@dataclass
class SessionState:
    mission_name: str = "UNNAMED-MISSION"
    business_objective: str = ""
    phase: str = "INIT"           # INIT / PHASE_0 / PHASE_A / PHASE_B / PHASE_C / PHASE_D
    last_milestone: str = ""
    results: dict[str, str] = field(default_factory=dict)  # section title → content
    change_log: list[dict] = field(default_factory=list)   # list of CR dicts
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def save(self, path: str = SESSION_FILE):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls, path: str = SESSION_FILE) -> "SessionState":
        if not os.path.isfile(path):
            return cls()
        with open(path) as f:
            data = json.load(f)
        return cls(**data)

    def get_context(self, sections: list[str] | None = None) -> str:
        """Return selected or all results as a markdown context string."""
        items = self.results.items() if sections is None else (
            (k, self.results[k]) for k in sections if k in self.results
        )
        parts = [f"### {k}\n\n{v}" for k, v in items]
        return "\n\n---\n\n".join(parts)

    def update(self, section: str, content: str):
        self.results[section] = content
        self.last_updated = datetime.utcnow().isoformat()

    def add_change(self, cr_dict: dict):
        self.change_log.append(cr_dict)
        self.last_updated = datetime.utcnow().isoformat()

    def summary(self) -> str:
        lines = [
            f"Mission:   {self.mission_name}",
            f"Phase:     {self.phase}",
            f"Milestone: {self.last_milestone or 'none'}",
            f"Sections:  {len(self.results)} documents in baseline",
            f"Changes:   {len(self.change_log)} CRs logged",
            f"Updated:   {self.last_updated[:19]}",
        ]
        return "\n".join(lines)
