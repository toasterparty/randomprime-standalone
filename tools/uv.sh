#!/usr/bin/env bash
# Run uv from the repo root with the settings in project.env applied.
set -euo pipefail

cd "$(dirname "$0")/.."

set -a
source ./project.env
set +a
export PATH="$(cd "$HOME" && pwd)/.local/bin:$PATH"

mkdir -p build
exec uv "$@"
