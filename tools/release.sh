#!/usr/bin/env bash
set -euo pipefail

dist_name="$(sed -n 's/^name = "\(.*\)"/\1/p' pyproject.toml)"
module="${dist_name//-/_}"
icons="$module/assets"

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    os_flags=(--windows-console-mode=disable "--windows-icon-from-ico=$icons/icon.ico")
    output="$dist_name.exe"
    platform="windows"
    ;;
  Darwin)
    os_flags=("--macos-app-icon=$icons/icon.png")
    output="$dist_name"
    platform="macos"
    ;;
  *)
    os_flags=("--linux-icon=$icons/icon.png")
    output="$dist_name"
    platform="linux"
    ;;
esac

uv run --locked --no-editable python -m nuitka \
  --onefile \
  --python-flag=-m \
  --enable-plugin=tk-inter \
  --assume-yes-for-downloads \
  --output-dir=build/dist \
  --output-filename="$output" \
  --include-distribution-metadata="$dist_name" \
  --include-package-data="$module" \
  "${os_flags[@]}" \
  "$module"

zip -j "build/$dist_name-$platform.zip" "build/dist/$output"
