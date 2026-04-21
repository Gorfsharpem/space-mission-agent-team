from __future__ import annotations

import os

from providers.cloud_anthropic import CloudAnthropicProvider
from providers.ollama_anthropic import OllamaAnthropicProvider


def build_provider():
    backend = os.environ.get("LLM_BACKEND", "anthropic").lower()

    if backend == "anthropic":
        return CloudAnthropicProvider()

    if backend == "ollama":
        return OllamaAnthropicProvider()

    raise ValueError(
        f"Unsupported LLM_BACKEND='{backend}'. Expected one of: anthropic, ollama."
    )
