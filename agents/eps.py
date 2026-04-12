"""
Electrical Power System (EPS) Agent
-------------------------------------
Designs the spacecraft power generation, storage, and distribution subsystem.
"""

from agents.base_agent import BaseAgent


class EPSAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="EPS Engineer",
            role="Electrical Power Subsystem Engineer",
            expertise=(
                "Solar array sizing (GaAs, silicon), battery technology (Li-ion, NiH2), "
                "power budget analysis, MPPT and power conditioning, "
                "eclipse/sunlight power balance, harness design, EMC, "
                "and radiation effects on power components."
            ),
        )

    def design_eps(self, context: str) -> str:
        task = (
            "Produce the EPS Preliminary Design output.\n\n"
            "Include:\n"
            "1. **Power Budget** — table of all loads (payload, ADCS, OBC, TT&C, thermal heaters) "
            "with peak and average values, plus 20% margin\n"
            "2. **Solar Array Design** — cell technology, array area (m²), orientation strategy, "
            "worst-case (end-of-life, max eclipse beta angle) power generation\n"
            "3. **Battery Design** — chemistry, capacity (Wh), depth of discharge, "
            "number of cells, estimated mass\n"
            "4. **Power Distribution** — bus voltage, PCU/PDU architecture, protection scheme\n"
            "5. **Eclipse Energy Balance** — can battery sustain the spacecraft through worst-case eclipse?\n"
            "6. **Mass Estimate** — solar array, battery, harness, PDU total mass (kg)\n"
            "7. **EPS Risks** — degradation, single points of failure, mitigation\n"
        )
        return self.run(task, context=context)
