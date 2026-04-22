"""
Base Agent
----------
All subsystem and system-level agents inherit from this class.
Supports:
  - inter-agent communication via AgentNetwork
  - critical change review via CriticalReviewMixin
"""

from __future__ import annotations
import os
from typing import TYPE_CHECKING

from core.critical_review import CriticalReviewMixin
from providers.factory import build_provider
from settings import MAX_TOKENS

if TYPE_CHECKING:
    from core.agent_network import AgentNetwork
    from core.change_request import ChangeRequest


class BaseAgent(CriticalReviewMixin):
    MODEL = "claude-sonnet-4-20250514"

    def __init__(self, name: str, role: str, expertise: str):
        self.name = name
        self.role = role
        self.expertise = expertise
        self.provider = build_provider()
        self.network: "AgentNetwork | None" = None  # injected by pipeline

    def _model(self) -> str:
        return os.environ.get("LLM_MODEL", self.MODEL)

    def _system_prompt(self) -> str:
        return (
            f"You are {self.name}, a highly experienced {self.role} on a space mission team.\n"
            f"Your expertise covers: {self.expertise}.\n\n"
            "You produce structured, technically accurate, and concise engineering outputs.\n"
            "Always format your response with clear section headers using markdown.\n"
            "Be specific with numbers, trade-offs, and assumptions where relevant.\n"
            "Flag open items and risks clearly.\n"
            "When referencing inputs from other team members, acknowledge them explicitly.\n\n"
            "CRITICAL BEHAVIOUR: You are an expert with strong technical opinions. "
            "You do not rubber-stamp proposals. When reviewing changes, you push back "
            "if something is technically unsound, even if it comes from senior management."
        )

    def run(self, task: str, context: str = "") -> str:
        user_message = task
        if context:
            user_message = f"## Mission Context\n\n{context}\n\n---\n\n## Your Task\n\n{task}"

        return self.provider.generate(
            system=self._system_prompt(),
            user=user_message,
            model=self._model(),
            max_tokens=MAX_TOKENS,
        )

    def ask_agent(self, target_name: str, question: str, context: str = "") -> str:
        if self.network is None:
            raise RuntimeError(
                f"Agent '{self.name}' is not connected to an AgentNetwork."
            )
        return self.network.ask(self, target_name, question, context)

    def __repr__(self):
        return f"<Agent: {self.name} | {self.role}>"
