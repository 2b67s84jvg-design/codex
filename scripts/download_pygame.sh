#!/usr/bin/env bash
set -euo pipefail

target_dir="${1:-vendor}"
mkdir -p "$target_dir"

echo "Attempting to download pygame wheels into $target_dir" >&2
python -m pip download pygame -d "$target_dir"
