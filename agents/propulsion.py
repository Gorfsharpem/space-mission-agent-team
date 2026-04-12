"""
Propulsion Agent
----------------
Designs the spacecraft propulsion subsystem for orbit raising,
station-keeping, attitude control, and disposal.
"""

from agents.base_agent import BaseAgent


class PropulsionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Propulsion Engineer",
            role="Propulsion Subsystem Engineer",
            expertise=(
                "Chemical propulsion (monopropellant hydrazine, bipropellant), "
                "electric propulsion (Hall-effect thrusters, ion engines, cold gas), "
                "delta-V budgeting, thruster sizing, propellant mass (Tsiolkovsky), "
                "tank design and COPV, feed system architecture, "
                "contamination and plume impingement analysis, REACH/ESA propellant compliance."
            ),
        )

    def design_propulsion(self, context: str) -> str:
        # Query mission analysis agent for delta-V budget if network is available
        dv_info = ""
        if self.network and "Mission Analyst" in self.network:
            dv_info = self.ask_agent(
                "Mission Analyst",
                "Please provide the delta-V budget breakdown for all mission phases "
                "(orbit insertion, station-keeping, disposal) that I need for propulsion sizing.",
                context,
            )

        full_context = context
        if dv_info:
            full_context += f"\n\n### Delta-V inputs from Mission Analyst\n\n{dv_info}"

        task = (
            "Produce the Propulsion Subsystem Preliminary Design output.\n\n"
            "Include:\n"
            "1. **Propulsion Trade** — chemical vs electric vs cold gas, "
            "selection rationale based on delta-V, timeline, and mass constraints\n"
            "2. **Thruster Selection** — type, thrust level (N or mN), Isp (s), "
            "heritage/TRL, supplier\n"
            "3. **Delta-V Budget** — itemised table: orbit insertion, station-keeping "
            "(annual + total lifetime), attitude control, disposal — with 10% margin\n"
            "4. **Propellant Mass** — Tsiolkovsky calculation, propellant type and mass (kg)\n"
            "5. **Tank & Feed System** — tank volume (L), material, pressurant or blowdown, "
            "valve and filter architecture\n"
            "6. **Plume Impingement** — risk assessment on solar arrays and payload, "
            "thruster placement rationale\n"
            "7. **Mass & Power** — total propulsion system mass (kg) and power (W)\n"
            "8. **Propulsion Risks** — leaks, thruster failure, contamination, mitigation\n"
        )
        return self.run(task, context=full_context)
