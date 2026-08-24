#!/usr/bin/env bash
# Provision the toolchain (Git bash, GNU make, uv). Without --update this only
# ensures they are present; --update pulls them to latest.
set -euo pipefail

cd "$(dirname "$0")/.."

update=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --update) update=1; shift ;;
    *) echo "Error: unknown argument '$1'" >&2; exit 1 ;;
  esac
done

uv_sh() { bash ./tools/uv.sh "$@"; }

winpwsh() { env -u PSModulePath powershell -NoProfile -ExecutionPolicy Bypass "$@"; }

is_windows() {
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) return 0 ;;
    *) return 1 ;;
  esac
}

install_uv() {
  uv_sh --version >/dev/null 2>&1 && return 0
  if is_windows; then
    winpwsh -Command "irm https://astral.sh/uv/install.ps1 | iex"
  else
    curl -LsSf https://astral.sh/uv/install.sh | sh
  fi
}

if is_windows; then
  if [[ $update -eq 1 ]]; then
    winpwsh -File tools/install-bash.ps1 -Update
  else
    winpwsh -File tools/install-bash.ps1
  fi
fi

install_uv

if [[ -z "${CI:-}" ]]; then
  uv_sh self update -q >/dev/null 2>&1 || true
fi
