"""
Mission Pipeline
----------------
Orchestrates the full mission lifecycle from business objective
to commissioning plan.  All agents are connected via AgentNetwork
so they can query each other during design.

Pipeline Stages:
  Phase 0 — Business Analysis       (Project Manager + Project Controller)
  Phase A — Mission Analysis        (Mission Analyst + Mission Director)
  Phase B — Subsystem Design        (All subsystem agents — parallel, inter-connected)
  QA Gate — Phase B gate review     (QA/PA Engineer)
  Phase C — System Integration      (Mission Director)
  Phase D — Commissioning Planning  (Mission Director)
  QA Gate — Final gate review       (QA/PA Engineer)
  Docs    — Document tree           (Document Manager)
"""

import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from core import MessageBus, AgentNetwork
from core.agent_factory import build_agent_roster


class MissionPipeline:
    def __init__(self, mission_name: str, business_objective: str, output_dir: str = "outputs"):
        self.mission_name = mission_name
        self.business_objective = business_objective
        self.output_dir = output_dir
        self.timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        self.results: dict[str, str] = {}
        os.makedirs(output_dir, exist_ok=True)

        # Infrastructure
        self.bus = MessageBus()
        self.network = AgentNetwork(self.bus)

        roster = build_agent_roster(
            only=[
                "Mission Director", "Project Manager", "Mission Analyst",
                "Payload Engineer", "EPS Engineer", "ADCS Engineer",
                "Thermal Engineer", "Structures Engineer", "TTC Engineer",
                "OBSW Engineer", "Propulsion Engineer", "Mechanical Engineer",
                "Electrical Engineer", "Antenna Engineer", "QA/PA Engineer",
                "Document Manager", "Project Controller",
            ]
        )

        for agent in roster.values():
            agent.network = self.network
            self.network.register(agent)

        # Convenience aliases
        self.director   = roster["Mission Director"]
        self.pm         = roster["Project Manager"]
        self.ma         = roster["Mission Analyst"]
        self.payload    = roster["Payload Engineer"]
        self.eps        = roster["EPS Engineer"]
        self.adcs       = roster["ADCS Engineer"]
        self.thermal    = roster["Thermal Engineer"]
        self.structures = roster["Structures Engineer"]
        self.ttc        = roster["TTC Engineer"]
        self.obsw       = roster["OBSW Engineer"]
        self.propulsion = roster["Propulsion Engineer"]
        self.mechanical = roster["Mechanical Engineer"]
        self.electrical = roster["Electrical Engineer"]
        self.antenna    = roster["Antenna Engineer"]
        self.qa_pa      = roster["QA/PA Engineer"]
        self.doc_mgr    = roster["Document Manager"]
        self.controller = roster["Project Controller"]

    def _log(self, msg: str):
        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] {msg}")

    def _save(self, section: str, content: str) -> str:
        fname = f"{self.output_dir}/{self.timestamp}_{section.lower().replace(' ', '_')}.md"
        with open(fname, "w") as f:
            f.write(f"# {section}\n\n**Mission:** {self.mission_name}  \n"
                    f"**Generated:** {self.timestamp}  \n\n---\n\n{content}")
        self._log(f"  ✔ Saved → {fname}")
        return fname

    def _ctx(self, *keys) -> str:
        return "\n\n---\n\n".join(
            f"### {k}\n\n{self.results[k]}" for k in keys if k in self.results
        )

    # ── Phases ──────────────────────────────────────────────────────────

    def phase_0(self):
        self._log("━━ PHASE 0 — Business Analysis ━━")
        out = self.pm.run_business_analysis(self.business_objective)
        self.results["Business Analysis"] = out
        self._save("Business Analysis", out)

        ctrl = self.controller.payment_schedule(out)
        self.results["Payment Schedule"] = ctrl
        self._save("Payment Schedule", ctrl)

    def phase_a(self):
        self._log("━━ PHASE A — Mission Analysis ━━")
        ctx = self._ctx("Business Analysis")
        ma_out = self.ma.run_mission_analysis(ctx)
        self.results["Mission Analysis"] = ma_out
        self._save("Mission Analysis", ma_out)

        sys_req = self.director.derive_system_requirements(
            self._ctx("Business Analysis", "Mission Analysis")
        )
        self.results["System Requirements"] = sys_req
        self._save("System Requirements", sys_req)

    def phase_b(self):
        self._log("━━ PHASE B — Subsystem Design (parallel, inter-agent comms enabled) ━━")
        ctx = self._ctx("Business Analysis", "Mission Analysis", "System Requirements")

        tasks = {
            "Payload Design":    lambda: self.payload.design_payload(ctx),
            "EPS Design":        lambda: self.eps.design_eps(ctx),
            "ADCS Design":       lambda: self.adcs.design_adcs(ctx),
            "Thermal Design":    lambda: self.thermal.design_thermal(ctx),
            "Structures Design": lambda: self.structures.design_structures(ctx),
            "Propulsion Design": lambda: self.propulsion.design_propulsion(ctx),
            "TTC Design":        lambda: self.ttc.design_ttc(ctx),
            "OBSW Design":       lambda: self.obsw.design_obsw(ctx),
            "Mechanical Design": lambda: self.mechanical.design_mechanical(ctx),
            "Electrical Design": lambda: self.electrical.design_electrical(ctx),
            "Antenna Design":    lambda: self.antenna.design_antennas(ctx),
        }

        with ThreadPoolExecutor(max_workers=4) as ex:
            futures = {ex.submit(fn): name for name, fn in tasks.items()}
            for f in as_completed(futures):
                name = futures[f]
                try:
                    result = f.result()
                    self.results[name] = result
                    self._save(name, result)
                    self._log(f"  ✔ {name} complete")
                except Exception as e:
                    self._log(f"  ✘ {name} failed: {e}")

    def qa_gate_b(self):
        self._log("━━ QA/PA GATE — Phase B Review ━━")
        all_b = self._ctx(
            "Payload Design", "EPS Design", "ADCS Design", "Thermal Design",
            "Structures Design", "Propulsion Design", "TTC Design", "OBSW Design",
            "Mechanical Design", "Electrical Design", "Antenna Design",
        )
        gate = self.qa_pa.phase_gate_review("Phase B — Subsystem Design", all_b)
        self.results["QA Gate B Review"] = gate
        self._save("QA Gate B Review", gate)

        fmea = self.qa_pa.fmea_review(all_b)
        self.results["FMEA Review"] = fmea
        self._save("FMEA Review", fmea)

    def phase_c(self):
        self._log("━━ PHASE C — System Integration Review ━━")
        ctx = self._ctx(
            "System Requirements", "Payload Design", "EPS Design", "ADCS Design",
            "Thermal Design", "Structures Design", "Propulsion Design",
            "TTC Design", "OBSW Design", "Mechanical Design",
            "Electrical Design", "Antenna Design",
        )
        out = self.director.integration_review(ctx)
        self.results["System Integration Review"] = out
        self._save("System Integration Review", out)

        ms = self.controller.milestone_review("Phase C — System Integration", out)
        self.results["Phase C Milestone Review"] = ms
        self._save("Phase C Milestone Review", ms)

    def phase_d(self):
        self._log("━━ PHASE D — Commissioning Plan ━━")
        ctx = self._ctx(
            "System Requirements", "System Integration Review",
            "Payload Design", "TTC Design", "OBSW Design",
        )
        out = self.director.commissioning_plan(ctx)
        self.results["Commissioning Plan"] = out
        self._save("Commissioning Plan", out)

        atp = self.qa_pa.acceptance_test_plan(
            self._ctx("System Integration Review", "Commissioning Plan")
        )
        self.results["Acceptance Test Plan"] = atp
        self._save("Acceptance Test Plan", atp)

    def qa_gate_final(self):
        self._log("━━ QA/PA GATE — Final Mission Readiness Review ━━")
        ctx = self._ctx("System Integration Review", "Commissioning Plan", "Acceptance Test Plan")
        gate = self.qa_pa.phase_gate_review("Final Mission Readiness Review", ctx)
        self.results["QA Final Gate Review"] = gate
        self._save("QA Final Gate Review", gate)

    def build_document_tree(self):
        self._log("━━ Document Manager — Building Document Tree ━━")
        tree = self.doc_mgr.build_document_tree(self.mission_name, self.results)
        self.results["Document Tree"] = tree
        self._save("Document Tree", tree)

    def generate_master_document(self):
        self._log("━━ Generating Master Mission Design Document ━━")
        order = [
            "Business Analysis", "Payment Schedule",
            "Mission Analysis", "System Requirements",
            "Payload Design", "EPS Design", "ADCS Design", "Thermal Design",
            "Structures Design", "Propulsion Design", "Mechanical Design",
            "Electrical Design", "Antenna Design", "TTC Design", "OBSW Design",
            "QA Gate B Review", "FMEA Review",
            "System Integration Review", "Phase C Milestone Review",
            "Commissioning Plan", "Acceptance Test Plan",
            "QA Final Gate Review", "Document Tree",
        ]
        lines = [
            f"# {self.mission_name} — Master Mission Design Document\n",
            f"**Generated:** {self.timestamp}  \n",
            f"**Business Objective:** {self.business_objective}\n\n---\n\n## Table of Contents\n",
        ]
        for i, s in enumerate(order, 1):
            if s in self.results:
                lines.append(f"{i}. {s}")
        lines.append("\n\n---\n")
        for s in order:
            if s in self.results:
                lines.append(f"\n## {s}\n\n{self.results[s]}\n\n---\n")

        # Append inter-agent communication log
        if len(self.bus) > 0:
            lines.append("\n## Inter-Agent Communication Log\n\n")
            lines.append(self.bus.format_log())

        master = "\n".join(lines)
        return self._save("Master Mission Design Document", master)

    def run(self):
        self._log(f"🚀 Starting Mission Pipeline: {self.mission_name}")
        self.phase_0()
        self.phase_a()
        self.phase_b()
        self.qa_gate_b()
        self.phase_c()
        self.phase_d()
        self.qa_gate_final()
        self.build_document_tree()
        path = self.generate_master_document()
        self._log(f"\n✅ Mission Pipeline Complete! Master doc: {path}")
        self._log(f"   Inter-agent messages exchanged: {len(self.bus)}")
        return self.results
