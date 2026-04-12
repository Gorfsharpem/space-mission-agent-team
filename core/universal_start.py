"""
Universal Start Engine
-----------------------
Start from ANY point in the system. The engine figures out what to run.

Start modes:
  FULL       — start from business objective, run entire mission pipeline
  SUBSYSTEM  — start from a specific subsystem, re-run that agent + propagate changes
  MILESTONE  — run a full milestone review (SRR / PDR / CDR / QR / AR)
  CHANGE     — propagate a change from any agent
  RESUME     — resume from saved session state, continue from last phase

The key design:
  The session state carries the mission baseline between runs.
  Any agent starting a SUBSYSTEM run gets the full baseline as context,
  produces their updated output, then change propagation handles alignment.
"""

from __future__ import annotations
import os
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from core.message_bus import MessageBus
from core.agent_network import AgentNetwork
from core.session_state import SessionState
from core.change_request import ChangeRequest, Severity, SourceType
from core.change_propagator import ChangePropagator
from core.milestone_review import MilestoneReview

if TYPE_CHECKING:
    pass


class StartMode(str, Enum):
    FULL      = "FULL"
    SUBSYSTEM = "SUBSYSTEM"
    MILESTONE = "MILESTONE"
    CHANGE    = "CHANGE"
    RESUME    = "RESUME"


# ── Agent → pipeline action map ──────────────────────────────────────────────
# Defines what each agent's "start from here" action triggers

AGENT_ACTION_MAP: dict[str, dict] = {
    # Business / management layer — triggers full pipeline phases
    "User":             {"mode": StartMode.FULL,  "phase": "0"},
    "Project Manager":  {"mode": StartMode.FULL,  "phase": "0"},
    "Mission Director": {"mode": StartMode.FULL,  "phase": "A"},
    "Mission Analyst":  {"mode": StartMode.FULL,  "phase": "A"},
    "Bid Manager":      {"mode": StartMode.FULL,  "phase": "PROPOSAL"},
    "Proposal Manager": {"mode": StartMode.FULL,  "phase": "PROPOSAL"},
    "R&D Manager":      {"mode": StartMode.FULL,  "phase": "RND"},

    # Subsystem engineers — trigger subsystem re-run + change propagation
    "Payload Engineer":    {"mode": StartMode.SUBSYSTEM, "method": "design_payload"},
    "EPS Engineer":        {"mode": StartMode.SUBSYSTEM, "method": "design_eps"},
    "ADCS Engineer":       {"mode": StartMode.SUBSYSTEM, "method": "design_adcs"},
    "Thermal Engineer":    {"mode": StartMode.SUBSYSTEM, "method": "design_thermal"},
    "Structures Engineer": {"mode": StartMode.SUBSYSTEM, "method": "design_structures"},
    "Propulsion Engineer": {"mode": StartMode.SUBSYSTEM, "method": "design_propulsion"},
    "Mechanical Engineer": {"mode": StartMode.SUBSYSTEM, "method": "design_mechanical"},
    "Electrical Engineer": {"mode": StartMode.SUBSYSTEM, "method": "design_electrical"},
    "Antenna Engineer":    {"mode": StartMode.SUBSYSTEM, "method": "design_antennas"},
    "TT&C Engineer":       {"mode": StartMode.SUBSYSTEM, "method": "design_ttc"},
    "OBSW Engineer":       {"mode": StartMode.SUBSYSTEM, "method": "design_obsw"},

    # Support agents — trigger their specific functions
    "QA/PA Engineer":     {"mode": StartMode.MILESTONE, "default_milestone": "PDR"},
    "Project Controller":    {"mode": StartMode.MILESTONE, "default_milestone": "PDR"},
    "Document Manager":      {"mode": StartMode.MILESTONE, "default_milestone": "PDR"},
    "Safety Engineer":       {"mode": StartMode.SUBSYSTEM,  "method": "safety_analysis"},
    "Ground Segment Engineer": {"mode": StartMode.SUBSYSTEM, "method": "design_ground_segment"},
    "Launch Campaign Manager": {"mode": StartMode.SUBSYSTEM, "method": "plan_launch_campaign"},
}


