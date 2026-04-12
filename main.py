"""
Space Mission Agent Team — Entry Point
=======================================
Three pipelines available:

  1. MissionPipeline   — full mission lifecycle (Phase 0 → commissioning)
  2. RnDPipeline       — R&D/innovation project (idea → exploitation)
  3. ProposalPipeline  — bid lifecycle (opportunity → contract)

Configure via environment variables or edit the sections below.

Usage:
    python main.py                        # runs mission pipeline (default)
    python main.py --pipeline rnd         # runs R&D pipeline
    python main.py --pipeline proposal    # runs proposal pipeline
    python main.py --pipeline all         # runs all three
"""

import os
import argparse
from dotenv import load_dotenv

load_dotenv()

from orchestrator import MissionPipeline, RnDPipeline, ProposalPipeline


# ── Mission Pipeline Config ──────────────────────────────────────────────────
MISSION_NAME = os.environ.get("MISSION_NAME", "DEMO-SAT-1")

BUSINESS_OBJECTIVE = os.environ.get(
    "BUSINESS_OBJECTIVE",
    (
        "Develop and operate a small satellite that provides daily, global, "
        "medium-resolution optical imagery of agricultural land to support "
        "precision farming analytics services. The satellite must be operational "
        "within 3 years, fit within a 100M EUR total mission cost, and achieve "
        "a minimum 3-year operational lifetime."
    ),
)

# ── R&D Pipeline Config ──────────────────────────────────────────────────────
RND_PROJECT_NAME = os.environ.get("RND_PROJECT_NAME", "DEMO-RND-001")

RND_IDEA = os.environ.get(
    "RND_IDEA",
    (
        "Develop a miniaturised Hall-effect thruster (< 0.5 kg, < 5 W input power) "
        "suitable for 6U CubeSats, capable of delivering 50 m/s delta-V to a 6 kg spacecraft, "
        "targeting TRL 5 at project completion."
    ),
)

# ── Proposal Pipeline Config ─────────────────────────────────────────────────
PROPOSAL_NAME = os.environ.get("PROPOSAL_NAME", "DEMO-PROPOSAL-001")

OPPORTUNITY = os.environ.get(
    "OPPORTUNITY",
    (
        "ESA Earth Observation Fast Track opportunity: supply a 100 kg class Earth "
        "observation satellite with 5m GSD optical imaging capability, 3-year lifetime, "
        "launch within 24 months of contract award. Budget envelope: 25M EUR. "
        "Evaluation criteria: technical merit (50%), schedule credibility (25%), price (25%)."
    ),
)


# ── Runner ───────────────────────────────────────────────────────────────────

def run_mission():
    print("\n" + "═" * 60)
    print("  MISSION PIPELINE")
    print("═" * 60 + "\n")
    pipeline = MissionPipeline(
        mission_name=MISSION_NAME,
        business_objective=BUSINESS_OBJECTIVE,
        output_dir="outputs",
    )
    pipeline.run()


def run_rnd():
    print("\n" + "═" * 60)
    print("  R&D PIPELINE")
    print("═" * 60 + "\n")
    pipeline = RnDPipeline(
        project_name=RND_PROJECT_NAME,
        idea=RND_IDEA,
        output_dir="outputs",
    )
    pipeline.run()


def run_proposal():
    print("\n" + "═" * 60)
    print("  PROPOSAL PIPELINE")
    print("═" * 60 + "\n")
    pipeline = ProposalPipeline(
        proposal_name=PROPOSAL_NAME,
        opportunity_description=OPPORTUNITY,
        output_dir="outputs",
    )
    pipeline.run()


def main():
    parser = argparse.ArgumentParser(description="Space Mission Agent Team")
    parser.add_argument(
        "--pipeline",
        choices=["mission", "rnd", "proposal", "all"],
        default="mission",
        help="Which pipeline to run (default: mission)",
    )
    args = parser.parse_args()

    if args.pipeline == "mission":
        run_mission()
    elif args.pipeline == "rnd":
        run_rnd()
    elif args.pipeline == "proposal":
        run_proposal()
    elif args.pipeline == "all":
        run_mission()
        run_rnd()
        run_proposal()


if __name__ == "__main__":
    main()
