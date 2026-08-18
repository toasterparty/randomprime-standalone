#!/usr/bin/env bash
set -euo pipefail

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

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    winpwsh -File tools/install-bash.ps1
    ;;
esac

install_uv
uv_sh self update -q >/dev/null 2>&1 || true
