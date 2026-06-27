#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Prefer local venv, else python3 (very common on WSL)
if [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
  PYTHON="$SCRIPT_DIR/.venv/bin/python"
else
  PYTHON="python3"
fi

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "[OutLoud] $PYTHON not found."
  echo "Run this in your terminal:"
  echo "  sudo apt update && sudo apt install -y python3 python3-pip python3-venv mpg123"
  exit 127
fi

exec "$PYTHON" "$SCRIPT_DIR/scripts/speaker.py" "$@"