"""
Electrical Engineer Agent
--------------------------
Responsible for spacecraft electrical architecture, wiring, grounding,
EMC, and electrical integration across all subsystems.
"""

from agents.base_agent import BaseAgent


class ElectricalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Electrical Engineer",
            role="Spacecraft Electrical Systems Engineer",
            expertise=(
                "Spacecraft electrical architecture, grounding and bonding (single-point ground), "
                "EMC/EMI design and testing (ECSS-E-ST-20-07), harness design (AWG sizing, shielding), "
                "connector selection (D-sub, DSUB, MIL-38999), PCB design for space, "
                "signal integrity, electrical power interface design, "
                "ESD protection, and electrical integration and test (EIT)."
            ),
        )

    def design_electrical(self, context: str) -> str:
        # Consult EPS for power bus and distribution details
        eps_info = ""
        if self.network and "EPS Engineer" in self.network:
            eps_info = self.ask_agent(
                "EPS Engineer",
                "Please provide the power bus voltage, current limits per line, "
                "connector interfaces, and any specific grounding requirements "
                "I need for the electrical architecture design.",
                context,
            )

        # Consult OBSW for data bus topology
        obsw_info = ""
        if self.network and "OBSW Engineer" in self.network:
            obsw_info = self.ask_agent(
                "OBSW Engineer",
                "Please confirm the internal data bus topology (SpaceWire, CAN, MIL-1553), "
                "connector types, cable lengths, and signal levels for the electrical harness design.",
                context,
            )

        full_context = context
        if eps_info:
            full_context += f"\n\n### EPS power interface inputs\n\n{eps_info}"
        if obsw_info:
            full_context += f"\n\n### OBSW data bus inputs\n\n{obsw_info}"

        task = (
            "Produce the Electrical Architecture Preliminary Design output.\n\n"
            "Include:\n"
            "1. **Electrical Architecture Overview** — block diagram description: "
            "power distribution paths, data buses, RF signal chains\n"
            "2. **Grounding & Bonding** — grounding philosophy (single-point, chassis), "
            "bonding requirements, lightning/ESD protection strategy\n"
            "3. **Harness Design** — wire gauge sizing per load current, shielding approach, "
            "connector selection, total harness mass estimate (kg)\n"
            "4. **EMC Design** — filtering strategy, cable separation rules, "
            "shielding effectiveness targets, test approach (per ECSS-E-ST-20-07)\n"
            "5. **Power Interface** — interface to EPS: bus voltage, overcurrent protection, "
            "load switch architecture\n"
            "6. **Data Interface** — connector pinout philosophy, signal conditioning, "
            "impedance matching for SpaceWire / CAN\n"
            "7. **EIT Plan** — Electrical Integration and Test sequence, "
            "continuity and isolation testing, functional verification\n"
            "8. **Electrical Risks** — shorts, EMI susceptibility, connector failure, mitigation\n"
        )
        return self.run(task, context=full_context)
