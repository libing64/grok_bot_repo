"""Tests for the Flask web API using the offline client."""

from __future__ import annotations

import pytest

from grok_bot.app import create_app
from grok_bot.client import GrokClient
from grok_bot.config import Config


@pytest.fixture()
def client():
    config = Config(
        api_key=None,
        base_url="https://api.x.ai/v1",
        model="grok-2-latest",
        system_prompt="You are Grok.",
        request_timeout=5.0,
    )
    app = create_app(GrokClient(config))
    app.testing = True
    return app.test_client()


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["offline"] is True


def test_index_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Grok Bot" in resp.data


def test_chat_with_message(client):
    resp = client.post("/api/chat", json={"message": "4 * 5"})
    assert resp.status_code == 200
    assert resp.get_json()["reply"] == "4 * 5 = 20"


def test_chat_with_messages_list(client):
    resp = client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "hello"}]},
    )
    assert resp.status_code == 200
    assert "offline" in resp.get_json()["reply"].lower()


def test_chat_requires_input(client):
    resp = client.post("/api/chat", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()
