"""
Mechanical Engineer Agent
--------------------------
Responsible for detailed mechanical design, harness routing,
mechanisms, and integration with structures.
"""

from agents.base_agent import BaseAgent


class MechanicalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Mechanical Engineer",
            role="Mechanical Design Engineer",
            expertise=(
                "Detailed mechanical design (CAD: CATIA, SolidWorks), "
                "harness routing and bracket design, thermal strap and heat pipe installation, "
                "mechanism design (hinges, hold-down release, deployable booms), "
                "tolerance stack-up analysis, fastener selection (space-qualified), "
                "surface treatment and coatings, cleanliness and contamination control (ECSS-Q-ST-70)."
            ),
        )

    def design_mechanical(self, context: str) -> str:
        # Consult structures engineer for envelope constraints
        struct_info = ""
        if self.network and "Structures Engineer" in self.network:
            struct_info = self.ask_agent(
                "Structures Engineer",
                "Please provide the structural envelope, panel dimensions, "
                "interface bracket locations, and any keep-out zones I must respect "
                "for detailed mechanical design and harness routing.",
                context,
            )

        full_context = context
        if struct_info:
            full_context += f"\n\n### Structural envelope from Structures Engineer\n\n{struct_info}"

        task = (
            "Produce the Mechanical Design Preliminary Output.\n\n"
            "Include:\n"
            "1. **Mechanical Architecture** — panel layout, bracket design philosophy, "
            "primary attachment philosophy to launch vehicle adapter\n"
            "2. **Harness Routing Plan** — major harness bundles, routing constraints, "
            "estimated harness mass (kg) and volume impact\n"
            "3. **Mechanisms List** — all mechanisms with function, drive type, "
            "latch/release concept, heritage, and TRL\n"
            "4. **Tolerance Stack-Up** — key assembly tolerances, alignment requirements "
            "for payload and antenna\n"
            "5. **Fastener & Joining Strategy** — space-qualified fastener grades, "
            "thread-locking approach, torque specification philosophy\n"
            "6. **Contamination Control Plan** — cleanliness levels (per ECSS-Q-ST-70), "
            "handling, bagging, and storage requirements\n"
            "7. **Interface Control** — mechanical ICDs needed with each subsystem\n"
            "8. **Mechanical Risks** — deployment failures, harness chafing, mitigation\n"
        )
        return self.run(task, context=full_context)
