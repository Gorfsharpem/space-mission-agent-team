"""
Impact Map
----------
Static dependency graph of the mission team.

When a change is raised by agent X, the Impact Map answers:
  "Which other agents are downstream of X and must review this change?"

The graph is DIRECTED: A → B means "a change in A has direct impact on B."
Transitive impacts are resolved automatically.

This is the core of the change propagation strategy.
"""

from __future__ import annotations

# fmt: off
DEPENDENCY_GRAPH: dict[str, list[str]] = {
    # ── Business / top-level ──────────────────────────────────────────────
    # A change to the business objective or user requirements touches everything.
    "User": [
        "Project Manager", "Mission Director", "Mission Analyst",
        "Bid Manager", "Proposal Manager", "R&D Manager",
    ],
    "Project Manager": [
        "Mission Director", "Project Controller", "Document Manager",
        "Proposal Manager", "Bid Manager",
    ],

    # ── Systems engineering ───────────────────────────────────────────────
    # A system requirement change by the Mission Director cascades to all subsystems.
    "Mission Director": [
        "Mission Analyst", "Payload Engineer", "EPS Engineer", "ADCS Engineer",
        "Thermal Engineer", "Structures Engineer", "Propulsion Engineer",
        "Mechanical Engineer", "Electrical Engineer", "Antenna Engineer",
        "TT&C Engineer", "OBSW Engineer", "QA/PA Engineer", "Project Controller",
    ],

    # ── Mission analysis ──────────────────────────────────────────────────
    # Orbit / launch / delta-V changes cascade to propulsion, power, thermal, ADCS.
    "Mission Analyst": [
        "Propulsion Engineer", "EPS Engineer", "ADCS Engineer",
        "Thermal Engineer", "TT&C Engineer", "Structures Engineer",
    ],

    # ── Payload ──────────────────────────────────────────────────────────
    # Payload changes drive power, data, pointing, thermal, downlink, and structure.
    "Payload Engineer": [
        "EPS Engineer", "ADCS Engineer", "Thermal Engineer",
        "Structures Engineer", "TT&C Engineer", "Antenna Engineer",
        "OBSW Engineer", "Mechanical Engineer",
    ],

    # ── Propulsion ───────────────────────────────────────────────────────
    # Thruster / propellant changes affect mass, power, thermal, pointing disturbances.
    "Propulsion Engineer": [
        "Structures Engineer", "Thermal Engineer", "EPS Engineer",
        "ADCS Engineer", "Mechanical Engineer",
    ],

    # ── EPS ──────────────────────────────────────────────────────────────
    # Power budget changes affect every power consumer; harness affects electrical + mechanical.
    "EPS Engineer": [
        "Structures Engineer", "Thermal Engineer", "Electrical Engineer",
        "Mechanical Engineer", "OBSW Engineer",
    ],

    # ── ADCS ─────────────────────────────────────────────────────────────
    # Attitude change affects mechanical mounting, power, software, and propulsion (desaturation).
    "ADCS Engineer": [
        "Structures Engineer", "Mechanical Engineer", "EPS Engineer",
        "OBSW Engineer", "Propulsion Engineer",
    ],

    # ── Thermal ──────────────────────────────────────────────────────────
    # Heater power changes affect EPS; structural changes affect MLI accommodation.
    "Thermal Engineer": [
        "EPS Engineer", "Structures Engineer", "Mechanical Engineer",
    ],

    # ── Structures ───────────────────────────────────────────────────────
    # Configuration or mass changes affect mechanical, thermal (MLI areas), and propulsion sizing.
    "Structures Engineer": [
        "Mechanical Engineer", "Thermal Engineer", "Propulsion Engineer",
        "EPS Engineer",
    ],

    # ── TT&C ─────────────────────────────────────────────────────────────
    # Frequency or data rate changes drive antenna redesign, OBSW, and electrical.
    "TT&C Engineer": [
        "Antenna Engineer", "OBSW Engineer", "Electrical Engineer",
    ],

    # ── Mechanical ───────────────────────────────────────────────────────
    # Harness routing changes affect electrical; mechanism changes affect structures.
    "Mechanical Engineer": [
        "Electrical Engineer", "Structures Engineer",
    ],

    # ── Electrical ───────────────────────────────────────────────────────
    # Grounding / EMC changes affect OBSW (data bus shielding) and TT&C (RF environment).
    "Electrical Engineer": [
        "OBSW Engineer", "TT&C Engineer",
    ],

    # ── Antenna ──────────────────────────────────────────────────────────
    # Antenna mass/volume change affects structures; RF environment affects electrical.
    "Antenna Engineer": [
        "Structures Engineer", "Electrical Engineer",
    ],

    # ── OBSW ─────────────────────────────────────────────────────────────
    # Software interface changes affect TT&C and ADCS command handling.
    "OBSW Engineer": [
        "TT&C Engineer", "ADCS Engineer",
    ],

    # ── QA/PA ─────────────────────────────────────────────────────────────
    # QA findings cascade back to Mission Director for disposition.
    "QA/PA Engineer": [
        "Mission Director", "Project Controller", "Document Manager",
    ],

    # ── Business dev agents ───────────────────────────────────────────────
    "Proposal Manager": [
        "Bid Manager", "Project Controller",
    ],
    "Bid Manager": [
        "Project Controller", "Project Manager",
    ],
    "R&D Manager": [
        "Proposal Manager", "Mission Director",
    ],
    "Project Controller": [
        "Project Manager", "Document Manager",
    ],
    "Document Manager": [],

    # ── Safety Engineer ───────────────────────────────────────────────────
    # Safety findings cascade to all subsystems and Mission Director.
    "Safety Engineer": [
        "Mission Director", "QA/PA Engineer", "Propulsion Engineer",
        "OBSW Engineer", "Structures Engineer", "Ground Segment Engineer",
    ],

    # ── Ground Segment Engineer ───────────────────────────────────────────
    # Ground segment changes affect TT&C, OBSW, and operations planning.
    "Ground Segment Engineer": [
        "TT&C Engineer", "OBSW Engineer", "Mission Director",
    ],

    # ── Launch Campaign Manager ───────────────────────────────────────────
    # Launch campaign changes affect structures (LV interface), propulsion (fuelling).
    "Launch Campaign Manager": [
        "Structures Engineer", "Propulsion Engineer", "Mission Analyst",
        "Ground Segment Engineer",
    ],

}
# fmt: on