class UniversalStartEngine:
    """
    Universal entry point. Instantiated once per session.
    Carries session state across runs.
    """

    def __init__(self, network: AgentNetwork, bus: MessageBus,
                 session: SessionState, output_dir: str = "outputs"):
        self.network = network
        self.bus = bus
        self.session = session
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _log(self, msg: str):
        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] {msg}")

    def _save_section(self, title: str, content: str):
        self.session.update(title, content)
        fname = f"{self.output_dir}/{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}_{title.lower().replace(' ', '_')}.md"
        with open(fname, "w") as f:
            f.write(f"# {title}\n\n**Mission:** {self.session.mission_name}  \n\n---\n\n{content}")
        return fname

    # ── FULL pipeline phases ─────────────────────────────────────────────

    def _run_phase_0(self):
        from agents import ProjectManagerAgent, ProjectControllerAgent
        self._log("━━ PHASE 0 — Business Analysis ━━")
        pm = self.network._registry.get("Project Manager")
        ctrl = self.network._registry.get("Project Controller")
        if pm:
            out = pm.run_business_analysis(self.session.business_objective)
            self._save_section("Business Analysis", out)
        if ctrl:
            out = ctrl.payment_schedule(self.session.get_context(["Business Analysis"]))
            self._save_section("Payment Schedule", out)
        self.session.phase = "PHASE_0"
        self.session.save()

    def _run_phase_a(self):
        self._log("━━ PHASE A — Mission Analysis ━━")
        ctx = self.session.get_context(["Business Analysis"])
        ma = self.network._registry.get("Mission Analyst")
        md = self.network._registry.get("Mission Director")
        if ma:
            out = ma.run_mission_analysis(ctx)
            self._save_section("Mission Analysis", out)
        if md:
            out = md.derive_system_requirements(
                self.session.get_context(["Business Analysis", "Mission Analysis"])
            )
            self._save_section("System Requirements", out)
        self.session.phase = "PHASE_A"
        self.session.save()

    def _run_phase_b(self):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        self._log("━━ PHASE B — Subsystem Design (parallel) ━━")
        ctx = self.session.get_context(
            ["Business Analysis", "Mission Analysis", "System Requirements"]
        )
        subsystem_agents = {
            "Payload Design":    ("Payload Engineer",    "design_payload"),
            "EPS Design":        ("EPS Engineer",        "design_eps"),
            "ADCS Design":       ("ADCS Engineer",       "design_adcs"),
            "Thermal Design":    ("Thermal Engineer",    "design_thermal"),
            "Structures Design": ("Structures Engineer", "design_structures"),
            "Propulsion Design": ("Propulsion Engineer", "design_propulsion"),
            "TTC Design":        ("TT&C Engineer",       "design_ttc"),
            "OBSW Design":       ("OBSW Engineer",       "design_obsw"),
            "Mechanical Design": ("Mechanical Engineer", "design_mechanical"),
            "Electrical Design": ("Electrical Engineer", "design_electrical"),
            "Antenna Design":    ("Antenna Engineer",    "design_antennas"),
        }
        with ThreadPoolExecutor(max_workers=4) as ex:
            futures = {}
            for title, (agent_name, method) in subsystem_agents.items():
                agent = self.network._registry.get(agent_name)
                if agent and hasattr(agent, method):
                    futures[ex.submit(getattr(agent, method), ctx)] = title
            for f in as_completed(futures):
                title = futures[f]
                try:
                    self._save_section(title, f.result())
                    self._log(f"  ✔ {title}")
                except Exception as e:
                    self._log(f"  ✘ {title}: {e}")
        self.session.phase = "PHASE_B"
        self.session.save()

    def _run_phase_c(self):
        self._log("━━ PHASE C — System Integration ━━")
        md = self.network._registry.get("Mission Director")
        ctrl = self.network._registry.get("Project Controller")
        ctx = self.session.get_context()
        if md:
            out = md.integration_review(ctx)
            self._save_section("System Integration Review", out)
        if ctrl:
            out = ctrl.milestone_review("Phase C", self.session.get_context(["System Integration Review"]))
            self._save_section("Phase C Milestone Review", out)
        self.session.phase = "PHASE_C"
        self.session.save()

    def _run_phase_d(self):
        self._log("━━ PHASE D — Commissioning ━━")
        md = self.network._registry.get("Mission Director")
        qa = self.network._registry.get("QA/PA Engineer")
        ctx = self.session.get_context()
        if md:
            out = md.commissioning_plan(ctx)
            self._save_section("Commissioning Plan", out)
        if qa:
            out = qa.acceptance_test_plan(ctx)
            self._save_section("Acceptance Test Plan", out)
        self.session.phase = "PHASE_D"
        self.session.save()

    # ── SUBSYSTEM re-run ─────────────────────────────────────────────────

    def _run_subsystem(self, agent_name: str, method: str, description: str):
        self._log(f"━━ SUBSYSTEM START: {agent_name} ━━")
        agent = self.network._registry.get(agent_name)
        if not agent or not hasattr(agent, method):
            self._log(f"  ✘ Agent {agent_name} or method {method} not found")
            return None

        ctx = self.session.get_context()
        self._log(f"  Running {agent_name}.{method}() with full mission context...")
        result = getattr(agent, method)(ctx)

        # Map agent name to section title
        section_map = {
            "Payload Engineer":    "Payload Design",
            "EPS Engineer":        "EPS Design",
            "ADCS Engineer":       "ADCS Design",
            "Thermal Engineer":    "Thermal Design",
            "Structures Engineer": "Structures Design",
            "Propulsion Engineer": "Propulsion Design",
            "Mechanical Engineer": "Mechanical Design",
            "Electrical Engineer": "Electrical Design",
            "Antenna Engineer":    "Antenna Design",
            "TT&C Engineer":       "TTC Design",
            "OBSW Engineer":       "OBSW Design",
        }
        section = section_map.get(agent_name, f"{agent_name} Output")
        self._save_section(section, result)
        self._log(f"  ✔ {agent_name} output updated in baseline")

        # Automatically propagate as a change if description provided
        if description:
            cr = ChangeRequest(
                cr_id=f"CR-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
                raised_by=agent_name,
                source_type=SourceType.SUBSYSTEM,
                title=f"{agent_name} updated their design",
                description=description,
                severity=Severity.MAJOR,
            )
            propagator = ChangePropagator(self.network, self.bus, self.output_dir)
            resolution = propagator.propagate(cr, self.session.get_context())
            self.session.add_change({"cr_id": cr.cr_id, "status": resolution.final_status})
            self.session.save()
            return resolution
        return result

    # ── Main entry point ─────────────────────────────────────────────────

    def start(
        self,
        from_agent: str,
        description: str = "",
        milestone: str = "",
        severity: str = "MAJOR",
        run_milestone_after: bool = False,
    ):
        """
        Universal start. Routes to the right pipeline based on from_agent.

        Args:
            from_agent:           Who is starting (any agent name, or "User")
            description:          What changed / the business objective / the task
            milestone:            For milestone mode: "SRR", "PDR", "CDR" etc.
            severity:             For change mode: CRITICAL / MAJOR / MINOR
            run_milestone_after:  Auto-run a milestone review after completing phases
        """
        self._log(f"\n{'═'*55}")
        self._log(f"  START FROM: {from_agent}")
        self._log(f"  Mode: {AGENT_ACTION_MAP.get(from_agent, {}).get('mode', 'CHANGE')}")
        if description:
            self._log(f"  {description[:80]}...")
        self._log(f"{'═'*55}\n")

        action = AGENT_ACTION_MAP.get(from_agent, {"mode": StartMode.CHANGE})
        mode = action["mode"]

        # ── FULL pipeline from top ────────────────────────────────────────
        if mode == StartMode.FULL:
            phase = action.get("phase", "0")

            if phase == "PROPOSAL":
                from orchestrator.proposal_pipeline import ProposalPipeline
                p = ProposalPipeline(
                    proposal_name=self.session.mission_name,
                    opportunity_description=description or self.session.business_objective,
                    output_dir=self.output_dir,
                )
                results = p.run()
                for k, v in results.items():
                    self.session.update(k, v)
                self.session.save()
                return results

            if phase == "RND":
                from orchestrator.rnd_pipeline import RnDPipeline
                p = RnDPipeline(
                    project_name=self.session.mission_name,
                    idea=description or self.session.business_objective,
                    output_dir=self.output_dir,
                )
                results = p.run()
                for k, v in results.items():
                    self.session.update(k, v)
                self.session.save()
                return results

            # Full mission pipeline — run from the specified phase onward
            if description:
                self.session.business_objective = description
            if from_agent == "User" or phase == "0":
                self._run_phase_0()
                self._run_phase_a()
                self._run_phase_b()
                self._run_phase_c()
                self._run_phase_d()
            elif phase == "A":
                self._run_phase_a()
                self._run_phase_b()
                self._run_phase_c()
                self._run_phase_d()
            elif phase == "B":
                self._run_phase_b()
                self._run_phase_c()
                self._run_phase_d()

        # ── SUBSYSTEM re-run ──────────────────────────────────────────────
        elif mode == StartMode.SUBSYSTEM:
            method = action.get("method", "")
            result = self._run_subsystem(from_agent, method, description)

            if run_milestone_after and self.session.last_milestone:
                self._log(f"\nRunning milestone review after subsystem update...")
                review = MilestoneReview(self.network, self.bus, self.output_dir)
                review.run(self.session.last_milestone, self.session.mission_name,
                           context=self.session.get_context(),
                           agents_override=[from_agent])
            return result

        # ── MILESTONE review ──────────────────────────────────────────────
        elif mode == StartMode.MILESTONE or milestone:
            target = milestone or action.get("default_milestone", "PDR")
            self.session.last_milestone = target
            self.session.save()
            reviewer = MilestoneReview(self.network, self.bus, self.output_dir)
            return reviewer.run(target, self.session.mission_name,
                                context=self.session.get_context())

        # ── CHANGE propagation ────────────────────────────────────────────
        else:  # StartMode.CHANGE or any unknown agent
            cr = ChangeRequest(
                cr_id=f"CR-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
                raised_by=from_agent,
                source_type=SourceType.SUBSYSTEM,
                title=description[:100] if description else f"Change from {from_agent}",
                description=description,
                severity=Severity[severity],
            )
            propagator = ChangePropagator(self.network, self.bus, self.output_dir)
            resolution = propagator.propagate(cr, self.session.get_context())
            self.session.add_change({"cr_id": cr.cr_id, "status": resolution.final_status})
            self.session.save()
            return resolution

        # Save final state
        self.session.save()
        self._log(f"\n✅ Start from '{from_agent}' complete.")
        self._log(f"Session saved: {self.session.summary()}")
