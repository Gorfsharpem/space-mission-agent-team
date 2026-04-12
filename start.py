"""
start.py — Universal Entry Point
=================================
Start from ANYWHERE. The system routes intelligently.

────────────────────────────────────────────────────────────────────────
EXAMPLES
────────────────────────────────────────────────────────────────────────

  # 1. Start a brand new mission from business objectives (full pipeline)
  python start.py --from User \\
      --mission "AGRI-SAT-1" \\
      --description "Provide daily global agricultural imagery, 3yr lifetime, 100M EUR"

  # 2. Start from Mission Director (skip Phase 0, run from Phase A onward)
  python start.py --from "Mission Director" \\
      --description "Mission lifetime is 5 years, EO mission, LEO 550km"

  # 3. Start from a subsystem — Propulsion Engineer changes their design
  python start.py --from "Propulsion Engineer" \\
      --description "Switching from hydrazine to cold gas. Delta-V drops 150→80 m/s."

  # 4. Run a full milestone review (all agents produce their domain deliverables)
  python start.py --milestone PDR --mission "AGRI-SAT-1"
  python start.py --milestone SRR --mission "AGRI-SAT-1"
  python start.py --milestone CDR --mission "AGRI-SAT-1"

  # 5. One agent re-runs their deliverable at a milestone
  python start.py --from "EPS Engineer" --milestone PDR \\
      --description "Updated power budget after payload mass increase"

  # 6. Propagate a critical business change through the whole team
  python start.py --from User --severity CRITICAL \\
      --description "Customer added SAR payload requirement. Peak power 1.5kW. Mass 35kg."

  # 7. Resume from saved session (continue from where you left off)
  python start.py --resume

  # 8. Show session state
  python start.py --status

  # 9. List all agents and what starting from each one does
  python start.py --list-agents

────────────────────────────────────────────────────────────────────────
"""

import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from core.message_bus import MessageBus
from core.agent_network import AgentNetwork
from core.session_state import SessionState
from core.universal_start import UniversalStartEngine, AGENT_ACTION_MAP, StartMode
from core.milestone_review import MilestoneReview, MILESTONE_DELIVERABLES

from agents import (
    MissionDirectorAgent, ProjectManagerAgent, MissionAnalysisAgent,
    PayloadAgent, EPSAgent, ADCSAgent, ThermalAgent, StructuresAgent,
    TTCAgent, OBSWAgent, PropulsionAgent, MechanicalAgent,
    ElectricalAgent, AntennaAgent, QAPAAgent, DocumentManagerAgent,
    ProjectControllerAgent, RnDManagerAgent, ProposalManagerAgent, BidManagerAgent,
)


OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "outputs")


def build_network(session: SessionState) -> tuple[AgentNetwork, MessageBus]:
    bus = MessageBus()
    network = AgentNetwork(bus)
    agents = [
        MissionDirectorAgent(), ProjectManagerAgent(), MissionAnalysisAgent(),
        PayloadAgent(), EPSAgent(), ADCSAgent(), ThermalAgent(), StructuresAgent(),
        TTCAgent(), OBSWAgent(), PropulsionAgent(), MechanicalAgent(),
        ElectricalAgent(), AntennaAgent(), QAPAAgent(), DocumentManagerAgent(),
        ProjectControllerAgent(), RnDManagerAgent(), ProposalManagerAgent(), BidManagerAgent(),
    ]
    for agent in agents:
        agent.network = network
        network.register(agent)
    return network, bus


