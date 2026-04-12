"""
Mission Director — Chief Systems Engineer
-----------------------------------------
Orchestrates the engineering team, consolidates subsystem outputs,
resolves interface conflicts, and owns the system-level design baseline.
"""

from agents.base_agent import BaseAgent


class MissionDirectorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Mission Director",
            role="Chief Systems Engineer",
            expertise=(
                "Systems engineering (ECSS standards), requirements management, "
                "trade-off analysis, system budgets (mass, power, data), "
                "interface control, mission lifecycle management (Phase A–E), "
                "risk management, and commissioning planning."
            ),
        )

    def derive_system_requirements(self, mission_context: str) -> str:
        task = (
            "Based on the mission context provided, derive the top-level System Requirements.\n\n"
            "Produce:\n"
            "1. **Mission Requirements** (MIS-XXX) — what the mission must achieve\n"
            "2. **System Requirements** (SYS-XXX) — how the system satisfies mission requirements\n"
            "3. **Key Design Drivers** — the 3–5 most critical constraints shaping the design\n"
            "4. **System Budgets (preliminary)** — mass, power, data rate, pointing\n"
            "5. **Open Items & Risks** — anything that needs resolution before PDR\n"
        )
        return self.run(task, context=mission_context)

    def integration_review(self, all_subsystem_outputs: str) -> str:
        task = (
            "Review all subsystem design outputs and produce a System Integration Review (SIR) report.\n\n"
            "Cover:\n"
            "1. **Interface Matrix** — key interfaces between subsystems (electrical, mechanical, thermal, data)\n"
            "2. **Budget Consolidation** — updated mass, power, and data budgets with margins\n"
            "3. **Design Conflicts & Resolutions** — any contradictions found and how they are resolved\n"
            "4. **System-Level Risks** — top 5 risks with likelihood and impact\n"
            "5. **Recommendation** — go/no-go for PDR with rationale\n"
        )
        return self.run(task, context=all_subsystem_outputs)

    def commissioning_plan(self, integrated_design: str) -> str:
        task = (
            "Generate a high-level Commissioning Plan for the mission.\n\n"
            "Include:\n"
            "1. **Launch & Early Operations (LEOP)** — critical timeline (0–72 hours)\n"
            "2. **In-Orbit Commissioning (IOC) Phases** — phase-by-phase with duration and success criteria\n"
            "3. **Subsystem Commissioning Sequence** — ordered list with dependencies\n"
            "4. **Acceptance Criteria** — what defines a successfully commissioned spacecraft\n"
            "5. **Contingency Scenarios** — top 3 failure cases and mitigation procedures\n"
        )
        return self.run(task, context=integrated_design)
