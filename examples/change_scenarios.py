"""
Example Change Scenarios
========================
Ready-to-run examples showing the change propagation system in action.

Run any scenario directly:
    python examples/change_scenarios.py --scenario propulsion
    python examples/change_scenarios.py --scenario lifetime
    python examples/change_scenarios.py --scenario payload_mass
    python examples/change_scenarios.py --scenario business_objective
    python examples/change_scenarios.py --list
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from core import (
    MessageBus, AgentNetwork,
    ChangeRequest, Severity, SourceType,
    ChangePropagator,
)
from agents import (
    MissionDirectorAgent, ProjectManagerAgent, MissionAnalysisAgent,
    PayloadAgent, EPSAgent, ADCSAgent, ThermalAgent, StructuresAgent,
    TTCAgent, OBSWAgent, PropulsionAgent, MechanicalAgent,
    ElectricalAgent, AntennaAgent, QAPAAgent, DocumentManagerAgent,
    ProjectControllerAgent, RnDManagerAgent, ProposalManagerAgent, BidManagerAgent,
)


# ── Scenario definitions ─────────────────────────────────────────────────────

SCENARIOS = {
    "propulsion": ChangeRequest(
        cr_id="CR-001",
        raised_by="Propulsion Engineer",
        source_type=SourceType.SUBSYSTEM,
        title="Switch from hydrazine monoprop to cold gas N2 thruster",
        severity=Severity.MAJOR,
        description=(
            "REACH regulation compliance review has flagged hydrazine as unavailable "
            "for this mission class under current procurement rules. "
            "Proposing a switch to cold gas nitrogen thrusters.\n\n"
            "Key impacts I have already identified:\n"
            "- Delta-V capability drops from 150 m/s to 80 m/s (Isp: 220s → 65s)\n"
            "- Propellant mass for equivalent performance increases significantly\n"
            "- Thruster footprint is similar but tank pressure is lower (250 bar → 50 bar)\n"
            "- Plume contamination risk is reduced\n\n"
            "I need all affected subsystems to review whether 80 m/s delta-V is still "
            "sufficient for their needs, and whether the mission is still viable."
        ),
    ),

    "lifetime": ChangeRequest(
        cr_id="CR-002",
        raised_by="User",
        source_type=SourceType.BUSINESS,
        title="Mission operational lifetime extended from 3 years to 5 years",
        severity=Severity.CRITICAL,
        description=(
            "The customer has formally requested an extension of the operational lifetime "
            "from 3 years to 5 years. This is a binding contractual change.\n\n"
            "Immediate implications I can foresee:\n"
            "- All consumables (propellant, battery cycles) must be re-budgeted for 5 years\n"
            "- Solar array degradation at EOL changes (3yr BOL→EOL vs 5yr BOL→EOL)\n"
            "- Radiation dose increases significantly for LEO at 5 years\n"
            "- All components must demonstrate 5-year qualification or have design margins\n"
            "- Disposal orbit calculation changes\n\n"
            "Each subsystem must assess whether their current design can support 5 years "
            "or what design changes are required. Do not simply agree — if 5 years is "
            "infeasible for your subsystem with the current design, state it clearly."
        ),
    ),

    "payload_mass": ChangeRequest(
        cr_id="CR-003",
        raised_by="Payload Engineer",
        source_type=SourceType.SUBSYSTEM,
        title="Payload mass increased from 12 kg to 18 kg; resolution upgrade to 2m GSD",
        severity=Severity.MAJOR,
        description=(
            "Following detailed optical design, the payload mass has increased from "
            "12 kg to 18 kg (+6 kg, +50%) due to a larger primary mirror needed to "
            "achieve 2m GSD (previously 5m GSD in the requirement).\n\n"
            "Payload changes:\n"
            "- Mass: 12 kg → 18 kg\n"
            "- Volume: 400x400x600 mm → 500x500x800 mm\n"
            "- Peak power: 45 W → 65 W\n"
            "- Data rate: 300 Mbps → 800 Mbps (higher resolution raw data)\n"
            "- Pointing requirement: 0.1 deg → 0.02 deg (tighter for 2m GSD)\n\n"
            "I expect significant pushback from structures (mass), EPS (power), "
            "ADCS (pointing), TTC (data rate), and OBSW (storage). "
            "I need each subsystem to tell me if they can absorb these changes or not."
        ),
    ),

    "business_objective": ChangeRequest(
        cr_id="CR-004",
        raised_by="User",
        source_type=SourceType.BUSINESS,
        title="New requirement: dual-band (optical + SAR) capability added to mission",
        severity=Severity.CRITICAL,
        description=(
            "The business team has signed a new customer agreement requiring the "
            "satellite to carry both an optical imager (existing) AND a synthetic "
            "aperture radar (SAR) payload operating at X-band.\n\n"
            "This is a new top-level user requirement, not optional.\n\n"
            "SAR preliminary specs from the customer:\n"
            "- Frequency: X-band (9.6 GHz)\n"
            "- Resolution: 1m (Spotlight mode), 5m (Stripmap)\n"
            "- Peak power: 1.5 kW (transmit pulse)\n"
            "- Average power: 300 W\n"
            "- Antenna: deployable 3m x 0.3m panel\n"
            "- Mass estimate: 35 kg (antenna + electronics)\n\n"
            "This is a major change. I need every subsystem to critically assess "
            "whether this is even feasible on the current platform, or whether "
            "we need a complete redesign. Do not agree without evidence."
        ),
    ),

    "orbit": ChangeRequest(
        cr_id="CR-005",
        raised_by="Mission Analyst",
        source_type=SourceType.SYSTEM,
        title="Orbit altitude reduced from 550 km to 450 km to improve resolution",
        severity=Severity.MAJOR,
        description=(
            "Mission analysis review has identified that reducing altitude from 550 km "
            "to 450 km improves ground resolution by 18% and reduces revisit time.\n\n"
            "However, the 450 km orbit has the following engineering consequences:\n"
            "- Atmospheric drag is significantly higher → propellant for station-keeping "
            "  increases from 8 kg to ~22 kg\n"
            "- Eclipse fraction increases slightly\n"
            "- Van Allen belt proton flux is higher at lower altitude (radiation dose up ~15%)\n"
            "- Launch vehicle insertion delta-V is lower (slight saving)\n"
            "- Orbital lifetime without propulsion is reduced from 25 years to 5 years "
            "  (disposal compliance maintained)\n\n"
            "I am proposing this as a system-level trade. I need other subsystems to "
            "challenge this if the consequences make it infeasible."
        ),
    ),
}


def build_network():
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


def run_scenario(name: str, output_dir: str = "outputs"):
    if name not in SCENARIOS:
        print(f"Unknown scenario: {name}. Use --list to see options.")
        return

    cr = SCENARIOS[name]
    print(f"\n{'═'*60}")
    print(f"  SCENARIO: {name.upper()}")
    print(f"  CR: {cr.cr_id} | From: {cr.raised_by} | {cr.severity.value}")
    print(f"  {cr.title}")
    print(f"{'═'*60}\n")

    network, bus = build_network()
    propagator = ChangePropagator(network, bus, output_dir=output_dir)
    resolution = propagator.propagate(cr, mission_context="", max_depth=2)

    print(f"\nScenario '{name}' complete.")
    print(f"Final status: {resolution.final_status}")
    print(f"Total inter-agent messages: {len(bus)}")


def main():
    parser = argparse.ArgumentParser(description="Run example change scenarios")
    parser.add_argument("--scenario", choices=list(SCENARIOS.keys()) + ["all"],
                        help="Scenario to run")
    parser.add_argument("--list", action="store_true", help="List available scenarios")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    if args.list:
        print("\nAvailable scenarios:")
        for name, cr in SCENARIOS.items():
            print(f"  {name:25} {cr.cr_id} | {cr.severity.value:10} | {cr.title}")
        return

    if args.scenario == "all":
        for name in SCENARIOS:
            run_scenario(name, args.output_dir)
    elif args.scenario:
        run_scenario(args.scenario, args.output_dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
