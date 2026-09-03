# grok_bot_repo

A small chatbot powered by [xAI's Grok API](https://docs.x.ai/), with both a
web UI and a command-line interface. It talks to the real Grok API when
`XAI_API_KEY` is set, and otherwise runs in a deterministic **offline mode** so
the app is always runnable in development, tests, and CI without credentials.

## Features

- Flask web chat UI with conversation history (`grok_bot/app.py`).
- JSON API: `POST /api/chat` and `GET /api/health`.
- Interactive terminal chat (`python -m grok_bot.cli`).
- Offline fallback responder (greetings, arithmetic, echo) when no API key.
- Pytest suite covering the client and the web API.

## Requirements

- Python 3.12+
- `python3-venv` (for creating the virtualenv)

## Setup

```bash
./scripts/install.sh          # creates .venv and installs dependencies
source .venv/bin/activate
```

To use the real Grok API, copy `.env.example` to `.env` and set `XAI_API_KEY`
(or export it in your shell). Without it, the bot runs in offline mode.

## Run the web app

```bash
./scripts/dev.sh              # serves on http://localhost:5000
```

Then open http://localhost:5000 and start chatting.

## Run the CLI

```bash
python -m grok_bot.cli                 # interactive REPL
python -m grok_bot.cli "2 + 2"         # one-shot message
```

## Test

```bash
source .venv/bin/activate
pytest
```

## Configuration

| Variable             | Default                 | Description                          |
| -------------------- | ----------------------- | ------------------------------------ |
| `XAI_API_KEY`        | _(unset → offline)_     | xAI API key. Enables real Grok.      |
| `XAI_BASE_URL`       | `https://api.x.ai/v1`   | API base URL.                        |
| `GROK_MODEL`         | `grok-2-latest`         | Model name.                          |
| `GROK_SYSTEM_PROMPT` | _(built-in)_            | System prompt.                       |
| `GROK_TIMEOUT`       | `30`                    | Request timeout in seconds.          |
| `PORT`               | `5000`                  | Web server port.                     |
