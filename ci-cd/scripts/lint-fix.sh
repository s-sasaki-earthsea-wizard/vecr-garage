#!/bin/bash
# ============================================================
# VECR Garage - Lint Auto-fix Script
# 全Pythonサービスのlint問題を自動修正
# ============================================================

set -e  # エラー時に即座に終了

echo "🔧 Running lint auto-fix for all services..."
echo "============================================================"

# 対象サービスディレクトリ
SERVICES=(
    "backend-db-registration"
    "backend-llm-response"
    "member-manager"
)

# 各サービスのlint自動修正
for SERVICE in "${SERVICES[@]}"; do
    echo ""
    echo "📦 Auto-fixing ${SERVICE}..."
    echo "------------------------------------------------------------"

    if [ -d "/workspace/${SERVICE}" ]; then
        cd "/workspace/${SERVICE}"

        # Ruff auto-fix実行
        if ruff check --fix . ; then
            echo "✅ ${SERVICE}: Auto-fix completed"
        else
            echo "❌ ${SERVICE}: Auto-fix failed or has remaining issues"
        fi
    else
        echo "⚠️  ${SERVICE}: Directory not found, skipping..."
    fi
done

echo ""
echo "============================================================"
echo "✅ All lint auto-fixes completed!"
echo "💡 Run 'make lint' to check remaining issues"
