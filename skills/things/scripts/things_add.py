#!/usr/bin/env python3
"""Send a batch of to-dos to Things 3 via the things:///json URL scheme.

Reads a JSON array from stdin or --file, URL-encodes it, and opens the
resulting URL on macOS. On other platforms prints the URL and exits 2.

Usage:
    echo '[{"type":"to-do","attributes":{"title":"Buy milk"}}]' | \\
        python3 things_add.py --stdin

    python3 things_add.py --file batch.json
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import urllib.parse

MAX_URL_LEN = 2000
THINGS_URL_BASE = "things:///json"


def load_items(args: argparse.Namespace) -> list[dict]:
    if args.stdin:
        raw = sys.stdin.read()
    elif args.file:
        raw = args.file.read_text()
    else:
        sys.exit("error: pass --stdin or --file <path>")

    try:
        items = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"error: input is not valid JSON: {e}")

    if not isinstance(items, list):
        sys.exit("error: JSON must be an array of items")
    if not items:
        sys.exit("error: no items to add")

    for i, item in enumerate(items):
        if not isinstance(item, dict):
            sys.exit(f"error: item {i} is not an object")
        if item.get("type") not in ("to-do", "project", "heading", "checklist-item"):
            sys.exit(f"error: item {i} has unsupported type {item.get('type')!r}")
        attrs = item.get("attributes") or {}
        if item["type"] in ("to-do", "project") and not attrs.get("title"):
            sys.exit(f"error: item {i} needs a non-empty title")

    return items


def needs_auth(items: list[dict]) -> bool:
    """Auth token is only required for update operations."""
    return any(item.get("operation") == "update" for item in items)


def build_url(items: list[dict]) -> str:
    payload = json.dumps(items, separators=(",", ":"), ensure_ascii=False)
    encoded = urllib.parse.quote(payload, safe="")
    url = f"{THINGS_URL_BASE}?data={encoded}"
    if needs_auth(items):
        token = os.environ.get("THINGS_AUTH_TOKEN")
        if not token:
            sys.exit(
                "error: items contain update operations but THINGS_AUTH_TOKEN is unset.\n"
                "Get the token from Things → Settings → General → Enable Things URLs → Manage."
            )
        url += f"&auth-token={urllib.parse.quote(token, safe='')}"
    return url


def open_on_mac(url: str) -> int:
    try:
        result = subprocess.run(["open", url], check=False)
    except FileNotFoundError:
        print(url)
        print("error: `open` not found — is this really macOS?", file=sys.stderr)
        return 2
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--stdin", action="store_true", help="read JSON from stdin")
    src.add_argument("--file", type=lambda p: __import__("pathlib").Path(p))
    parser.add_argument(
        "--print-url",
        action="store_true",
        help="print the URL before opening (useful for debugging)",
    )
    args = parser.parse_args()

    items = load_items(args)
    url = build_url(items)

    if len(url) > MAX_URL_LEN:
        print(
            f"warning: URL is {len(url)} chars (limit ~{MAX_URL_LEN}); "
            f"Things may reject. Split the batch if this fails.",
            file=sys.stderr,
        )

    if args.print_url:
        print(url)

    count = sum(1 for i in items if i.get("type") == "to-do")

    if platform.system() == "Darwin":
        rc = open_on_mac(url)
        if rc != 0:
            print(f"error: open exited {rc}", file=sys.stderr)
            return rc
        print(f"Added {count} to-do{'s' if count != 1 else ''} to Things.")
        return 0

    print(url)
    print(
        f"note: not macOS ({platform.system()}); printed URL instead of opening. "
        f"{count} to-do{'s' if count != 1 else ''} ready to send.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
