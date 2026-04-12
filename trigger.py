"""
Change Management Trigger
--------------------------
Trigger a change from any point in the system.
The propagator resolves who is affected, forces critical reviews,
and produces a resolution with baseline update instructions.

Usage:
    python trigger.py --source "Propulsion Engineer" \\
                      --severity MAJOR \\
                      --title "Switch from hydrazine to cold gas thruster" \\
                      --description "Due to REACH regulation, hydrazine is not available. \\
                                     Proposing switch to cold gas N2. Delta-V drops from \\
                                     150 m/s to 80 m/s. Isp drops from 220s to 65s."

    python trigger.py --source "User" \\
                      --severity CRITICAL \\
                      --title "Mission lifetime extended from 3 to 5 years" \\
                      --description "Customer has requested a 5-year operational lifetime. \\
                                     This was previously 3 years in the business objective."

    python trigger.py --source "Payload Engineer" \\
                      --severity MAJOR \\
                      --title "Payload mass increased from 12 kg to 18 kg" \\
                      --description "New imaging module requires 18 kg, up from 12 kg baseline. \\
                                     Resolution increased from 5m to 2m GSD."

    python trigger.py --list-agents    # shows all registered agents
    python trigger.py --list-impacts "Propulsion Engineer"  # shows who is affected
"""

import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from core import (
    MessageBus, AgentNetwork,
    ChangeRequest, Severity, SourceType,
    ImpactMap, ChangePropagator,
)
from agents import (
    MissionDirectorAgent, ProjectManagerAgent, MissionAnalysisAgent,
    PayloadAgent, EPSAgent, ADCSAgent, ThermalAgent, StructuresAgent,
    TTCAgent, OBSWAgent, PropulsionAgent, MechanicalAgent,
    ElectricalAgent, AntennaAgent, QAPAAgent, DocumentManagerAgent,
    ProjectControllerAgent, RnDManagerAgent, ProposalManagerAgent, BidManagerAgent,
)


def build_network() -> tuple[AgentNetwork, MessageBus]:
    """Instantiate and register all agents in the network."""
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


def infer_source_type(source: str) -> SourceType:
    if source in ("User", "Project Manager", "Bid Manager", "Proposal Manager"):
        return SourceType.BUSINESS
    if source in ("Mission Director",):
        return SourceType.SYSTEM
    return SourceType.SUBSYSTEM


def main():
    parser = argparse.ArgumentParser(
        description="Trigger a change request and propagate it through the mission team.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--source",      help="Agent name raising the change (or 'User')")
    parser.add_argument("--severity",    choices=["CRITICAL", "MAJOR", "MINOR"], default="MAJOR")
    parser.add_argument("--title",       help="One-line change title")
    parser.add_argument("--description", help="Full description of the change and reason")
    parser.add_argument("--cr-id",       default=None, help="Optional CR ID (auto-generated if omitted)")
    parser.add_argument("--context",     default="", help="Path to a .md file with mission baseline context")
    parser.add_argument("--output-dir",  default="outputs")
    parser.add_argument("--max-depth",   type=int, default=2,
                        help="How many hops in the dependency graph to follow (default: 2)")
    parser.add_argument("--list-agents", action="store_true", help="List all registered agents and exit")
    parser.add_argument("--list-impacts", metavar="AGENT_NAME",
                        help="Show impact map for a given agent name and exit")

    args = parser.parse_args()

    # ── Info modes ──────────────────────────────────────────────────────
    if args.list_agents:
        network, _ = build_network()
        print("\nRegistered agents:")
        for name in sorted(network.list_agents()):
            print(f"  • {name}")
        return

    if args.list_impacts:
        impact_map = ImpactMap()
        print(f"\nDirect impacts from '{args.list_impacts}':")
        for a in impact_map.direct_impacts(args.list_impacts):
            print(f"  → {a}")
        print(f"\nAll transitive impacts (depth 3):")
        for a in impact_map.all_impacts(args.list_impacts):
            print(f"  ⇝ {a}")
        return

    # ── Validate required args for propagation ───────────────────────────
    if not all([args.source, args.title, args.description]):
        parser.error("--source, --title, and --description are required for change propagation.")

    # ── Load optional baseline context ───────────────────────────────────
    mission_context = ""
    if args.context and os.path.isfile(args.context):
        with open(args.context) as f:
            mission_context = f.read()
        print(f"Loaded mission context from {args.context} ({len(mission_context)} chars)")

    # ── Build the network ─────────────────────────────────────────────────
    network, bus = build_network()

    # ── Build the change request ──────────────────────────────────────────
    from datetime import datetime
    cr_id = args.cr_id or f"CR-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    cr = ChangeRequest(
        cr_id=cr_id,
        raised_by=args.source,
        source_type=infer_source_type(args.source),
        title=args.title,
        description=args.description,
        severity=Severity[args.severity],
    )

    print(f"\n{'═'*55}")
    print(f"  CHANGE REQUEST: {cr_id}")
    print(f"  From: {cr.raised_by} | Severity: {cr.severity.value}")
    print(f"  {cr.title}")
    print(f"{'═'*55}\n")

    # ── Show impact map preview ───────────────────────────────────────────
    impact_map = ImpactMap()
    affected = impact_map.all_impacts(cr.raised_by, max_depth=args.max_depth)
    affected = [a for a in affected if a != cr.raised_by]
    print(f"Impact map (depth {args.max_depth}):")
    for a in affected:
        print(f"  ⇝ {a}")
    print()

    # ── Propagate ─────────────────────────────────────────────────────────
    propagator = ChangePropagator(network, bus, output_dir=args.output_dir)
    resolution = propagator.propagate(cr, mission_context, max_depth=args.max_depth)

    print(f"\nFinal status: {resolution.final_status}")
    print(f"Inter-agent messages: {len(bus)}")
    if resolution.baseline_updates:
        print(f"\nSubsystems requiring baseline update:")
        for agent in resolution.baseline_updates:
            print(f"  • {agent}")


if __name__ == "__main__":
    main()
