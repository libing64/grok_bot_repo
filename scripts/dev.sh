#!/usr/bin/env bash
# Start the Grok Bot web server for local development.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -d .venv ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

export FLASK_APP=grok_bot.app:app
export PORT="${PORT:-5000}"

exec python -m flask run --host 0.0.0.0 --port "$PORT"
