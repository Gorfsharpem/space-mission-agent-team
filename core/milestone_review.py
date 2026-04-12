"""
Milestone Review
----------------
At any milestone (SRR, PDR, CDR, QR, AR, commissioning) every agent
produces their domain deliverables in parallel.

This is not a summary — each agent produces the actual artifact
a real engineer in that role would hand over at that review:
  - calculations with numbers
  - registers with itemised rows
  - budgets as tables
  - code as runnable snippets
  - dashboards with RAG status

The MilestoneReview collects all deliverables, QA/PA gates them,
and the Document Manager assembles the review package.
"""

from __future__ import annotations
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from core.deliverable import Deliverable, DeliverableType
from core.message_bus import MessageBus

if TYPE_CHECKING:
    from core.agent_network import AgentNetwork


# ── Milestone definitions ────────────────────────────────────────────────────

MILESTONE_DELIVERABLES: dict[str, dict[str, str]] = {
    # agent name → what they must produce at this milestone
    "SRR": {  # System Requirements Review
        "Mission Analyst":     "Orbital parameters table, delta-V budget, launch vehicle trade matrix",
        "Payload Engineer":    "Payload requirements derivation, performance budget, data volume estimate",
        "EPS Engineer":        "Preliminary power budget table with all loads and 20% margin",
        "ADCS Engineer":       "Pointing requirements derivation, disturbance torque estimates",
        "Thermal Engineer":    "Thermal environment definition, preliminary hot/cold case temperatures",
        "Structures Engineer": "Preliminary mass budget table, launch load factors, configuration sketch description",
        "Propulsion Engineer": "Delta-V budget table, propulsion trade (chemical vs electric vs cold gas)",
        "TT&C Engineer":       "Preliminary link budget table, ground station trade",
        "OBSW Engineer":       "Software requirements, OBC trade, FDIR concept",
        "Mechanical Engineer": "Mechanisms list with TRL, harness mass estimate",
        "Electrical Engineer": "Electrical architecture overview, grounding philosophy",
        "Antenna Engineer":    "Antenna trade matrix, preliminary gain budget",
        "QA/PA Engineer":      "Requirements compliance matrix, NCR register (open items), SRR gate checklist",
        "Project Controller":  "Phase A milestone tracker, resource loading table, cost-to-date",
        "Document Manager":    "DRL for Phase A/B, document status dashboard",
        "Mission Director":    "System requirements document summary, key design drivers, system budgets",
        "Project Manager":     "Project schedule (Phase A-E), risk register top-10, stakeholder map",
        "Safety Engineer":     "Initial hazard identification register, safety-critical functions list, launch range safety constraints",
        "Ground Segment Engineer": "Ground station trade matrix, CONOPS overview, mission control system options",
        "Launch Campaign Manager": "Launch vehicle trade summary, campaign schedule estimate, launch site options",
    },
    "PDR": {  # Preliminary Design Review
        "Mission Analyst":     "Updated MAR: final orbit selection, coverage analysis table, eclipse fraction calculation",
        "Payload Engineer":    "Payload preliminary design: performance table, ICD summary, calibration plan",
        "EPS Engineer":        "Power budget (detailed, all modes), solar array sizing calculation, battery sizing calculation, eclipse energy balance",
        "ADCS Engineer":       "Pointing error budget table, actuator sizing calculation, sensor selection table, momentum budget",
        "Thermal Engineer":    "Thermal control design: MLI coverage table, radiator sizing calculation, heater power register, hot/cold case temperature table",
        "Structures Engineer": "Mass budget table (component level), launch load analysis, CoM/CoI estimate, configuration description",
        "Propulsion Engineer": "Propulsion sizing: Tsiolkovsky calculation, propellant mass budget, tank sizing, plume impingement assessment",
        "TT&C Engineer":       "Link budget tables (TM/TC/ranging, worst-case), antenna coverage analysis, ground station contact schedule",
        "OBSW Engineer":       "Software architecture doc, FDIR state machine description, memory map, task list with periods",
        "Mechanical Engineer": "Harness routing plan, mechanisms design summary, tolerance stack-up table, contamination control plan",
        "Electrical Engineer": "Electrical architecture block description, grounding diagram description, harness mass/length estimate, EMC test plan",
        "Antenna Engineer":    "Antenna design table (all antennas: type/gain/beamwidth/mass), pattern analysis summary, feed network description",
        "QA/PA Engineer":      "PDR gate review report, NCR register, FMEA top-level extract, action item register",
        "Project Controller":  "EVM dashboard (BCWS/BCWP/ACWP/SPI/CPI), milestone tracker RAG, payment schedule table",
        "Document Manager":    "Updated DRL with status, configuration baseline definition, CCB log",
        "Mission Director":    "System integration review summary, interface matrix, system budget consolidation, go/no-go recommendation",
        "Project Manager":     "Updated risk register, schedule performance report, resource utilisation",
        "Safety Engineer":     "Safety analysis report: hazard register table, FTA description, safety-critical software items, orbital debris plan",
        "Ground Segment Engineer": "Ground segment design: station network table, MCS architecture, CONOPS phases table, simulator requirements",
        "Launch Campaign Manager": "Launch campaign plan: campaign schedule table, LV ICD summary, launch site requirements, LRR checklist",
    },
    "CDR": {  # Critical Design Review
        "Mission Analyst":     "Final MAR, disposal trajectory analysis, launch window analysis",
        "Payload Engineer":    "Payload CDR package: final performance predictions, test configuration, as-designed ICD",
        "EPS Engineer":        "Final power budget (all operating modes), battery depth-of-discharge analysis, harness losses calculation",
        "ADCS Engineer":       "Final pointing error budget, control law description, wheel desaturation analysis, FDIR modes",
        "Thermal Engineer":    "Final temperature predictions table, thermal balance test plan, heater algorithm description",
        "Structures Engineer": "Final mass budget, FEA results summary (fundamental frequency, stress), vibration test plan",
        "Propulsion Engineer": "Final propellant budget, thruster qualification status, feed system schematic description",
        "TT&C Engineer":       "Final link budgets (all bands, all geometries), CCSDS compliance checklist",
        "OBSW Engineer":       "Software design document summary, test coverage table, FDIR test scenarios, code metrics",
        "Mechanical Engineer": "Final harness list, mechanisms qualification status, assembly procedure list",
        "Electrical Engineer": "Final grounding and bonding plan, EMC test results summary, EIT procedure checklist",
        "Antenna Engineer":    "Final antenna design, pattern test results summary, deployment test plan",
        "QA/PA Engineer":      "CDR gate review report, NCR closure status, acceptance test plan, qualification status matrix",
        "Project Controller":  "Final EVM report, cost-at-completion forecast, invoices issued/paid/outstanding table",
        "Document Manager":    "CDR document package list, final DRL, drawing register",
        "Mission Director":    "CDR system status report, interface freeze confirmation, open items to close before QR",
        "Project Manager":     "Final risk register, lessons learned register, launch readiness assessment",
        "Safety Engineer":     "Final safety case: claim-argument-evidence, residual hazard register, software safety verification status",
        "Ground Segment Engineer": "Final ground segment design, operations readiness assessment, staff training plan",
        "Launch Campaign Manager": "Final launch campaign plan, countdown procedure, LEOP timeline, handover to operations checklist",
    },
}

