#!/usr/bin/env bash
set -euo pipefail

source ./project.env

dist_name="$(sed -n 's/^name = "\(.*\)"/\1/p' pyproject.toml)"
version="$(sed -n 's/^version = "\(.*\)"/\1/p' pyproject.toml)"
description="$(sed -n 's/^description = "\(.*\)"/\1/p' pyproject.toml)"
module="${dist_name//-/_}"
product_name="$(tools/uv.sh run -q --locked --no-editable python -c "import $module; print($module.PRODUCT_NAME)")"
copyright="Copyright $(date +%Y) $COMPANY_NAME"

for field in COMPANY_NAME dist_name version description product_name; do
  if [ -z "${!field:-}" ]; then
    echo "Cannot release: $field is empty" >&2
    exit 1
  fi
done

case "${SHOW_CONSOLE:-}" in
  1) console_mode=attach ;;  # Prints to the terminal that launched it, opens none of its own.
  0) console_mode=disable ;;
  *) echo "Cannot release: SHOW_CONSOLE must be 0 or 1" >&2; exit 1 ;;
esac

# Never onefile: it unpacks to a temp directory per run and trips antivirus.
flags=(
  --mode=standalone
  --deployment
  --python-flag=-m
  --assume-yes-for-downloads
  --output-dir=build/dist
  "--include-distribution-metadata=$dist_name"
  --enable-plugin=tk-inter
  "--include-package-data=$module"
)

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    platform=windows
    output="$dist_name.exe"
    flags+=(
      --msvc=latest
      "--windows-console-mode=$console_mode"
      "--windows-icon-from-ico=$module/assets/icon.ico"
      "--company-name=$COMPANY_NAME"
      "--product-name=$product_name"
      "--file-description=$description"
      "--copyright=$copyright"
      "--file-version=$version"
      "--product-version=$version"
    )
    ;;
  Darwin)
    platform=macos
    output="$dist_name"
    flags+=("--macos-app-icon=$module/assets/icon.png")
    ;;
  *)
    platform=linux
    output="$dist_name"
    flags+=("--linux-icon=$module/assets/icon.png")
    ;;
esac
flags+=("--output-filename=$output")

tools/uv.sh run --locked --no-editable python -m nuitka "${flags[@]}" "$module"

# Extracting must yield one folder, not a spill of loose files.
rm -rf "build/dist/$dist_name"
mv "build/dist/$module.dist" "build/dist/$dist_name"

stem="build/$dist_name-v$version-$platform"
if [ "$platform" = windows ]; then
  tools/uv.sh run --no-sync python -c "
import shutil, sys
shutil.make_archive(sys.argv[1], 'zip', root_dir='build/dist', base_dir=sys.argv[2])
" "$stem" "$dist_name"
  archive="$stem.zip"
else
  # tar.gz preserves the executable bit on Unix; zip does not.
  archive="$stem.tar.gz"
  tar -czf "$archive" -C build/dist "$dist_name"
fi

echo "Built $archive"
