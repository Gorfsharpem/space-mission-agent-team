"""
Proposal Manager Agent
-----------------------
Leads the proposal process from ITT/RFP receipt to submission.
Coordinates technical, commercial, and management volumes.
"""

from agents.base_agent import BaseAgent


class ProposalManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Proposal Manager",
            role="Proposal Manager",
            expertise=(
                "ESA/NASA/commercial RFP and ITT response, "
                "proposal writing (technical, management, commercial volumes), "
                "win strategy and discriminators, "
                "executive summary and storyboarding, "
                "compliance matrix, colour team reviews (Pink / Red / Gold), "
                "teaming agreements and consortium management, "
                "proposal scheduling (S-curves, submission milestones), "
                "and lessons learned from won/lost bids."
            ),
        )

    def analyse_rfp(self, rfp_text: str) -> str:
        task = (
            "Analyse the following RFP/ITT and produce a Proposal Kick-off Package.\n\n"
            "Include:\n"
            "1. **RFP Summary** — one-paragraph plain-language summary of what is being asked\n"
            "2. **Compliance Matrix** — table: RFP Requirement | Section | "
            "Compliant (Y/N/Partial) | Where addressed in proposal\n"
            "3. **Evaluation Criteria** — list with weightings if stated, "
            "ranked by importance\n"
            "4. **Win Themes** — 3-5 key differentiators we should emphasise\n"
            "5. **Gaps & Risks** — requirements we cannot fully meet, with mitigation\n"
            "6. **Proposal Outline** — recommended structure (volumes, sections, page limits)\n"
            "7. **Key Deadlines** — clarification questions due, submission date, "
            "presentations scheduled\n"
            "8. **Bid/No-Bid Recommendation** — with rationale and confidence level\n"
        )
        return self.run(task, context=rfp_text)

    def write_technical_volume(self, rfp_summary: str, team_context: str) -> str:
        # Query R&D Manager for relevant technology heritage
        tech_heritage = ""
        if self.network and "R&D Manager" in self.network:
            tech_heritage = self.ask_agent(
                "R&D Manager",
                "Please provide relevant technology heritage, TRL achievements, "
                "and R&D results we can reference in the proposal technical volume.",
                team_context,
            )

        full_context = rfp_summary + ("\n\n" + tech_heritage if tech_heritage else "")

        task = (
            "Write the Technical Volume of the proposal.\n\n"
            "Structure:\n"
            "1. **Executive Summary** — 1 page: what we propose, why we win, top 3 differentiators\n"
            "2. **Understanding of Requirements** — demonstrate deep understanding of the customer's need\n"
            "3. **Technical Approach** — mission concept, architecture, key design choices\n"
            "4. **Innovation & Differentiators** — what makes our solution unique\n"
            "5. **Heritage & Proven Technologies** — relevant past missions/projects, TRL evidence\n"
            "6. **Risk Management Approach** — top risks and our specific mitigation strategies\n"
            "7. **Compliance Summary** — confirm compliance to all key requirements\n"
        )
        return self.run(task, context=full_context)

    def proposal_review(self, draft_proposal: str, review_stage: str = "Red Team") -> str:
        task = (
            f"Conduct a **{review_stage} Review** of the draft proposal.\n\n"
            "Evaluate and report on:\n"
            "1. **Compliance** — are all RFP requirements addressed? List any gaps\n"
            "2. **Win Theme Strength** — are differentiators clear and compelling throughout?\n"
            "3. **Technical Credibility** — is the solution technically sound and believable?\n"
            "4. **Clarity & Readability** — is it easy to evaluate? Are key messages clear?\n"
            "5. **Weaknesses & Vulnerabilities** — what would evaluators score negatively?\n"
            "6. **Recommended Changes** — specific changes, ranked by impact on win probability\n"
            "7. **Overall Score** — out of 100, with breakdown by volume\n"
        )
        return self.run(task, context=draft_proposal)
