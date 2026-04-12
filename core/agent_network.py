"""
Agent Network
-------------
Central registry of all instantiated agents.
Enables any agent to query any other agent by name,
creating the inter-agent "talking" behaviour.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent
from core.message_bus import MessageBus


class AgentNetwork:
    """
    Registry of all agents in the mission team.
    Agents register themselves on instantiation when given a network reference.

    Usage inside any agent:
        response = self.network.ask("EPS Engineer", "What is the power budget?", context)
    """

    def __init__(self, bus: MessageBus):
        self.bus = bus
        self._registry: dict[str, "BaseAgent"] = {}

    def register(self, agent: "BaseAgent"):
        self._registry[agent.name] = agent

    def ask(self, requester: "BaseAgent", target_name: str, question: str, context: str = "") -> str:
        """
        Route a question from one agent to another by name.
        Logs the exchange on the message bus.
        """
        target = self._registry.get(target_name)
        if target is None:
            available = ", ".join(self._registry.keys())
            raise ValueError(
                f"Agent '{target_name}' not found in network. Available: {available}"
            )

        self.bus.publish(
            sender=requester.name,
            recipient=target_name,
            topic="inter-agent query",
            content=question,
        )

        response = target.run(question, context=context)

        self.bus.publish(
            sender=target_name,
            recipient=requester.name,
            topic="inter-agent response",
            content=response[:500] + "..." if len(response) > 500 else response,
        )

        return response

    def list_agents(self) -> list[str]:
        return list(self._registry.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._registry
