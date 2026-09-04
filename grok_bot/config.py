"""Runtime configuration for Grok Bot, sourced from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional at runtime
    pass


DEFAULT_BASE_URL = "https://api.x.ai/v1"
DEFAULT_MODEL = "grok-2-latest"
DEFAULT_SYSTEM_PROMPT = (
    "You are Grok, a witty and helpful AI assistant. Answer clearly and concisely."
)


@dataclass(frozen=True)
class Config:
    """Resolved configuration for talking to the Grok API."""

    api_key: str | None
    base_url: str
    model: str
    system_prompt: str
    request_timeout: float

    @property
    def offline(self) -> bool:
        """True when no API key is configured, so the mock responder is used."""
        return not self.api_key


def load_config() -> Config:
    """Build a :class:`Config` from the current environment."""
    return Config(
        api_key=os.getenv("XAI_API_KEY") or None,
        base_url=os.getenv("XAI_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
        model=os.getenv("GROK_MODEL", DEFAULT_MODEL),
        system_prompt=os.getenv("GROK_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT),
        request_timeout=float(os.getenv("GROK_TIMEOUT", "30")),
    )
