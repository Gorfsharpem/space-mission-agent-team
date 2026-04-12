"""
Proposal Pipeline
-----------------
Drives a bid from opportunity identification through to contract award.

Pipeline Stages:
  Stage 1 — Opportunity Evaluation & Bid/No-Bid  (Bid Manager)
  Stage 2 — RFP Analysis                         (Proposal Manager)
  Stage 3 — Technical Volume                     (Proposal Manager + R&D Manager)
  Stage 4 — Pricing & Commercial Volume          (Bid Manager + Project Controller)
  Stage 5 — Internal Review (Red Team)           (Proposal Manager + QA/PA)
  Stage 6 — Submission Package                   (Document Manager)
  Stage 7 — Contract Review (post-award)         (Bid Manager)
"""

import os
from datetime import datetime

from core import MessageBus, AgentNetwork
from agents import (
    BidManagerAgent, ProposalManagerAgent, ProjectControllerAgent,
    QAPAAgent, DocumentManagerAgent, RnDManagerAgent,
)


class ProposalPipeline:
    def __init__(
        self,
        proposal_name: str,
        opportunity_description: str,
        rfp_text: str = "",
        output_dir: str = "outputs",
    ):
        self.proposal_name = proposal_name
        self.opportunity = opportunity_description
        self.rfp_text = rfp_text
        self.output_dir = output_dir
        self.timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        self.results: dict[str, str] = {}
        os.makedirs(output_dir, exist_ok=True)

        self.bus = MessageBus()
        self.network = AgentNetwork(self.bus)

        self.bid      = BidManagerAgent()
        self.proposal = ProposalManagerAgent()
        self.ctrl     = ProjectControllerAgent()
        self.qa       = QAPAAgent()
        self.doc_mgr  = DocumentManagerAgent()
        self.rnd      = RnDManagerAgent()

        for agent in [self.bid, self.proposal, self.ctrl, self.qa, self.doc_mgr, self.rnd]:
            agent.network = self.network
            self.network.register(agent)

    def _log(self, msg: str):
        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] {msg}")

    def _save(self, section: str, content: str) -> str:
        fname = (f"{self.output_dir}/{self.timestamp}_proposal_"
                 f"{section.lower().replace(' ', '_')}.md")
        with open(fname, "w") as f:
            f.write(f"# {section}\n\n**Proposal:** {self.proposal_name}  \n"
                    f"**Generated:** {self.timestamp}  \n\n---\n\n{content}")
        self._log(f"  ✔ Saved → {fname}")
        return fname

    def _ctx(self, *keys) -> str:
        return "\n\n---\n\n".join(
            f"### {k}\n\n{self.results[k]}" for k in keys if k in self.results
        )

    def stage_1_bid_decision(self):
        self._log("━━ STAGE 1 — Bid/No-Bid Decision ━━")
        decision = self.bid.bid_decision(self.opportunity)
        self.results["Bid Decision"] = decision
        self._save("Bid Decision", decision)

    def stage_2_rfp_analysis(self):
        self._log("━━ STAGE 2 — RFP Analysis ━━")
        source = self.rfp_text if self.rfp_text else self.opportunity
        analysis = self.proposal.analyse_rfp(source)
        self.results["RFP Analysis"] = analysis
        self._save("RFP Analysis", analysis)

    def stage_3_technical_volume(self):
        self._log("━━ STAGE 3 — Technical Volume ━━")
        ctx = self._ctx("RFP Analysis", "Bid Decision")
        tech = self.proposal.write_technical_volume(ctx, ctx)
        self.results["Technical Volume"] = tech
        self._save("Technical Volume", tech)

    def stage_4_commercial_volume(self):
        self._log("━━ STAGE 4 — Pricing & Commercial Volume ━━")
        ctx = self._ctx("RFP Analysis", "Technical Volume")
        pricing = self.bid.pricing_strategy(ctx)
        self.results["Commercial Volume"] = pricing
        self._save("Commercial Volume", pricing)

        ms = self.ctrl.payment_schedule(ctx)
        self.results["Proposed Payment Schedule"] = ms
        self._save("Proposed Payment Schedule", ms)

    def stage_5_red_team_review(self):
        self._log("━━ STAGE 5 — Red Team Review ━━")
        full_proposal = self._ctx("Technical Volume", "Commercial Volume")
        review = self.proposal.proposal_review(full_proposal, review_stage="Red Team")
        self.results["Red Team Review"] = review
        self._save("Red Team Review", review)

        qa_check = self.qa.phase_gate_review("Proposal Submission Gate", full_proposal)
        self.results["Proposal QA Gate"] = qa_check
        self._save("Proposal QA Gate", qa_check)

    def stage_6_submission_package(self):
        self._log("━━ STAGE 6 — Submission Package ━━")
        tree = self.doc_mgr.build_document_tree(self.proposal_name, self.results)
        self.results["Submission Document List"] = tree
        self._save("Submission Document List", tree)

    def stage_7_contract_review(self, draft_contract: str = ""):
        self._log("━━ STAGE 7 — Post-Award Contract Review ━━")
        source = draft_contract if draft_contract else self._ctx("Commercial Volume", "RFP Analysis")
        review = self.bid.contract_review(source)
        self.results["Contract Review"] = review
        self._save("Contract Review", review)

    def generate_master(self):
        self._log("━━ Generating Proposal Master Package ━━")
        order = [
            "Bid Decision", "RFP Analysis",
            "Technical Volume", "Commercial Volume", "Proposed Payment Schedule",
            "Red Team Review", "Proposal QA Gate",
            "Submission Document List", "Contract Review",
        ]
        lines = [
            f"# {self.proposal_name} — Proposal Master Package\n",
            f"**Generated:** {self.timestamp}  \n",
            f"**Opportunity:** {self.opportunity[:200]}...\n\n---\n\n## Table of Contents\n",
        ]
        for i, s in enumerate(order, 1):
            if s in self.results:
                lines.append(f"{i}. {s}")
        lines.append("\n\n---\n")
        for s in order:
            if s in self.results:
                lines.append(f"\n## {s}\n\n{self.results[s]}\n\n---\n")

        if len(self.bus) > 0:
            lines.append("\n## Inter-Agent Communication Log\n\n")
            lines.append(self.bus.format_log())

        master = "\n".join(lines)
        return self._save("Proposal Master Package", master)

    def run(self, draft_contract: str = ""):
        self._log(f"📋 Starting Proposal Pipeline: {self.proposal_name}")
        self.stage_1_bid_decision()
        self.stage_2_rfp_analysis()
        self.stage_3_technical_volume()
        self.stage_4_commercial_volume()
        self.stage_5_red_team_review()
        self.stage_6_submission_package()
        self.stage_7_contract_review(draft_contract)
        path = self.generate_master()
        self._log(f"\n✅ Proposal Pipeline Complete! Package: {path}")
        self._log(f"   Inter-agent messages exchanged: {len(self.bus)}")
        return self.results
