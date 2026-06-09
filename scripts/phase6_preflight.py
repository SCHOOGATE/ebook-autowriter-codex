#!/usr/bin/env python3
"""Phase 6/7 preflight check: verify Chrome DevTools is reachable.

Usage:
  python scripts/phase6_preflight.py          # default port 9222
  python scripts/phase6_preflight.py 9224     # custom port
  CDTP_PORT=9224 python scripts/phase6_preflight.py  # env var
"""
import os
import sys
import urllib.request
import json

DEFAULT_PORT = 9222
TIMEOUT = 5


def get_port():
    """Resolve port from: CLI arg > env var > default (9222)."""
    if len(sys.argv) > 1:
        return int(sys.argv[1])
    env_port = os.environ.get("CDTP_PORT")
    if env_port:
        return int(env_port)
    return DEFAULT_PORT


def check(port):
    url = f"http://127.0.0.1:{port}/json/version"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            browser = data.get("Browser", "unknown")
            ws = data.get("webSocketDebuggerUrl", "")
            print(f"PASS: Chrome DevTools reachable on port {port}")
            print(f"  Browser: {browser}")
            print(f"  WebSocket: {ws}")
            return 0
    except Exception as e:
        print(f"FAIL: Chrome DevTools NOT reachable on port {port}")
        print(f"  Error: {e}")
        print()
        print("Action required:")
        print(f"  1. Launch Chrome with: --remote-debugging-port={port} --remote-allow-origins=*")
        print(f"  2. Or double-click the 'Chrome book creation' shortcut on Desktop")
        print(f"  3. Then restart Codex so MCP config is loaded")
        print()
        print("DO NOT proceed with Phase 6/7 until this check passes.")
        return 1


if __name__ == "__main__":
    sys.exit(check(get_port()))