# Default deliverable task for any milestone not in the map
DEFAULT_TASK = "Produce your domain deliverable for this milestone. Include all tables, calculations, registers, and analysis relevant to your subsystem at this stage."


# ── Milestone Review ─────────────────────────────────────────────────────────

@dataclass
class MilestonePackage:
    milestone: str
    mission_name: str
    deliverables: list[Deliverable] = field(default_factory=list)
    qa_gate_report: str = ""
    document_index: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_master_document(self) -> str:
        lines = [
            f"# {self.mission_name} — {self.milestone} Review Package",
            f"**Date:** {self.timestamp[:10]}  ",
            f"**Deliverables:** {len(self.deliverables)}  ",
            "",
            "---",
            "",
            "## Table of Contents",
            "",
        ]
        for i, d in enumerate(self.deliverables, 1):
            lines.append(f"{i}. [{d.title}](#{d.agent_name.lower().replace(' ', '-')}) — {d.agent_name}")

        lines.append("\n\n---\n")

        for d in self.deliverables:
            lines.append(d.to_markdown())
            lines.append("\n\n---\n")

        if self.qa_gate_report:
            lines.append("## QA/PA Gate Review\n")
            lines.append(self.qa_gate_report)
            lines.append("\n\n---\n")

        if self.document_index:
            lines.append("## Document Index\n")
            lines.append(self.document_index)

        return "\n".join(lines)


