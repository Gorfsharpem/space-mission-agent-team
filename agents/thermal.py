"""
Thermal Control Subsystem (TCS) Agent
--------------------------------------
Designs the spacecraft thermal control architecture.
"""

from agents.base_agent import BaseAgent


class ThermalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Thermal Engineer",
            role="Thermal Control Subsystem Engineer",
            expertise=(
                "Passive and active thermal control, multi-layer insulation (MLI), "
                "thermal coatings (OSR, black paint, Kapton), heat pipes, "
                "louvers, heaters, thermostats, thermal mathematical models (TMM), "
                "finite element thermal analysis, and worst-case hot/cold analysis."
            ),
        )

    def design_thermal(self, context: str) -> str:
        task = (
            "Produce the Thermal Control Preliminary Design output.\n\n"
            "Include:\n"
            "1. **Thermal Environment** — hot case (max solar flux, albedo) and cold case (eclipse, EOL) "
            "boundary conditions\n"
            "2. **Component Temperature Requirements** — table of critical components with "
            "operating and survival temperature limits\n"
            "3. **Thermal Architecture** — passive vs active strategy, overall design concept\n"
            "4. **Passive Elements** — MLI coverage areas, surface coatings, radiator sizing (m²)\n"
            "5. **Active Elements** — heater power (W), thermostat setpoints, heat pipes if needed\n"
            "6. **Worst-Case Analysis** — estimated temperatures for hot and cold cases\n"
            "7. **Mass & Power** — total TCS mass (kg) and heater power budget (W)\n"
            "8. **Thermal Risks** — transient events, shadowing, mitigation\n"
        )
        return self.run(task, context=context)
