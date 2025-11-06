#!/bin/bash
# ============================================================
# VECR Garage - Format Check Script
# 全Pythonサービスのフォーマットチェックを実行（修正なし）
# ============================================================

set -e  # エラー時に即座に終了

echo "🎨 Checking code format for all services..."
echo "============================================================"

# 対象サービスディレクトリ
SERVICES=(
    "backend-db-registration"
    "backend-llm-response"
    "member-manager"
)

# 各サービスのフォーマットチェック
for SERVICE in "${SERVICES[@]}"; do
    echo ""
    echo "📦 Checking ${SERVICE}..."
    echo "------------------------------------------------------------"

    if [ -d "/workspace/${SERVICE}" ]; then
        cd "/workspace/${SERVICE}"

        # Black フォーマットチェック実行（--check: 修正なし）
        if black --check . ; then
            echo "✅ ${SERVICE}: Format check passed"
        else
            echo "❌ ${SERVICE}: Format check failed"
            exit 1
        fi
    else
        echo "⚠️  ${SERVICE}: Directory not found, skipping..."
    fi
done

echo ""
echo "============================================================"
echo "✅ All services format check passed!"
