"""Tests for the offline responder and API client behaviour."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from grok_bot.client import GrokClient, GrokError
from grok_bot.config import Config


def offline_config() -> Config:
    return Config(
        api_key=None,
        base_url="https://api.x.ai/v1",
        model="grok-2-latest",
        system_prompt="You are Grok.",
        request_timeout=5.0,
    )


def online_config() -> Config:
    return Config(
        api_key="test-key",
        base_url="https://api.x.ai/v1",
        model="grok-2-latest",
        system_prompt="You are Grok.",
        request_timeout=5.0,
    )


def test_client_is_offline_without_key():
    client = GrokClient(offline_config())
    assert client.offline is True


def test_offline_greeting():
    client = GrokClient(offline_config())
    reply = client.chat([{"role": "user", "content": "hello"}])
    assert "offline mode" in reply.lower()


def test_offline_arithmetic():
    client = GrokClient(offline_config())
    assert client.chat([{"role": "user", "content": "2 + 3"}]) == "2 + 3 = 5"
    assert client.chat([{"role": "user", "content": "10 / 4"}]) == "10 / 4 = 2.5"


def test_offline_echo_word_count():
    client = GrokClient(offline_config())
    reply = client.chat([{"role": "user", "content": "the quick brown fox"}])
    assert "4 words" in reply


def test_system_prompt_prepended():
    client = GrokClient(offline_config())
    captured = {}
    original = client._offline_reply

    def spy(messages):
        captured["messages"] = messages
        return original(messages)

    with patch.object(client, "_offline_reply", side_effect=spy):
        client.chat([{"role": "user", "content": "hi"}])

    assert captured["messages"][0]["role"] == "system"


class _FakeResponse:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


def test_api_reply_success():
    client = GrokClient(online_config())
    payload = {"choices": [{"message": {"content": "  Hello from Grok  "}}]}
    with patch("grok_bot.client.requests.post", return_value=_FakeResponse(200, payload)):
        reply = client.chat([{"role": "user", "content": "hi"}])
    assert reply == "Hello from Grok"


def test_api_reply_error_status():
    client = GrokClient(online_config())
    with patch(
        "grok_bot.client.requests.post",
        return_value=_FakeResponse(401, text="unauthorized"),
    ):
        with pytest.raises(GrokError):
            client.chat([{"role": "user", "content": "hi"}])
