#!/usr/bin/env bash
set -euo pipefail

command -v uv >/dev/null 2>&1 && exit 0

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    powershell.exe -NoProfile -ExecutionPolicy ByPass -Command \
      "irm https://astral.sh/uv/install.ps1 | iex"
    ;;
  *)
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ;;
esac
