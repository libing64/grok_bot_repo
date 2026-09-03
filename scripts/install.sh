#!/usr/bin/env bash
# Idempotent environment bootstrap for Grok Bot.
# Creates a virtualenv and installs pinned dependencies.
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"

if [ ! -d .venv ]; then
  "$PYTHON" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

echo "Grok Bot dependencies installed."
