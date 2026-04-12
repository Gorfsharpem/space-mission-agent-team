"""
Safety Engineer Agent
----------------------
Responsible for system safety analysis, hazard identification,
fault tree analysis, and safety case development.
"""

from agents.base_agent import BaseAgent


class SafetyEngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Safety Engineer",
            role="System Safety Engineer",
            expertise=(
                "MIL-STD-882 / ECSS-Q-ST-40 system safety, hazard identification and risk assessment (HIRA), "
                "fault tree analysis (FTA), failure mode effects and criticality analysis (FMECA), "
                "safety case development, software safety (IEC 61508 / DO-178C), "
                "range safety and launch approval, orbital debris mitigation (IADC guidelines), "
                "radiation safety, propellant handling safety, and safety verification."
            ),
        )

    def safety_analysis(self, context: str) -> str:
        task = (
            "Produce the System Safety Analysis for this mission.\n\n"
            "Include:\n"
            "1. **Hazard Identification Register** — table: HAZ-ID | Hazard | Cause | "
            "Effect | Severity (Cat I-IV) | Probability | Risk Level | Mitigation\n"
            "2. **Top-Level Fault Tree** — describe FTA for mission loss event: "
            "top event → intermediate events → basic events with AND/OR gates\n"
            "3. **Safety-Critical Functions** — list of functions whose failure leads to "
            "Cat I/II hazard, with required integrity level\n"
            "4. **Software Safety** — safety-critical software items, required SIL level, "
            "forbidden constructs and verification approach\n"
            "5. **Launch & Range Safety** — propellant toxicity class, "
            "blast exclusion zone estimate, destruct system requirement\n"
            "6. **Orbital Debris Mitigation** — compliance with 25-year rule, "
            "passivation plan (propellant venting, battery discharge), disposal strategy\n"
            "7. **Safety Case Summary** — claim, argument, evidence structure\n"
            "8. **Open Safety Items** — unresolved hazards requiring design action\n"
        )
        return self.run(task, context=context)
