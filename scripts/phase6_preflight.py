#!/usr/bin/env python3
"""Phase 6/7 preflight check: verify Chrome DevTools is reachable on port 9224."""
import sys
import urllib.request
import json

PORT = 9224
URL = f"http://127.0.0.1:{PORT}/json/version"
TIMEOUT = 5


def check():
    try:
        req = urllib.request.Request(URL)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            browser = data.get("Browser", "unknown")
            ws = data.get("webSocketDebuggerUrl", "")
            print(f"PASS: Chrome DevTools reachable on port {PORT}")
            print(f"  Browser: {browser}")
            print(f"  WebSocket: {ws}")
            return 0
    except Exception as e:
        print(f"FAIL: Chrome DevTools NOT reachable on port {PORT}")
        print(f"  Error: {e}")
        print()
        print("Action required:")
        print(f"  1. Launch Chrome with: --remote-debugging-port={PORT} --remote-allow-origins=*")
        print(f"  2. Or run: scripts\\start_chrome_9224.bat")
        print(f"  3. Then restart Codex so MCP config is loaded")
        print()
        print("DO NOT proceed with Phase 6/7 until this check passes.")
        return 1


if __name__ == "__main__":
    sys.exit(check())
