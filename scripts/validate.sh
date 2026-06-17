#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_DIR="$ROOT_DIR/plugins/company-brain-harness"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CODEX_PLUGIN_VALIDATOR="$CODEX_HOME/skills/.system/plugin-creator/scripts/validate_plugin.py"

echo "== python compile =="
python3 -m py_compile "$PLUGIN_DIR"/bin/*.py "$ROOT_DIR"/scripts/*.py

echo "== skill structure =="
python3 "$ROOT_DIR/scripts/validate_skills.py" "$ROOT_DIR"

if [[ "${SKIP_CLI_VALIDATORS:-0}" != "1" && -f "$CODEX_PLUGIN_VALIDATOR" ]]; then
  echo "== codex plugin manifest =="
  python3 "$CODEX_PLUGIN_VALIDATOR" "$PLUGIN_DIR"
else
  echo "== codex plugin manifest =="
  echo "skipped (validator not found or SKIP_CLI_VALIDATORS=1)"
fi

if [[ "${SKIP_CLI_VALIDATORS:-0}" != "1" && "$(command -v claude || true)" != "" ]]; then
  echo "== claude plugin manifest =="
  claude plugin validate "$PLUGIN_DIR"
  echo "== claude marketplace =="
  claude plugin validate "$ROOT_DIR"
else
  echo "== claude plugin manifest =="
  echo "skipped (claude CLI not found or SKIP_CLI_VALIDATORS=1)"
fi

echo "== smoke test =="
bash "$ROOT_DIR/scripts/smoke-test.sh"

echo "validation passed"
