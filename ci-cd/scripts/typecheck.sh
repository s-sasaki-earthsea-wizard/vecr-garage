#!/bin/bash
# ============================================================
# VECR Garage - Type Check Script
# 全Pythonサービスの型チェックを実行
# ============================================================

set -e  # エラー時に即座に終了

echo "🔍 Running type checker for all services..."
echo "============================================================"

# 対象サービスディレクトリ（型チェック有効なもののみ）
SERVICES=(
    "backend-db-registration/src"
    "backend-llm-response/src"
)

# 終了コード初期化
EXIT_CODE=0

# 各サービスの型チェック
for SERVICE in "${SERVICES[@]}"; do
    echo ""
    echo "📦 Type checking ${SERVICE}..."
    echo "------------------------------------------------------------"

    if [ -d "/workspace/${SERVICE}" ]; then
        cd "/workspace"

        # mypy 実行
        if mypy "${SERVICE}" --ignore-missing-imports ; then
            echo "✅ ${SERVICE}: Type check passed"
        else
            echo "❌ ${SERVICE}: Type check failed"
            EXIT_CODE=1
        fi
    else
        echo "⚠️  ${SERVICE}: Directory not found, skipping..."
    fi
done

echo ""
echo "============================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All type checks passed!"
else
    echo "❌ Some type checks failed. Please fix the issues above."
fi

exit $EXIT_CODE
