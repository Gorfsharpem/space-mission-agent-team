"""
Structures & Mechanisms Agent
------------------------------
Designs the spacecraft primary structure, configuration, and mechanisms.
"""

from agents.base_agent import BaseAgent


class StructuresAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Structures Engineer",
            role="Structures & Mechanisms Engineer",
            expertise=(
                "Spacecraft structural design, launch load analysis, "
                "finite element analysis (FEA), material selection (CFRP, aluminium alloys, titanium), "
                "modal analysis, acoustic and vibration environments, "
                "mechanisms (solar array deployment, antenna pointing), "
                "mass properties, and configuration design."
            ),
        )

    def design_structures(self, context: str) -> str:
        task = (
            "Produce the Structures & Mechanisms Preliminary Design output.\n\n"
            "Include:\n"
            "1. **Configuration Concept** — spacecraft layout description and rationale, "
            "with key dimensions (mm) and coordinate frame definition\n"
            "2. **Structural Architecture** — primary load-bearing concept (central tube, panel, truss, etc.) "
            "and material selection\n"
            "3. **Launch Load Analysis** — quasi-static load factors from launcher user manual, "
            "preliminary stress estimates\n"
            "4. **Mass Budget** — component-level mass table with contingency, "
            "total wet and dry mass (kg), and mass margin\n"
            "5. **Centre of Mass & Inertia** — preliminary CoM location and moments of inertia\n"
            "6. **Mechanisms** — list of all deployment/pointing mechanisms with heritage/TRL\n"
            "7. **Accommodation** — how all subsystems fit; any conflicts or tight packaging areas\n"
            "8. **Structural Risks** — frequency conflicts, mechanism reliability, mitigation\n"
        )
        return self.run(task, context=context)
