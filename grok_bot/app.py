"""Flask web application exposing a simple Grok chat UI and JSON API."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from .client import GrokClient, GrokError


def create_app(client: GrokClient | None = None) -> Flask:
    app = Flask(__name__)
    bot = client or GrokClient()

    @app.get("/")
    def index() -> str:
        return render_template("index.html", offline=bot.offline, model=bot.config.model)

    @app.get("/api/health")
    def health():
        return jsonify(
            status="ok",
            offline=bot.offline,
            model=bot.config.model,
        )

    @app.post("/api/chat")
    def chat():
        payload = request.get_json(silent=True) or {}
        messages = payload.get("messages")
        if messages is None:
            message = (payload.get("message") or "").strip()
            if not message:
                return jsonify(error="A 'message' or 'messages' field is required."), 400
            messages = [{"role": "user", "content": message}]

        if not isinstance(messages, list):
            return jsonify(error="'messages' must be a list."), 400

        try:
            reply = bot.chat(messages)
        except GrokError as exc:
            return jsonify(error=str(exc)), 502

        return jsonify(reply=reply, offline=bot.offline, model=bot.config.model)

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    import os

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
