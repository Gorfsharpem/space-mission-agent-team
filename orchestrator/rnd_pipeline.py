"""
R&D Pipeline
------------
Drives innovation projects from idea capture through to delivery.
The full team participates: R&D Manager owns the project,
Proposal Manager and Bid Manager handle funding bids,
QA/PA gates each phase, and the Document Manager tracks outputs.

Pipeline Stages:
  Stage 1 — Idea & Technology Assessment   (R&D Manager)
  Stage 2 — Funding Proposal               (Proposal Manager + Bid Manager)
  Stage 3 — Project Kick-off               (Project Manager + Project Controller)
  Stage 4 — Research Execution             (R&D Manager + subsystem experts)
  Stage 5 — QA Gate                        (QA/PA Engineer)
  Stage 6 — Results & Exploitation         (R&D Manager + Mission Director)
  Stage 7 — Document Management            (Document Manager)
"""

import os
from datetime import datetime

from core import MessageBus, AgentNetwork
from agents import (
    RnDManagerAgent, ProposalManagerAgent, BidManagerAgent,
    ProjectManagerAgent, ProjectControllerAgent,
    QAPAAgent, DocumentManagerAgent, MissionDirectorAgent,
)


class RnDPipeline:
    def __init__(self, project_name: str, idea: str, output_dir: str = "outputs"):
        self.project_name = project_name
        self.idea = idea
        self.output_dir = output_dir
        self.timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        self.results: dict[str, str] = {}
        os.makedirs(output_dir, exist_ok=True)

        self.bus = MessageBus()
        self.network = AgentNetwork(self.bus)

        self.rnd      = RnDManagerAgent()
        self.proposal = ProposalManagerAgent()
        self.bid      = BidManagerAgent()
        self.pm       = ProjectManagerAgent()
        self.ctrl     = ProjectControllerAgent()
        self.qa       = QAPAAgent()
        self.doc_mgr  = DocumentManagerAgent()
        self.director = MissionDirectorAgent()

        for agent in [self.rnd, self.proposal, self.bid, self.pm,
                      self.ctrl, self.qa, self.doc_mgr, self.director]:
            agent.network = self.network
            self.network.register(agent)

    def _log(self, msg: str):
        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] {msg}")

    def _save(self, section: str, content: str) -> str:
        fname = (f"{self.output_dir}/{self.timestamp}_rnd_"
                 f"{section.lower().replace(' ', '_')}.md")
        with open(fname, "w") as f:
            f.write(f"# {section}\n\n**R&D Project:** {self.project_name}  \n"
                    f"**Generated:** {self.timestamp}  \n\n---\n\n{content}")
        self._log(f"  ✔ Saved → {fname}")
        return fname

    def _ctx(self, *keys) -> str:
        return "\n\n---\n\n".join(
            f"### {k}\n\n{self.results[k]}" for k in keys if k in self.results
        )

    # ── Stages ──────────────────────────────────────────────────────────

    def stage_1_idea_assessment(self):
        self._log("━━ STAGE 1 — Idea & Technology Assessment ━━")
        pid = self.rnd.rnd_project_initiation(self.idea)
        self.results["R&D Project Initiation Document"] = pid
        self._save("R&D Project Initiation Document", pid)

        roadmap = self.rnd.technology_roadmap(pid)
        self.results["Technology Roadmap"] = roadmap
        self._save("Technology Roadmap", roadmap)

    def stage_2_funding_proposal(self):
        self._log("━━ STAGE 2 — Funding Strategy & Proposal ━━")
        ctx = self._ctx("R&D Project Initiation Document")

        bid_dec = self.bid.bid_decision(
            f"R&D funding opportunity for: {self.project_name}\n\n{ctx}"
        )
        self.results["Bid Decision"] = bid_dec
        self._save("Bid Decision", bid_dec)

        pricing = self.bid.pricing_strategy(ctx)
        self.results["R&D Pricing Strategy"] = pricing
        self._save("R&D Pricing Strategy", pricing)

        tech_vol = self.proposal.write_technical_volume(ctx, ctx)
        self.results["Proposal Technical Volume"] = tech_vol
        self._save("Proposal Technical Volume", tech_vol)

    def stage_3_project_kickoff(self):
        self._log("━━ STAGE 3 — Project Kick-off ━━")
        ctx = self._ctx("R&D Project Initiation Document", "R&D Pricing Strategy")

        plan = self.pm.run_business_analysis(
            f"R&D Project kick-off for: {self.project_name}. "
            f"Produce a project plan, team structure, and WBS.\n\n{ctx}"
        )
        self.results["R&D Project Plan"] = plan
        self._save("R&D Project Plan", plan)

        schedule = self.ctrl.payment_schedule(ctx)
        self.results["R&D Payment Schedule"] = schedule
        self._save("R&D Payment Schedule", schedule)

    def stage_4_execution_review(self):
        self._log("━━ STAGE 4 — Execution Review (mid-project) ━━")
        ctx = self._ctx(
            "R&D Project Initiation Document", "R&D Project Plan",
            "Technology Roadmap",
        )
        portfolio = self.rnd.rnd_portfolio_review(ctx)
        self.results["R&D Portfolio Review"] = portfolio
        self._save("R&D Portfolio Review", portfolio)

        ms = self.ctrl.milestone_review("R&D Mid-Project Review", ctx)
        self.results["R&D Milestone Review"] = ms
        self._save("R&D Milestone Review", ms)

    def stage_5_qa_gate(self):
        self._log("━━ STAGE 5 — QA/PA Gate Review ━━")
        ctx = self._ctx(
            "R&D Project Initiation Document", "R&D Portfolio Review",
            "R&D Milestone Review",
        )
        gate = self.qa.phase_gate_review("R&D Phase Gate Review", ctx)
        self.results["R&D QA Gate Review"] = gate
        self._save("R&D QA Gate Review", gate)

    def stage_6_results_exploitation(self):
        self._log("━━ STAGE 6 — Results & Exploitation ━━")
        ctx = self._ctx(
            "R&D Project Initiation Document", "Technology Roadmap",
            "R&D Portfolio Review",
        )
        exploitation = self.rnd.run(
            "Based on the R&D project results, produce an Exploitation Plan.\n\n"
            "Include:\n"
            "1. **Key Results & Achievements** — TRL reached, key measurements, demos\n"
            "2. **IP Output** — patents filed, know-how generated, software tools\n"
            "3. **Route to Flight** — qualification plan, next TRL steps, target missions\n"
            "4. **Commercial Exploitation** — licensing opportunities, spin-off potential\n"
            "5. **Publications & Dissemination** — conference papers, journal articles planned\n"
            "6. **Lessons Learned** — what worked, what did not, recommendations for future\n"
            "7. **Follow-on Funding** — recommended next project and funding route\n",
            context=ctx,
        )
        self.results["R&D Exploitation Plan"] = exploitation
        self._save("R&D Exploitation Plan", exploitation)

    def stage_7_documents(self):
        self._log("━━ STAGE 7 — Document Management ━━")
        tree = self.doc_mgr.build_document_tree(self.project_name, self.results)
        self.results["R&D Document Tree"] = tree
        self._save("R&D Document Tree", tree)

    def generate_master(self):
        self._log("━━ Generating R&D Master Report ━━")
        order = [
            "R&D Project Initiation Document", "Technology Roadmap",
            "Bid Decision", "R&D Pricing Strategy", "Proposal Technical Volume",
            "R&D Project Plan", "R&D Payment Schedule",
            "R&D Portfolio Review", "R&D Milestone Review",
            "R&D QA Gate Review",
            "R&D Exploitation Plan", "R&D Document Tree",
        ]
        lines = [
            f"# {self.project_name} — R&D Master Report\n",
            f"**Generated:** {self.timestamp}  \n",
            f"**Idea:** {self.idea}\n\n---\n\n## Table of Contents\n",
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
        return self._save("R&D Master Report", master)

    def run(self):
        self._log(f"🔬 Starting R&D Pipeline: {self.project_name}")
        self.stage_1_idea_assessment()
        self.stage_2_funding_proposal()
        self.stage_3_project_kickoff()
        self.stage_4_execution_review()
        self.stage_5_qa_gate()
        self.stage_6_results_exploitation()
        self.stage_7_documents()
        path = self.generate_master()
        self._log(f"\n✅ R&D Pipeline Complete! Report: {path}")
        self._log(f"   Inter-agent messages exchanged: {len(self.bus)}")
        return self.results
