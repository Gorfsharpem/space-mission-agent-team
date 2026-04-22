from __future__ import annotations

import os
import anthropic
import httpx
from providers.base import LLMProvider

from settings import MAX_TOKENS, NO_THINK

class OllamaAnthropicProvider(LLMProvider):
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.client = anthropic.Anthropic(
            base_url=base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            api_key=api_key or os.environ.get("OLLAMA_API_KEY", "ollama"),
            timeout=httpx.Timeout(
                connect=10.0,    # connection to Ollama
                read=1800.0,     # wait up to 30 min for token generation
                write=30.0,
                pool=10.0,
            ),
        )

    def generate(self, *, system: str, user: str, model: str, max_tokens: int = MAX_TOKENS) -> str:
        extra = {}
        if NO_THINK:
            # This is a qwen3 specific tuning for disabling thinking mode
            system = f"/no_think\n\n{system}"
            print(system)
        else:
            extra["thinking"] = {"type": "enabled", "budget_tokens": 8000}
        
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            **extra
        )
        # Filter out ThinkingBlocks, get first TextBlock
        text_blocks = [b for b in response.content if isinstance(b, anthropic.types.TextBlock)]
        
        if not text_blocks:
                raise ValueError(f"No TextBlock found in response. Got: {[type(b).__name__ for b in response.content]}")
            
        return text_blocks[0].text        
