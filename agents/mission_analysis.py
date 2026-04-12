"""
Mission Analysis & Astrodynamics Agent
---------------------------------------
Defines the mission orbit, launch profile, coverage, and lifetime.
"""

from agents.base_agent import BaseAgent


class MissionAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Mission Analyst",
            role="Mission Analysis & Astrodynamics Engineer",
            expertise=(
                "Orbital mechanics, launch vehicle selection, delta-V budgets, "
                "orbit propagation (SGP4, numerical), ground coverage analysis, "
                "link geometry, eclipse/sunlight fractions, lifetime analysis, "
                "re-entry and disposal strategies, and GMAT/STK/Orekit tooling."
            ),
        )

    def run_mission_analysis(self, context: str) -> str:
        task = (
            "Perform the preliminary Mission Analysis and produce a Mission Analysis Report (MAR).\n\n"
            "Include:\n"
            "1. **Orbit Selection** — recommended orbit type (LEO/MEO/GEO/HEO/interplanetary) with trade rationale\n"
            "2. **Orbital Parameters** — altitude, inclination, RAAN, eccentricity, period\n"
            "3. **Launch Vehicle Trade** — 2–3 candidate launchers, selection rationale\n"
            "4. **Delta-V Budget** — all manoeuvres including margins\n"
            "5. **Coverage Analysis** — revisit time, ground station visibility windows\n"
            "6. **Eclipse & Sun Fractions** — worst-case eclipse duration and beta angle range\n"
            "7. **Mission Lifetime & Disposal** — design lifetime and end-of-life strategy\n"
            "8. **Key Astrodynamics Risks** — perturbations, conjunction risks, etc.\n"
        )
        return self.run(task, context=context)
