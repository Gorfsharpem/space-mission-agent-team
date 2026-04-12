"""
Bid Manager Agent
-----------------
Owns the commercial and pricing strategy for bids.
Works with the Proposal Manager on win strategy and price-to-win.
"""

from agents.base_agent import BaseAgent


class BidManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Bid Manager",
            role="Bid & Commercial Manager",
            expertise=(
                "Price-to-win analysis, cost modelling (bottom-up, parametric, analogical), "
                "commercial volume writing, contract terms (FFP, CPFF, T&M), "
                "teaming and subcontractor agreements, NDA management, "
                "bid governance (bid board, authority levels), "
                "competitive intelligence, should-cost analysis, "
                "margin and risk pricing, and export control (ITAR/EAR)."
            ),
        )

    def bid_decision(self, opportunity: str) -> str:
        task = (
            f"Evaluate the following opportunity and produce a Bid/No-Bid Decision Report:\n\n"
            f"{opportunity}\n\n"
            "Include:\n"
            "1. **Opportunity Summary** — customer, value, duration, scope\n"
            "2. **Strategic Fit** — alignment with company strategy (High/Medium/Low)\n"
            "3. **Win Probability Assessment** — estimated Pwin (%) with rationale\n"
            "4. **Competitive Landscape** — likely competitors and their strengths\n"
            "5. **Bid Cost Estimate** — cost to prepare and submit the bid (EUR)\n"
            "6. **Resource Availability** — key people required and their current availability\n"
            "7. **Risk Factors** — commercial, technical, and delivery risks\n"
            "8. **Decision** — BID / NO-BID / CONDITIONAL with clear rationale\n"
            "9. **Conditions / Actions** — if conditional, what must happen before committing\n"
        )
        return self.run(task, context="")

    def pricing_strategy(self, technical_scope: str, competitive_context: str = "") -> str:
        # Consult Project Controller for cost baseline
        cost_info = ""
        if self.network and "Project Controller" in self.network:
            cost_info = self.ask_agent(
                "Project Controller",
                "Please provide bottom-up cost estimates for this scope of work, "
                "including labour rates by role, non-recurring engineering costs, "
                "recurring unit costs, and recommended contingency percentage.",
                technical_scope,
            )

        full_context = technical_scope
        if competitive_context:
            full_context += f"\n\n### Competitive Context\n\n{competitive_context}"
        if cost_info:
            full_context += f"\n\n### Cost Estimate from Project Controller\n\n{cost_info}"

        task = (
            "Develop the Pricing Strategy and Commercial Volume.\n\n"
            "Include:\n"
            "1. **Cost Build-Up** — bottom-up cost by work package: "
            "Labour (hours × rate) | Materials | Subcontracts | Travel | Overheads | Margin\n"
            "2. **Price-to-Win Analysis** — estimated customer budget, "
            "competitor price range, our target price\n"
            "3. **Margin Strategy** — recommended margin by contract type and risk level\n"
            "4. **Contract Type Recommendation** — FFP vs CPFF vs T&M with rationale\n"
            "5. **Payment Terms** — milestone payment schedule aligned with deliverables\n"
            "6. **Risk Pricing** — contingency and risk budget allocation\n"
            "7. **Assumptions & Exclusions** — scope inclusions/exclusions, "
            "customer-furnished items, named subcontractors\n"
            "8. **Commercial Risks** — currency, inflation, late payment, scope creep mitigation\n"
        )
        return self.run(task, context=full_context)

    def contract_review(self, draft_contract: str) -> str:
        task = (
            "Review the draft contract and produce a Contract Risk Assessment.\n\n"
            "Flag:\n"
            "1. **Unfavourable Terms** — liability caps, IP ownership, termination clauses\n"
            "2. **Ambiguous Scope** — requirements that could lead to disputes\n"
            "3. **Payment Risk** — late payment provisions, invoice conditions\n"
            "4. **Penalty Clauses** — liquidated damages, performance bonds\n"
            "5. **IP & Data Rights** — what we retain vs what we licence to customer\n"
            "6. **Export Control** — ITAR/EAR triggers, end-use restrictions\n"
            "7. **Recommended Red Lines** — terms we must change before signing\n"
            "8. **Recommended Fallback Positions** — what we can accept under pressure\n"
        )
        return self.run(task, context=draft_contract)
