#!/usr/bin/env bash
set -euo pipefail

echo "==> Project Permanence Compiler Pipeline"

echo "[1/5] Syntax verification..."
python3 -m py_compile \
    Compiler/compiler.py \
    Compiler/core/*.py \
    Compiler/core/advisory/*.py \
    Compiler/validators/*.py \
    Compiler/generators/contract/generate.py

echo "[2/5] Git status..."
git status --short

echo "[3/5] Running compiler smoke test..."
python3 - <<'PY'
from Compiler.compiler import Compiler

compiler = Compiler()

print("✓ Compiler import successful")
print("✓ Pipeline ready")
PY

echo "[4/5] Recent commits..."
git log --oneline -3

echo "[5/5] Pipeline complete."

echo
echo "DS ✓"