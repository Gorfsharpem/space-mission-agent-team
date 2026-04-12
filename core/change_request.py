"""
Change Request
--------------
Typed representation of any requirement change in the mission.
Raised by any agent or by the user (business layer).

severity levels:
  CRITICAL  — affects mission feasibility or top-level requirements
  MAJOR     — affects one or more subsystem designs significantly
  MINOR     — localised change, limited downstream impact

source_type:
  BUSINESS       — new/changed business objective or user requirement
  SYSTEM         — system-level requirement change (Mission Director)
  SUBSYSTEM      — subsystem-initiated change (e.g. Propulsion can't meet delta-V)
  INTERFACE      — interface incompatibility discovered between two subsystems
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    MAJOR    = "MAJOR"
    MINOR    = "MINOR"


class SourceType(str, Enum):
    BUSINESS   = "BUSINESS"
    SYSTEM     = "SYSTEM"
    SUBSYSTEM  = "SUBSYSTEM"
    INTERFACE  = "INTERFACE"


@dataclass
class ChangeRequest:
    """
    A formal change request raised by any agent or the user.

    Attributes:
        cr_id          : Unique identifier, e.g. CR-001
        raised_by      : Agent name or "User"
        source_type    : Where the change originates
        title          : One-line summary
        description    : Full description of what changed and why
        severity       : CRITICAL / MAJOR / MINOR
        affected_areas : Optional list of subsystems the raiser already knows are affected
        timestamp      : ISO timestamp of creation
        status         : OPEN → IN_REVIEW → RESOLVED / REJECTED
        resolution     : Final decision and rationale (filled by Mission Director)
    """
    cr_id: str
    raised_by: str
    source_type: SourceType
    title: str
    description: str
    severity: Severity
    affected_areas: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "OPEN"
    resolution: Optional[str] = None

    def to_markdown(self) -> str:
        lines = [
            f"## Change Request {self.cr_id}",
            f"**Raised by:** {self.raised_by}  ",
            f"**Type:** {self.source_type.value}  ",
            f"**Severity:** {self.severity.value}  ",
            f"**Status:** {self.status}  ",
            f"**Timestamp:** {self.timestamp}  ",
            f"\n### Title\n{self.title}",
            f"\n### Description\n{self.description}",
        ]
        if self.affected_areas:
            lines.append(f"\n### Initially flagged areas\n" + ", ".join(self.affected_areas))
        if self.resolution:
            lines.append(f"\n### Resolution\n{self.resolution}")
        return "\n".join(lines)
