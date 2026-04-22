from __future__ import annotations

import os
import anthropic
from providers.base import LLMProvider

from settings import MAX_TOKENS

class CloudAnthropicProvider(LLMProvider):
    def __init__(self, api_key: str | None = None):
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        )

    def generate(self, *, system: str, user: str, model: str, max_tokens: int = MAX_TOKENS) -> str:
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text
