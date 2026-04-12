"""
Change Propagator
-----------------
The engine of the change management system.

Inspired by the gstack pattern:
  CEO review → Eng Manager review → specialists → QA → resolution

Our equivalent:
  Change raised → Impact map resolves affected agents →
  Each affected agent does a CRITICAL review (not rubber-stamp) →
  Mission Director adjudicates conflicts →
  QA/PA validates resolution →
  Document Manager updates baseline

The key design rule:
  Agents are ADVERSARIAL reviewers, not approvers.
  The system surfaces real disagreements so the Mission Director
  can make an informed engineering judgment call.
"""

from __future__ import annotations
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from core.change_request import ChangeRequest, Severity
from core.impact_map import ImpactMap
from core.message_bus import MessageBus

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent
    from core.agent_network import AgentNetwork


# ── Review result from a single agent ───────────────────────────────────────

@dataclass
class AgentReview:
    agent_name: str
    verdict: str          # ACCEPT / ACCEPT WITH CONDITIONS / REJECT
    review_text: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_markdown(self) -> str:
        return (
            f"### Review by {self.agent_name}\n"
            f"**Verdict:** {self.verdict}\n\n"
            f"{self.review_text}"
        )


# ── Full change resolution ───────────────────────────────────────────────────

@dataclass
class ChangeResolution:
    cr: ChangeRequest
    reviews: list[AgentReview] = field(default_factory=list)
    director_adjudication: str = ""
    qa_validation: str = ""
    final_status: str = "PENDING"   # APPROVED / APPROVED_WITH_CONDITIONS / REJECTED
    baseline_updates: dict[str, str] = field(default_factory=dict)

    def to_markdown(self) -> str:
        lines = [
            f"# Change Resolution Report\n",
            self.cr.to_markdown(),
            f"\n---\n\n## Agent Reviews ({len(self.reviews)} responses)\n",
        ]
        verdict_counts: dict[str, int] = {}
        for r in self.reviews:
            verdict_counts[r.verdict] = verdict_counts.get(r.verdict, 0) + 1
            lines.append(r.to_markdown())
            lines.append("\n---\n")

        lines.append(f"\n## Verdict Summary\n")
        for v, count in verdict_counts.items():
            lines.append(f"- **{v}**: {count} agent(s)")

        if self.director_adjudication:
            lines.append(f"\n## Mission Director Adjudication\n{self.director_adjudication}")

        if self.qa_validation:
            lines.append(f"\n## QA/PA Validation\n{self.qa_validation}")

        lines.append(f"\n## Final Status: **{self.final_status}**")

        if self.baseline_updates:
            lines.append("\n## Baseline Updates Required")
            for agent, update in self.baseline_updates.items():
                lines.append(f"\n### {agent}\n{update}")

        return "\n".join(lines)


# ── The propagator ───────────────────────────────────────────────────────────

