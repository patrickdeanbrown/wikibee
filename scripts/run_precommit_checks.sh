#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required for this script. Install it from https://docs.astral.sh/uv/" >&2
  exit 2
fi

EXCLUDES=(".venv" ".uv-cache")
ISORT_SKIP=()
RUFF_EXCLUDES=()
BLACK_PATTERN=""
for dir in "${EXCLUDES[@]}"; do
  ISORT_SKIP+=("--skip" "$dir")
  RUFF_EXCLUDES+=("--exclude" "$dir")
  # Build regex fragment for black
  escaped_dir=${dir//\./\\.}
  BLACK_PATTERN+="|/${escaped_dir}/"
done
# Remove leading | and wrap in regex expected by black
BLACK_REGEX="(${BLACK_PATTERN#|})"

uv run isort --profile black "${ISORT_SKIP[@]}" .
uv run black --exclude "$BLACK_REGEX" .
uv run ruff check "${RUFF_EXCLUDES[@]}" .
uv run mypy --config-file pyproject.toml wikibee