class ImpactMap:
    """
    Resolves which agents are affected (directly or transitively)
    by a change originating from a given source agent.
    """

    def __init__(self):
        self._graph = DEPENDENCY_GRAPH

    def direct_impacts(self, source: str) -> list[str]:
        return self._graph.get(source, [])

    def all_impacts(self, source: str, max_depth: int = 3) -> list[str]:
        """
        BFS to find all transitively affected agents, up to max_depth hops.
        Returns them in order: direct impacts first, then second-order, etc.
        Deduplicates and excludes the source itself.
        """
        visited: set[str] = set()
        queue: list[tuple[str, int]] = [(source, 0)]
        ordered: list[str] = []

        while queue:
            node, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            for neighbour in self._graph.get(node, []):
                if neighbour not in visited and neighbour != source:
                    visited.add(neighbour)
                    ordered.append(neighbour)
                    queue.append((neighbour, depth + 1))

        return ordered

    def impact_summary(self, source: str) -> str:
        direct = self.direct_impacts(source)
        all_imp = self.all_impacts(source)
        second = [a for a in all_imp if a not in direct]
        lines = [
            f"**Direct impacts** from `{source}`: {', '.join(direct) if direct else 'none'}",
            f"**Transitive impacts**: {', '.join(second) if second else 'none'}",
        ]
        return "\n".join(lines)
