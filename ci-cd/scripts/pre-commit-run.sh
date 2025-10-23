#!/bin/bash
# ============================================================
# VECR Garage - Pre-commit Runner Script
# CI/CDコンテナ内でpre-commit hooksを実行
# ============================================================

set -e

echo "============================================================"
echo "🔍 Pre-commit Hooks - CI Runner"
echo "============================================================"
echo ""

# 引数チェック: --all-files または staged files
if [ "$1" = "--all-files" ]; then
    echo "📋 Mode: All files"
    echo "============================================================"
    pre-commit run --all-files
else
    echo "📋 Mode: Staged files only"
    echo "============================================================"

    # Staged filesを取得
    STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || echo "")

    if [ -z "$STAGED_FILES" ]; then
        echo "⚠️  No staged files found. Skipping pre-commit."
        exit 0
    fi

    echo "Staged files:"
    echo "$STAGED_FILES" | sed 's/^/  - /'
    echo ""

    # Staged filesに対してpre-commit実行
    pre-commit run --files $STAGED_FILES
fi

echo ""
echo "============================================================"
echo "✅ Pre-commit hooks completed successfully!"
echo "============================================================"
