"""
R&D Manager Agent
------------------
Manages the innovation and research portfolio from idea to delivery.
Works across mission and proposal pipelines to identify technology gaps
and drive TRL maturation.
"""

from agents.base_agent import BaseAgent


class RnDManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="R&D Manager",
            role="Research & Development Manager",
            expertise=(
                "Technology readiness levels (TRL 1-9), technology maturation plans, "
                "ESA/NASA GSTP and BIC funding mechanisms, IP management, "
                "innovation portfolio management, technology transfer, "
                "research partnerships (universities, labs, agencies), "
                "R&D project planning and reporting, "
                "patent strategy, and technology roadmapping."
            ),
        )

    def rnd_project_initiation(self, idea: str, context: str = "") -> str:
        task = (
            f"Initiate an R&D Project for the following idea:\n\n**{idea}**\n\n"
            "Produce an R&D Project Initiation Document (PID) covering:\n\n"
            "1. **Technology Overview** — what the technology is and why it matters\n"
            "2. **Current TRL** — current Technology Readiness Level with justification\n"
            "3. **Target TRL** — desired TRL at project completion and why\n"
            "4. **Technology Gap Analysis** — what is missing between current and target TRL\n"
            "5. **Research Objectives** — 3-5 SMART objectives\n"
            "6. **Work Plan** — phases (Concept / Breadboard / Prototype / Demonstration), "
            "duration, and key activities per phase\n"
            "7. **Resource Requirements** — team, lab equipment, budget estimate (EUR)\n"
            "8. **Funding Strategy** — internal funding, ESA GSTP, Horizon Europe, "
            "national agencies, or customer-funded\n"
            "9. **IP & Exploitation Plan** — patent potential, licensing, "
            "route to flight qualification\n"
            "10. **Risk Register** — top 5 technical risks with likelihood and mitigation\n"
            "11. **Go/No-Go Criteria** — measurable criteria at each phase exit\n"
        )
        return self.run(task, context=context)

    def rnd_portfolio_review(self, active_projects: str) -> str:
        task = (
            "Conduct an R&D Portfolio Review.\n\n"
            "For the active R&D projects provided, produce:\n"
            "1. **Portfolio Dashboard** — table: Project | TRL Start/End | "
            "Phase | % Complete | Budget Status | RAG\n"
            "2. **TRL Progress Tracker** — TRL achieved vs planned for each project\n"
            "3. **Strategic Alignment** — how each project supports mission pipeline needs\n"
            "4. **Resource Conflicts** — team members or equipment over-allocated\n"
            "5. **Funding Status** — internal vs external funding per project\n"
            "6. **Stop/Continue/Accelerate Recommendations** — for each project with rationale\n"
            "7. **New Opportunities** — technology gaps identified from current missions "
            "that should start new R&D projects\n"
        )
        return self.run(task, context=active_projects)

    def technology_roadmap(self, mission_requirements: str) -> str:
        task = (
            "Produce a 5-year Technology Roadmap based on mission requirements.\n\n"
            "Include:\n"
            "1. **Technology Landscape** — key enabling technologies identified from requirements\n"
            "2. **TRL Assessment** — current TRL of each technology, target TRL and year needed\n"
            "3. **Roadmap Timeline** — year-by-year milestones per technology stream\n"
            "4. **Investment Plan** — budget allocation per technology per year\n"
            "5. **Critical Path Technologies** — technologies that gate mission readiness\n"
            "6. **Partnership Opportunities** — academia, agencies, industry for each stream\n"
        )
        return self.run(task, context=mission_requirements)
