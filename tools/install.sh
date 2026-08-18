#!/usr/bin/env bash
set -euo pipefail

have() { command -v "$1" >/dev/null 2>&1; }

uv_sh() { bash "$(dirname "$0")/uv.sh" "$@"; }

winpwsh() { env -u PSModulePath powershell -NoProfile -ExecutionPolicy Bypass "$@"; }

install_uv() {
  uv_sh --version >/dev/null 2>&1 && return 0
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
      winpwsh -Command "irm https://astral.sh/uv/install.ps1 | iex"
      ;;
    *)
      curl -LsSf https://astral.sh/uv/install.sh | sh
      ;;
  esac
}

install_python_tk() {
  have brew || return 0

  local minor
  minor="$(sed -n 's/^requires-python = "[^0-9]*\([0-9]*\.[0-9]*\).*/\1/p' pyproject.toml)"
  [ -n "$minor" ] || {
    echo "Expected requires-python in pyproject.toml to start with an X.Y version" >&2
    exit 1
  }

  local formula="python-tk@${minor}"
  brew list --formula "$formula" >/dev/null 2>&1 || brew install "$formula"
}

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    winpwsh -File tools/install-bash.ps1
    ;;
  Darwin)
    install_python_tk
    ;;
esac

install_uv
uv_sh self update -q >/dev/null 2>&1 || true