class MilestoneReview:
    """
    Runs a full milestone review: every agent produces their domain deliverables
    in parallel, QA/PA gates them, Document Manager assembles the package.
    """

    def __init__(self, network: "AgentNetwork", bus: MessageBus, output_dir: str = "outputs"):
        self.network = network
        self.bus = bus
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _log(self, msg: str):
        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] {msg}")

    def _get_agent(self, name: str):
        return self.network._registry.get(name)

    def _run_deliverable(
        self, agent_name: str, milestone: str, task: str, context: str
    ) -> Deliverable:
        agent = self._get_agent(agent_name)
        if agent is None:
            return Deliverable(
                agent_name=agent_name, milestone=milestone,
                title=f"{agent_name} — {milestone} deliverable",
                doc_type=DeliverableType.MARKDOWN,
                content=f"Agent not available in network.",
            )

        self.bus.publish("MilestoneReview", agent_name, "deliverable_request",
                         f"{milestone}: {task[:100]}")

        full_task = (
            f"You are producing your formal deliverable for the **{milestone}** review.\n\n"
            f"**Required deliverable:** {task}\n\n"
            "Requirements for this deliverable:\n"
            "- Use markdown tables wherever data is tabular (budgets, registers, link budgets, mass budgets)\n"
            "- Show calculations step by step with assumed values where real data is not yet available\n"
            "- For registers (NCR, risk, action items): use a table with ID | description | severity/status | owner | due date\n"
            "- For code deliverables: produce actual runnable Python or pseudocode with comments\n"
            "- Be quantitative — every design parameter needs a number with units and margin\n"
            "- Flag every assumption explicitly as [ASSUMPTION: ...]\n"
            "- Flag every open item as [OPEN: ...]\n"
            "- End with a **Confidence Level**: High / Medium / Low and brief justification\n"
        )

        content = agent.run(full_task, context=context)

        # Infer doc type from content
        doc_type = DeliverableType.MARKDOWN
        if "```python" in content or "```" in content:
            doc_type = DeliverableType.CODE
        elif content.count("|") > 20:
            doc_type = DeliverableType.TABLE
        elif any(kw in content.lower() for kw in ["ncr-", "risk-", "ai-", "action item"]):
            doc_type = DeliverableType.REGISTER
        elif any(kw in content.lower() for kw in ["= ", "kg", "w ", "m/s", "calculation"]):
            doc_type = DeliverableType.CALCULATION

        self.bus.publish(agent_name, "MilestoneReview", "deliverable_complete",
                         f"Produced {doc_type.value} for {milestone}")

        return Deliverable(
            agent_name=agent_name,
            milestone=milestone,
            title=f"{agent_name} — {milestone}",
            doc_type=doc_type,
            content=content,
            doc_id=f"{milestone}-{agent_name[:3].upper()}-001",
        )

    def run(
        self,
        milestone: str,
        mission_name: str,
        context: str = "",
        agents_override: list[str] | None = None,
        max_workers: int = 5,
    ) -> MilestonePackage:
        """
        Run a full milestone review. All agents produce deliverables in parallel.

        Args:
            milestone:       e.g. "PDR", "CDR", "SRR", or any custom string
            mission_name:    Name of the mission
            context:         Current mission baseline as markdown string
            agents_override: If set, only these agents produce deliverables
            max_workers:     Thread pool size
        """
        self._log(f"\n{'━'*55}")
        self._log(f"MILESTONE REVIEW: {milestone} — {mission_name}")
        self._log(f"{'━'*55}")

        # Determine which agents produce what
        deliverable_map = MILESTONE_DELIVERABLES.get(milestone, {})

        if agents_override:
            agent_list = agents_override
        else:
            # All registered agents that have a defined task, plus any extras in the network
            registered = set(self.network.list_agents())
            agent_list = [a for a in deliverable_map.keys() if a in registered]
            # Add any registered agents not in the standard map
            for name in registered:
                if name not in agent_list and name not in ("Document Manager", "QA/PA Engineer"):
                    agent_list.append(name)

        self._log(f"Agents producing deliverables: {len(agent_list)}")

        package = MilestonePackage(milestone=milestone, mission_name=mission_name)

        # Parallel deliverable production
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for agent_name in agent_list:
                task = deliverable_map.get(agent_name, DEFAULT_TASK)
                futures[executor.submit(
                    self._run_deliverable, agent_name, milestone, task, context
                )] = agent_name

            for future in as_completed(futures):
                name = futures[future]
                try:
                    deliverable = future.result()
                    package.deliverables.append(deliverable)
                    self._log(f"  ✔ {name} — {deliverable.doc_type.value}")
                except Exception as e:
                    self._log(f"  ✘ {name} failed: {e}")

        # Sort deliverables into a consistent order
        order = list(deliverable_map.keys())
        package.deliverables.sort(
            key=lambda d: order.index(d.agent_name) if d.agent_name in order else 999
        )

        # QA/PA gate review
        self._log(f"\n  Running QA/PA gate review...")
        qa = self._get_agent("QA/PA Engineer")
        if qa:
            deliverables_summary = "\n\n".join(
                f"**{d.agent_name}** ({d.doc_type.value}): {d.content[:300]}..."
                for d in package.deliverables
            )
            package.qa_gate_report = qa.phase_gate_review(milestone, deliverables_summary)

        # Document Manager index
        self._log(f"  Building document index...")
        doc_mgr = self._get_agent("Document Manager")
        if doc_mgr:
            doc_dict = {d.title: d.content[:200] for d in package.deliverables}
            package.document_index = doc_mgr.build_document_tree(
                f"{mission_name} {milestone}", doc_dict
            )

        # Save master document
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        fname = f"{self.output_dir}/{ts}_{milestone}_review_package.md"
        with open(fname, "w") as f:
            f.write(package.to_master_document())
        self._log(f"\n  ✔ {milestone} package saved → {fname}")

        # Save individual deliverables
        for d in package.deliverables:
            ind_fname = f"{self.output_dir}/{ts}_{milestone}_{d.filename()}"
            with open(ind_fname, "w") as f:
                f.write(d.to_markdown())

        self._log(f"\n✅ {milestone} complete — {len(package.deliverables)} deliverables")
        return package
