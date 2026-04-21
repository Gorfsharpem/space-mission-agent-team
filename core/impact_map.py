"""
Impact Map
----------
Loads the directed dependency graph from DEPENDENCY_GRAPH_FILE.

Inspired by the HLA FOM approach: topology is declared externally,
not hardcoded in the execution layer. This allows team restructuring,
new pipelines, and mission-specific variants without touching Python source.

Description of the model behing the static dependency graph of the mission team.

When a change is raised by agent X, the Impact Map answers:
  "Which other agents are downstream of X and must review this change?"

The graph is DIRECTED: A → B means "a change in A has direct impact on B."
Transitive impacts are resolved automatically.

This is the core of the change propagation strategy.
"""


from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path


DEPENDENCY_GRAPH_FILE = os.environ.get("DEPENDENCY_GRAPH_FILE", "dependency_graph.json")

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / DEPENDENCY_GRAPH_FILE

def load_dependency_graph(path: Path = _CONFIG_PATH) -> dict[str, list[str]]:
    """Load and validate the dependency graph from a JSON config file."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dependency graph config not found at: {path}\n"
            "Expected for example: config/dependency_graph.json"
        )
    with path.open("r", encoding="utf-8") as f:
        data: dict = json.load(f)

    # Strip meta key if present
    graph = {k: v for k, v in data.items() if not k.startswith("_")}

    _validate_graph(graph)
    return graph


def _validate_graph(graph: dict[str, list[str]]) -> None:
    """Ensure all referenced agents exist as top-level keys."""
    all_agents = set(graph.keys())
    for source, targets in graph.items():
        for t in targets:
            if t not in all_agents:
                raise ValueError(
                    f"Dependency graph: agent '{t}' referenced as downstream of "
                    f"'{source}' but has no own entry. Add '{t}' as a key."
                )


# Cached singleton — loaded once at import time
DEPENDENCY_GRAPH: dict[str, list[str]] = load_dependency_graph()

class ImpactMap:
    """
    Resolves transitive downstream impact for any source agent: which agents are
    affected (directly or transitively) by a change originating from a given source agent. ?

    Usage:
        im = ImpactMap()
        affected = im.resolve("EPS Engineer")
        # → {"Thermal Engineer", "OBSW Engineer", "Electrical Engineer", ...}

    Resolves 
    """

    def __init__(self, graph: dict[str, list[str]] | None = None):
        self._graph = graph or DEPENDENCY_GRAPH

    @lru_cache(maxsize=None)
    def resolve(self, source_agent: str) -> frozenset[str]:
        """Return all agents transitively downstream of source_agent."""
        visited: set[str] = set()
        self._dfs(source_agent, visited)
        visited.discard(source_agent)
        return frozenset(visited)

    def _dfs(self, node: str, visited: set[str]) -> None:
        if node in visited:
            return
        visited.add(node)
        for neighbour in self._graph.get(node, []):
            self._dfs(neighbour, visited)

    def direct_downstream(self, source_agent: str) -> list[str]:
        """Return only direct (non-transitive) downstream agents."""
        return list(self._graph.get(source_agent, []))

    def all_agents(self) -> list[str]:
        return list(self._graph.keys())

    def direct_impacts(self, source: str) -> list[str]:
        return self._graph.get(source, [])

    def all_impacts(self, source: str, max_depth: int = 3) -> list[str]:
        """
        BFS to find all transitively affected agents, up to max_depth hops.
        Returns them in order: direct impacts first, then second-order, etc.
        Deduplicates and excludes the source itself.
        """
        visited: set[str] = set()
        queue: list[tuple[str, int]] = [(source, 0)]
        ordered: list[str] = []

        while queue:
            node, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            for neighbour in self._graph.get(node, []):
                if neighbour not in visited and neighbour != source:
                    visited.add(neighbour)
                    ordered.append(neighbour)
                    queue.append((neighbour, depth + 1))

        return ordered

    def impact_summary(self, source: str) -> str:
        direct = self.direct_impacts(source)
        all_imp = self.all_impacts(source)
        second = [a for a in all_imp if a not in direct]
        lines = [
            f"**Direct impacts** from `{source}`: {', '.join(direct) if direct else 'none'}",
            f"**Transitive impacts**: {', '.join(second) if second else 'none'}",
        ]
        return "\n".join(lines)
