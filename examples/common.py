"""Shared helpers for the AG2 network examples."""
import os


def make_config():
    """Return a ModelConfig based on environment variables.

    - AG2_PROVIDER=ollama (default) uses a local Ollama server.
    - AG2_PROVIDER=openai uses OPENAI_API_KEY.
    - AG2_PROVIDER=anthropic uses ANTHROPIC_API_KEY.
    """
    provider = os.getenv("AG2_PROVIDER", "ollama").lower()
    model = os.getenv("AG2_MODEL")
    if provider == "openai":
        from ag2.config import OpenAIConfig
        return OpenAIConfig(model=model or "gpt-4o-mini")
    if provider == "anthropic":
        from ag2.config import AnthropicConfig
        return AnthropicConfig(model=model or "claude-sonnet-4-5")
    from ag2.config import OllamaConfig
    return OllamaConfig(model=model or "gemma4:e4b")