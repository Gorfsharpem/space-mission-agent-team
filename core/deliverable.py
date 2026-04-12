"""
Deliverable
-----------
A typed artifact produced by an agent at a milestone.

Each agent produces deliverables specific to their domain:
  - Mission Analyst  → orbital parameters table, delta-V budget, coverage analysis
  - EPS Engineer     → power budget table, eclipse energy balance
  - Structures       → mass budget table, CoM estimate, launch load check
  - ADCS             → pointing error budget, actuator sizing, desaturation schedule
  - Propulsion       → Tsiolkovsky calculation, propellant budget, tank sizing
  - Thermal          → temperature table (hot/cold), heater power register
  - TT&C             → link budget table, ground contact schedule
  - OBSW             → FDIR tree, memory map, software task list
  - QA/PA            → NCR register, gate review checklist, FMEA extract
  - Project Control  → EVM table, milestone tracker, invoice log
  - Document Manager → DRL, document status dashboard
  - Bid Manager      → cost breakdown, price-to-win table
  - Proposal Manager → compliance matrix, win theme register
  - R&D Manager      → TRL register, portfolio table, technology roadmap
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DeliverableType(str, Enum):
    MARKDOWN   = "markdown"    # prose report, analysis
    TABLE      = "table"       # markdown table (budget, register, log)
    CALCULATION= "calculation" # step-by-step numerical derivation
    CODE       = "code"        # Python / pseudocode / config
    REGISTER   = "register"    # itemised list (NCRs, actions, risks)
    DASHBOARD  = "dashboard"   # multi-section status overview


@dataclass
class Deliverable:
    """
    A single artifact produced by an agent at a specific milestone.
    """
    agent_name: str
    milestone: str
    title: str
    doc_type: DeliverableType
    content: str
    doc_id: str = ""
    revision: str = "A"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_markdown(self) -> str:
        header = "\n".join([
            f"# {self.title}",
            f"**Document ID:** {self.doc_id or 'TBD'}  ",
            f"**Revision:** {self.revision}  ",
            f"**Author:** {self.agent_name}  ",
            f"**Milestone:** {self.milestone}  ",
            f"**Type:** {self.doc_type.value}  ",
            f"**Date:** {self.timestamp[:10]}  ",
            "",
            "---",
            "",
        ])
        return header + self.content

    def filename(self) -> str:
        safe_title = self.title.lower().replace(" ", "_").replace("/", "_")[:50]
        safe_agent = self.agent_name.lower().replace(" ", "_").replace("/", "_")
        return f"{safe_agent}_{safe_title}.md"
