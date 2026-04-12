"""
Project Manager Agent
---------------------
Translates business objectives into mission goals, defines stakeholders,
manages schedule, cost constraints, and keeps the team aligned.
"""

from agents.base_agent import BaseAgent


class ProjectManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Project Manager",
            role="Mission Project Manager",
            expertise=(
                "Space project management (ECSS-M standards), stakeholder management, "
                "work breakdown structure (WBS), schedule (Gantt, CPM), cost estimation, "
                "risk registers, milestone reviews (SRR, PDR, CDR, QR, AR), "
                "and mission lifecycle governance."
            ),
        )

    def run_business_analysis(self, business_objective: str) -> str:
        task = (
            "Analyse the business objective and produce a Mission Initiation Document.\n\n"
            "Produce:\n"
            "1. **Mission Statement** — one-paragraph summary of what this mission does and why\n"
            "2. **Stakeholder Analysis** — key stakeholders, their roles, and needs\n"
            "3. **Mission Goals & Success Criteria** — SMART goals with measurable KPIs\n"
            "4. **High-Level Schedule** — major phases (A through E) with indicative durations\n"
            "5. **Cost & Resource Constraints** — budget envelope and key resource limits\n"
            "6. **Key Risks at Project Level** — top risks to delivery and mitigation strategy\n"
        )
        return self.run(task, context=f"Business Objective: {business_objective}")
