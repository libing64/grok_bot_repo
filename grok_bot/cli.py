"""Interactive command-line chat interface for Grok Bot."""

from __future__ import annotations

import argparse
import sys

from .client import GrokClient, GrokError


def _run_repl(client: GrokClient) -> int:
    mode = "offline" if client.offline else f"online ({client.config.model})"
    print(f"Grok Bot [{mode}]. Type 'exit' or Ctrl-D to quit.\n")
    history: list[dict[str, str]] = []
    while True:
        try:
            user = input("you> ").strip()
        except EOFError:
            print()
            break
        if user.lower() in {"exit", "quit"}:
            break
        if not user:
            continue
        history.append({"role": "user", "content": user})
        try:
            reply = client.chat(history)
        except GrokError as exc:
            print(f"error: {exc}", file=sys.stderr)
            history.pop()
            continue
        history.append({"role": "assistant", "content": reply})
        print(f"grok> {reply}\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chat with Grok from the terminal.")
    parser.add_argument(
        "message",
        nargs="*",
        help="Send a single message and print the reply, then exit.",
    )
    args = parser.parse_args(argv)

    client = GrokClient()

    if args.message:
        message = " ".join(args.message)
        try:
            print(client.chat([{"role": "user", "content": message}]))
        except GrokError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 0

    return _run_repl(client)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
