#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

have() { command -v "$1" >/dev/null 2>&1; }

install_uv() {
  have uv && return 0
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
      powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
      ;;
    *)
      curl -LsSf https://astral.sh/uv/install.sh | sh
      ;;
  esac
}

install_python_tk() {
  have brew || return 0

  local minor
  minor="$(sed -En 's/^([0-9]+\.[0-9]+)(\.[0-9]+)?$/\1/p' .python-version 2>/dev/null || true)"
  [ -n "$minor" ] || {
    echo "Expected .python-version to contain X.Y or X.Y.Z" >&2
    exit 1
  }

  local formula="python-tk@${minor}"
  brew list --formula "$formula" >/dev/null 2>&1 || brew install "$formula"
}

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    powershell -NoProfile -ExecutionPolicy Bypass -File tools/install-bash.ps1
    ;;
  Darwin)
    install_python_tk
    ;;
esac

install_uv
uv self update -q || true
