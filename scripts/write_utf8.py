#!/usr/bin/env python3
"""UTF-8 safe file writer for Windows environments.

Usage:
  # Write from stdin
  echo "content" | python scripts/write_utf8.py output/slug/manuscript.md

  # Write from Python variable (in Codex)
  python -c "
  import subprocess, sys
  content = '''your content here'''
  proc = subprocess.run(
      [sys.executable, 'scripts/write_utf8.py', 'output/slug/manuscript.md'],
      input=content, text=True, encoding='utf-8'
  )
  "

Why this exists:
  On Windows, Python's default open() uses cp932 encoding, which replaces
  all Japanese characters with '?'. This script always uses UTF-8.
  Incident: 2026-06-10 shingata-eiyou-shicchou test — 94% of chars became '?'.
"""
import sys

if len(sys.argv) < 2:
    print("Usage: python scripts/write_utf8.py <output_path>")
    print("  Reads content from stdin and writes to output_path as UTF-8.")
    sys.exit(1)

output_path = sys.argv[1]

# Read from stdin with UTF-8
if sys.stdin.encoding and sys.stdin.encoding.lower() != "utf-8":
    import io
    stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
else:
    stdin = sys.stdin

content = stdin.read()

# Write with explicit UTF-8, no BOM
with open(output_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

char_count = len(content)
jp_chars = sum(1 for c in content if ord(c) > 0x3000)
print(f"OK: {output_path} ({char_count} chars, {jp_chars} Japanese chars, UTF-8)")
