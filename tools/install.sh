#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    # Keep Git bash + GNU make installed and current (winget-managed).
    powershell -NoProfile -ExecutionPolicy Bypass -File tools/install-bash.ps1
    command -v uv >/dev/null 2>&1 ||
      powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    ;;
  *)
    command -v uv >/dev/null 2>&1 ||
      curl -LsSf https://astral.sh/uv/install.sh | sh
    ;;
esac

uv self update -q
