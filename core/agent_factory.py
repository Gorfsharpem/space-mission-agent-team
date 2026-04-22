"""
Agent Factory
-------------
Instantiates agents from config file.

Replaces the hardcoded per-pipeline instantiation blocks.
Each pipeline calls build_agent_roster(only=[...]) to get exactly
the agents it needs — no more, no less.
"""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

AGENTS_FILE = os.environ.get("AGENTS_FILE", "agents.json")

_AGENTS_CONFIG = Path(__file__).resolve().parent.parent / "config" / AGENTS_FILE


def build_agent_roster(
    only: list[str] | None = None,
    path: Path = _AGENTS_CONFIG,
) -> dict[str, "BaseAgent"]:
    """
    Instantiate agents from config and return a {name: agent} dict.

    Args:
        only: Optional list of agent names to instantiate.
              If None, all agents in config are instantiated.
              Names must match the 'name' field in AGENTS_FILE exactly.
        path: Path to AGENTS_FILE config. Defaults to config/agents.json.

    Returns:
        Dict mapping agent name → agent instance.

    Raises:
        FileNotFoundError: if AGENTS_FILE is missing.
        ValueError: if a name in `only` is not found in config.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Agent config not found at: {path}\n"
            "Expected for example: config/agents.json"
        )

    with path.open("r", encoding="utf-8") as f:
        data: dict = json.load(f)

    specs: list[dict] = [s for s in data["agents"] if not s.get("_comment")]

    # Validate the `only` filter against known names before instantiating anything
    if only is not None:
        known_names = {s["name"] for s in specs}
        unknown = set(only) - known_names
        if unknown:
            raise ValueError(
                f"build_agent_roster: unknown agent name(s) in `only`: {sorted(unknown)}\n"
                f"Known agents: {sorted(known_names)}"
            )
        specs = [s for s in specs if s["name"] in only]

    agents_module = importlib.import_module("agents")
    roster: dict[str, "BaseAgent"] = {}

    for spec in specs:
        cls = getattr(agents_module, spec["class"])
        agent = cls()                        # calls existing __init__, no changes to agent files
        # Override identity from config (works because _system_prompt reads at call time)
        agent.name      = spec["name"]
        agent.role      = spec["role"]
        agent.expertise = spec["expertise"]
        roster[spec["name"]] = agent

    return roster