class ChangePropagator:
    """
    Propagates a ChangeRequest through the team.

    Usage:
        propagator = ChangePropagator(network, bus, output_dir="outputs")
        resolution = propagator.propagate(change_request, mission_context)
    """

    def __init__(
        self,
        network: "AgentNetwork",
        bus: MessageBus,
        output_dir: str = "outputs",
    ):
        self.network = network
        self.bus = bus
        self.impact_map = ImpactMap()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _log(self, msg: str):
        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] {msg}")

    def _get_agent(self, name: str) -> "BaseAgent | None":
        return self.network._registry.get(name)

    def _collect_reviews(
        self,
        cr: ChangeRequest,
        affected_agents: list[str],
        mission_context: str,
        max_workers: int = 4,
    ) -> list[AgentReview]:
        """
        Run critical reviews in parallel across all affected agents.
        Each agent is an adversarial reviewer — not an approver.
        """
        reviews: list[AgentReview] = []

        def review_one(agent_name: str) -> AgentReview:
            agent = self._get_agent(agent_name)
            if agent is None:
                return AgentReview(
                    agent_name=agent_name,
                    verdict="NOT AVAILABLE",
                    review_text=f"Agent '{agent_name}' not found in network.",
                )

            self.bus.publish(
                sender="ChangePropagator",
                recipient=agent_name,
                topic="critical_review_request",
                content=f"CR {cr.cr_id}: {cr.title}",
            )

            review_text = agent.critical_review(cr, mission_context)

            # Extract verdict from the review text
            verdict = "ACCEPT"  # default
            upper = review_text.upper()
            if "REJECT" in upper:
                verdict = "REJECT"
            elif "ACCEPT WITH CONDITIONS" in upper or "CONDITIONAL" in upper:
                verdict = "ACCEPT WITH CONDITIONS"

            self.bus.publish(
                sender=agent_name,
                recipient="ChangePropagator",
                topic="critical_review_response",
                content=f"Verdict: {verdict}",
            )

            return AgentReview(
                agent_name=agent_name,
                verdict=verdict,
                review_text=review_text,
            )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(review_one, name): name for name in affected_agents}
            for future in as_completed(futures):
                name = futures[future]
                try:
                    review = future.result()
                    reviews.append(review)
                    self._log(f"  ✔ Review from {name}: {review.verdict}")
                except Exception as e:
                    self._log(f"  ✘ Review from {name} failed: {e}")

        return reviews

    def _director_adjudication(
        self,
        cr: ChangeRequest,
        reviews: list[AgentReview],
        mission_context: str,
    ) -> str:
        """
        Mission Director reads all reviews and makes the engineering judgment call.
        This is the CEO-review equivalent from gstack.
        """
        director = self._get_agent("Mission Director")
        if director is None:
            return "Mission Director not available."

        reviews_text = "\n\n---\n\n".join(r.to_markdown() for r in reviews)
        rejects = [r for r in reviews if r.verdict == "REJECT"]
        conditions = [r for r in reviews if r.verdict == "ACCEPT WITH CONDITIONS"]

        task = (
            f"You have received the following Change Request and {len(reviews)} critical "
            f"reviews from the engineering team. Your role is to adjudicate.\n\n"
            f"## Change Request\n\n{cr.to_markdown()}\n\n"
            f"## Engineering Reviews\n\n{reviews_text}\n\n"
            f"---\n\n"
            f"**Summary:** {len(rejects)} REJECT(s), "
            f"{len(conditions)} ACCEPT WITH CONDITIONS, "
            f"{len(reviews) - len(rejects) - len(conditions)} ACCEPT(s)\n\n"
            "As Mission Director, you must now:\n\n"
            "1. **Acknowledge the legitimate objections** — do not dismiss engineer concerns\n"
            "2. **Resolve conflicts** — where two subsystems have conflicting constraints, "
            "state which takes priority and why\n"
            "3. **Issue a Change Impact Notice (CIN)** — for each affected subsystem, "
            "state exactly what must change in their design\n"
            "4. **State your final recommendation** to the team: "
            "APPROVE / APPROVE WITH CONDITIONS / REJECT\n"
            "5. **If REJECT** — propose a modified version of the change that is feasible\n\n"
            "Be a leader, not a rubber stamp. If the change is wrong, say so."
        )
        return director.run(task, context=mission_context)

    def _qa_validation(
        self,
        cr: ChangeRequest,
        resolution: ChangeResolution,
        mission_context: str,
    ) -> str:
        """
        QA/PA validates that the change resolution is complete and traceable.
        """
        qa = self._get_agent("QA/PA Engineer")
        if qa is None:
            return "QA/PA Engineer not available."

        task = (
            f"A Change Request has been processed and adjudicated. "
            f"Validate the resolution before it is baselined.\n\n"
            f"## Change Request\n\n{cr.to_markdown()}\n\n"
            f"## Director Adjudication\n\n{resolution.director_adjudication}\n\n"
            f"## Number of Reviews\n{len(resolution.reviews)} agents reviewed\n\n"
            "Your validation checklist:\n"
            "1. **Traceability** — is the change traceable from requirement to affected subsystems?\n"
            "2. **Completeness** — are all impacted subsystems addressed in the resolution?\n"
            "3. **Open Items** — are there any unresolved objections that were dismissed without justification?\n"
            "4. **Verification** — what verification action must be added to the test plan to close this CR?\n"
            "5. **Document Update Required** — which baseline documents must be revised?\n"
            "6. **QA Verdict** — VALIDATED / VALIDATED WITH ACTIONS / HOLD\n"
        )
        return qa.run(task, context=mission_context)

    def _extract_baseline_updates(
        self,
        reviews: list[AgentReview],
        adjudication: str,
    ) -> dict[str, str]:
        """
        Derive which agents need to update their design outputs.
        Based on ACCEPT WITH CONDITIONS and REJECT reviews that were overridden.
        """
        updates: dict[str, str] = {}
        for review in reviews:
            if review.verdict in ("ACCEPT WITH CONDITIONS", "REJECT"):
                updates[review.agent_name] = (
                    f"Must update their design to address the concerns raised in their "
                    f"review (verdict: {review.verdict}). See adjudication for specific direction."
                )
        return updates

    def _save(self, resolution: ChangeResolution) -> str:
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        fname = f"{self.output_dir}/{ts}_change_resolution_{resolution.cr.cr_id}.md"
        with open(fname, "w") as f:
            f.write(resolution.to_markdown())
        self._log(f"  ✔ Change resolution saved → {fname}")
        return fname

    # ── Main entry point ────────────────────────────────────────────────

    def propagate(
        self,
        cr: ChangeRequest,
        mission_context: str = "",
        max_depth: int = 3,
    ) -> ChangeResolution:
        """
        Propagate a ChangeRequest through the full team.

        Steps:
          1. Resolve affected agents via ImpactMap
          2. Collect parallel critical reviews (adversarial)
          3. Mission Director adjudicates
          4. QA/PA validates
          5. Produce ChangeResolution with baseline update list
        """
        self._log(f"\n{'━'*55}")
        self._log(f"CHANGE PROPAGATION: {cr.cr_id} — {cr.title}")
        self._log(f"Raised by: {cr.raised_by} | Severity: {cr.severity.value}")
        self._log(f"{'━'*55}")

        # Step 1: Find affected agents
        affected = self.impact_map.all_impacts(cr.raised_by, max_depth=max_depth)
        # Don't ask the raiser to review their own change
        affected = [a for a in affected if a != cr.raised_by]
        # Remove management-only agents from technical reviews for subsystem CRs
        non_technical = {"Document Manager", "Project Controller", "Bid Manager", "Proposal Manager"}
        if cr.severity == Severity.MINOR:
            affected = [a for a in affected if a not in non_technical]

        self._log(f"Affected agents ({len(affected)}): {', '.join(affected)}")
        print()

        resolution = ChangeResolution(cr=cr)

        # Step 2: Parallel critical reviews
        self._log("Step 1/4 — Collecting critical reviews (agents are adversarial reviewers)...")
        resolution.reviews = self._collect_reviews(cr, affected, mission_context)

        # Step 3: Mission Director adjudication
        self._log("\nStep 2/4 — Mission Director adjudicating conflicts...")
        resolution.director_adjudication = self._director_adjudication(
            cr, resolution.reviews, mission_context
        )

        # Step 4: QA validation
        self._log("\nStep 3/4 — QA/PA validating resolution...")
        resolution.qa_validation = self._qa_validation(cr, resolution, mission_context)

        # Step 5: Determine final status and baseline updates
        upper_adj = resolution.director_adjudication.upper()
        if "REJECT" in upper_adj and "APPROVE" not in upper_adj:
            resolution.final_status = "REJECTED"
        elif "CONDITION" in upper_adj:
            resolution.final_status = "APPROVED_WITH_CONDITIONS"
        else:
            resolution.final_status = "APPROVED"

        resolution.baseline_updates = self._extract_baseline_updates(
            resolution.reviews, resolution.director_adjudication
        )

        cr.status = "RESOLVED"
        cr.resolution = resolution.final_status

        # Save and log
        self._log("\nStep 4/4 — Saving resolution...")
        self._save(resolution)

        self._log(f"\n{'━'*55}")
        self._log(f"RESOLUTION: {resolution.final_status}")
        self._log(f"Reviews: {len(resolution.reviews)} | "
                  f"Rejects: {sum(1 for r in resolution.reviews if r.verdict == 'REJECT')} | "
                  f"Conditions: {sum(1 for r in resolution.reviews if 'CONDITION' in r.verdict)}")
        self._log(f"Agents needing baseline update: {len(resolution.baseline_updates)}")
        self._log(f"{'━'*55}\n")

        return resolution
