#!/bin/bash
# ============================================================
# VECR Garage - Lint Check Script
# 全Pythonサービスのlintチェックを実行
# ============================================================

set -e  # エラー時に即座に終了

echo "🔍 Running linters for all services..."
echo "============================================================"

# 対象サービスディレクトリ
SERVICES=(
    "backend-db-registration"
    "backend-llm-response"
    "member-manager"
)

# 終了コード初期化
EXIT_CODE=0

# 各サービスのlintチェック
for SERVICE in "${SERVICES[@]}"; do
    echo ""
    echo "📦 Checking ${SERVICE}..."
    echo "------------------------------------------------------------"

    if [ -d "/workspace/${SERVICE}" ]; then
        cd "/workspace/${SERVICE}"

        # Ruff lintチェック
        if ruff check . ; then
            echo "✅ ${SERVICE}: Ruff check passed"
        else
            echo "❌ ${SERVICE}: Ruff check failed"
            EXIT_CODE=1
        fi
    else
        echo "⚠️  ${SERVICE}: Directory not found, skipping..."
    fi
done

echo ""
echo "============================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All lint checks passed!"
else
    echo "❌ Some lint checks failed. Please fix the issues above."
fi

exit $EXIT_CODE
