from __future__ import annotations

import os
import anthropic
import httpx
from providers.base import LLMProvider

from settings import MAX_TOKENS, NO_THINK

QWEN3_NO_THINK_MODELS = {
    "qwen3", "qwen3:latest",
    "qwen3:0.6b", "qwen3:1.7b", "qwen3:4b", "qwen3:8b", "qwen3:14b", "qwen3:30b", "qwen3:32b", "qwen3:235b"
}

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
        is_qwen3 = any(m in model.lower() for m in QWEN3_NO_THINK_MODELS)

        if is_qwen3:
            if NO_THINK:
                # Qwen3-specific: disable thinking via system prompt prefix
                system = f"/no_think\n\n{system}"
            else:
                # Qwen3-specific: enable extended thinking budget
                extra["thinking"] = {"type": "enabled", "budget_tokens": round(max_tokens/2)}
        # Non-Qwen3 models: no thinking manipulation at all        
        
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
