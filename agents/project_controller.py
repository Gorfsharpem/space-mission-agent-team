"""
Project Controller Agent
-------------------------
Tracks mission schedule, milestones, earned value,
costs (paid/unpaid), and produces phase review dashboards.
"""

from agents.base_agent import BaseAgent


class ProjectControllerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Project Controller",
            role="Mission Project Controller",
            expertise=(
                "Earned Value Management (EVM), schedule control (Gantt, CPM, critical path), "
                "cost control (budget at completion, cost variance, schedule variance), "
                "milestone tracking (planned vs actual), "
                "invoice and payment tracking, resource loading, "
                "risk contingency management, and project reporting (weekly, monthly, milestone)."
            ),
        )

    def milestone_review(self, phase_name: str, phase_outputs: str, schedule_data: str = "") -> str:
        context = phase_outputs
        if schedule_data:
            context += f"\n\n### Schedule Data\n\n{schedule_data}"

        task = (
            f"Produce a Milestone Review Report for **{phase_name}**.\n\n"
            "Include:\n"
            "1. **Milestone Status Table** — columns: "
            "Milestone | Planned Date | Actual Date | Status (On-time/Delayed/At Risk) | "
            "Delta (days) | Owner\n"
            "2. **Phase Completion Assessment** — % complete by work package, "
            "with RAG (Red/Amber/Green) status\n"
            "3. **Earned Value Summary** — "
            "BCWS (Planned Value), BCWP (Earned Value), ACWP (Actual Cost), "
            "SPI (Schedule Performance Index), CPI (Cost Performance Index)\n"
            "4. **Budget Status** — "
            "table: Budget Line | Approved Budget | Spent (invoiced) | "
            "Committed (ordered, not invoiced) | Remaining | Forecast at Completion\n"
            "5. **Payment Tracking** — invoices issued, paid, and outstanding; "
            "next payment milestone and conditions\n"
            "6. **Critical Path** — current critical path activities and float\n"
            "7. **Forecast** — projected phase completion date and cost at completion\n"
            "8. **Actions Required** — top 5 corrective actions with owner and due date\n"
        )
        return self.run(task, context=context)

    def payment_schedule(self, business_analysis: str) -> str:
        task = (
            "Generate a Mission Payment Schedule and Invoice Plan.\n\n"
            "Based on the mission phases and cost structure, produce:\n"
            "1. **Payment Milestones Table** — "
            "Milestone | Phase | Trigger Event | Amount (EUR/USD) | "
            "Planned Payment Date | Status (Planned/Invoiced/Paid)\n"
            "2. **Cash Flow Projection** — monthly expenditure profile over mission lifecycle\n"
            "3. **Invoice Conditions** — what deliverables or events trigger each invoice\n"
            "4. **Payment Terms** — net payment terms, late payment penalties\n"
            "5. **Contingency Reserve** — how contingency budget is released and tracked\n"
            "6. **Financial Risk** — late payments, cost overruns, scope creep mitigation\n"
        )
        return self.run(task, context=business_analysis)
