from __future__ import annotations

from abc import ABC, abstractmethod

from settings import MAX_TOKENS


class LLMProvider(ABC):
    """
    Base class for all LLM backend providers.
    Subclass this to add Anthropic, Ollama, Mistral, Perplexity, etc.

    Concrete providers must implement generate().
    """

    @abstractmethod
    def generate(
        self,
        *,
        system: str,
        user: str,
        model: str,
        max_tokens: int = MAX_TOKENS,
    ) -> str:
        """
        Send a system + user prompt to the backend and return the text response.

        All providers must honour:
          - system:     the agent persona/instructions prompt
          - user:       the task message (may include mission context)
          - model:      the model identifier string (backend-specific)
          - max_tokens: upper bound on response length
        """
        ...

    @property
    def name(self) -> str:
        return self.__class__.__name__.replace("Provider", "").lower()

    def __repr__(self) -> str:
        return f"<LLMProvider: {self.__class__.__name__}>"