def main():
    parser = argparse.ArgumentParser(
        description="Space Mission Agent Team — Universal Start",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # ── Core args ────────────────────────────────────────────────────────
    parser.add_argument(
        "--from", dest="from_agent", metavar="AGENT",
        help="Which agent to start from (or 'User' for business level)",
    )
    parser.add_argument(
        "--description", "-d",
        help="What changed, the business objective, or the task",
    )
    parser.add_argument(
        "--mission", "-m",
        help="Mission name (used for new missions or to override session name)",
    )
    parser.add_argument(
        "--milestone",
        choices=list(MILESTONE_DELIVERABLES.keys()) + ["CUSTOM"],
        help="Run a milestone review (SRR / PDR / CDR)",
    )
    parser.add_argument(
        "--severity",
        choices=["CRITICAL", "MAJOR", "MINOR"],
        default="MAJOR",
        help="Change severity (for change propagation mode, default: MAJOR)",
    )
    parser.add_argument(
        "--milestone-after",
        action="store_true",
        help="After a subsystem update, also re-run the last milestone review for that agent",
    )
    parser.add_argument(
        "--output-dir", default=OUTPUT_DIR,
        help=f"Output directory (default: {OUTPUT_DIR})",
    )

    # ── Info / utility args ──────────────────────────────────────────────
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume from saved session state",
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Show current session state and exit",
    )
    parser.add_argument(
        "--list-agents", action="store_true",
        help="List all agents and what starting from each one does",
    )
    parser.add_argument(
        "--clear-session", action="store_true",
        help="Clear session state and start fresh",
    )

    args = parser.parse_args()

    # ── Utility modes ────────────────────────────────────────────────────
    if args.list_agents:
        print("\nAll agents and their start behaviour:\n")
        print(f"{'Agent':<28} {'Mode':<12} {'Details'}")
        print("─" * 70)
        for name, action in sorted(AGENT_ACTION_MAP.items()):
            mode = action["mode"].value
            detail = action.get("phase", action.get("method", action.get("default_milestone", "")))
            print(f"{name:<28} {mode:<12} {detail}")
        print("\nAny agent NOT in this list → CHANGE propagation mode")
        return

    if args.clear_session:
        from core.session_state import SESSION_FILE
        if os.path.isfile(SESSION_FILE):
            os.remove(SESSION_FILE)
            print("Session cleared.")
        else:
            print("No session to clear.")
        return

    # ── Load session ──────────────────────────────────────────────────────
    session = SessionState.load()

    if args.mission:
        session.mission_name = args.mission

    if args.status:
        print(f"\n{'═'*50}")
        print("  SESSION STATE")
        print(f"{'═'*50}")
        print(session.summary())
        if session.results:
            print(f"\nBaseline sections:")
            for k in session.results:
                print(f"  • {k} ({len(session.results[k])} chars)")
        if session.change_log:
            print(f"\nChange log:")
            for cr in session.change_log[-5:]:
                print(f"  • {cr['cr_id']}: {cr['status']}")
        return

    # ── Resume mode ───────────────────────────────────────────────────────
    if args.resume:
        print(f"\nResuming session: {session.mission_name}")
        print(session.summary())
        from_agent = args.from_agent or input("\nStart from which agent? > ").strip()
        description = args.description or input("Description (or Enter to skip): ").strip()
        args.from_agent = from_agent
        args.description = description

    # ── Validate ──────────────────────────────────────────────────────────
    if not args.from_agent and not args.milestone:
        parser.error(
            "Specify --from AGENT_NAME (to start from an agent) "
            "or --milestone MILESTONE (to run a milestone review).\n"
            "Use --list-agents to see all options."
        )

    # ── Build network ─────────────────────────────────────────────────────
    print(f"\nBuilding agent network ({session.mission_name})...")
    network, bus = build_network(session)
    engine = UniversalStartEngine(network, bus, session, output_dir=args.output_dir)

    # ── Milestone-only mode (no --from) ───────────────────────────────────
    if args.milestone and not args.from_agent:
        print(f"\nRunning {args.milestone} milestone review for {session.mission_name}...")
        reviewer = MilestoneReview(network, bus, args.output_dir)
        session.last_milestone = args.milestone
        session.save()
        package = reviewer.run(
            milestone=args.milestone,
            mission_name=session.mission_name,
            context=session.get_context(),
        )
        print(f"\n✅ {args.milestone} review complete — {len(package.deliverables)} deliverables")
        print(f"   QA gate: {package.qa_gate_report[:120] if package.qa_gate_report else 'N/A'}...")
        return

    # ── Universal start ───────────────────────────────────────────────────
    engine.start(
        from_agent=args.from_agent,
        description=args.description or "",
        milestone=args.milestone or "",
        severity=args.severity,
        run_milestone_after=args.milestone_after,
    )


if __name__ == "__main__":
    main()
