"""Grok API client with an offline fallback responder.

The xAI Grok API is OpenAI-compatible, so requests are POSTed to
``{base_url}/chat/completions``. When no API key is available the client
produces a deterministic local reply instead, which keeps the app runnable in
development and CI without network access or credentials.
"""

from __future__ import annotations

import re
from typing import Iterable

import requests

from .config import Config, load_config


class GrokError(RuntimeError):
    """Raised when the Grok API returns an error response."""


Message = dict[str, str]


class GrokClient:
    """Thin client around the xAI chat-completions endpoint."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or load_config()

    @property
    def offline(self) -> bool:
        return self.config.offline

    def chat(self, messages: Iterable[Message]) -> str:
        """Return the assistant reply for the given conversation.

        ``messages`` is a list of ``{"role", "content"}`` dicts. The configured
        system prompt is prepended automatically when the caller has not
        supplied one.
        """
        history = list(messages)
        if not history or history[0].get("role") != "system":
            history = [
                {"role": "system", "content": self.config.system_prompt},
                *history,
            ]

        if self.config.offline:
            return self._offline_reply(history)
        return self._api_reply(history)

    def _api_reply(self, messages: list[Message]) -> str:
        url = f"{self.config.base_url}/chat/completions"
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        try:
            resp = requests.post(
                url, json=payload, headers=headers, timeout=self.config.request_timeout
            )
        except requests.RequestException as exc:  # network failure
            raise GrokError(f"Failed to reach Grok API: {exc}") from exc

        if resp.status_code != 200:
            raise GrokError(
                f"Grok API returned {resp.status_code}: {resp.text[:500]}"
            )

        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise GrokError(f"Unexpected Grok API response: {data!r}") from exc

    def _offline_reply(self, messages: list[Message]) -> str:
        """Produce a deterministic, self-explaining reply without network."""
        last_user = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"),
            "",
        )
        text = last_user.strip()
        lowered = text.lower()

        if not text:
            return "Hi, I'm Grok (offline mode). Ask me something!"

        if re.search(r"\b(hi|hello|hey|yo)\b", lowered):
            return (
                "Hello! I'm Grok running in offline mode (no XAI_API_KEY set). "
                "Set XAI_API_KEY to talk to the real Grok API."
            )

        # Simple arithmetic so a demo can show a real, verifiable answer.
        match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)\s*", text)
        if match:
            a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
            result = {
                "+": a + b,
                "-": a - b,
                "*": a * b,
                "/": a / b if b else float("nan"),
            }[op]
            pretty = int(result) if result == int(result) else result
            return f"{text} = {pretty}"

        word_count = len(text.split())
        return (
            f"(offline) You said: \"{text}\". That's {word_count} word"
            f"{'s' if word_count != 1 else ''}. "
            "Set XAI_API_KEY for real Grok answers."
        )
