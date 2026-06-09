#!/bin/bash
# Codex Environment Setup
# Run this before first use. Installs dependencies and configures Chrome DevTools MCP.

set -e

# DOCX conversion & image processing
pip install python-docx Pillow

# Configure Chrome DevTools MCP in Codex config (if not already present)
CODEX_CONFIG="$HOME/.codex/config.toml"
if [ -f "$CODEX_CONFIG" ]; then
    if ! grep -q "chrome-devtools" "$CODEX_CONFIG"; then
        echo '' >> "$CODEX_CONFIG"
        echo '[mcp_servers.chrome-devtools]' >> "$CODEX_CONFIG"
        echo 'command = "npx"' >> "$CODEX_CONFIG"
        echo 'args = ["-y", "chrome-devtools-mcp@latest"]' >> "$CODEX_CONFIG"
        echo "Chrome DevTools MCP added to config.toml (default port 9222)"
    else
        echo "Chrome DevTools MCP already configured in config.toml"
    fi
else
    echo "WARNING: $CODEX_CONFIG not found. Create it and add chrome-devtools MCP manually."
fi

# Create desktop shortcut for Chrome (Windows only)
if [[ "$OS" == "Windows_NT" ]]; then
    powershell -ExecutionPolicy Bypass -File scripts/create_shortcuts.ps1 2>/dev/null || true
fi

echo "Setup complete"
