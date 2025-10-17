#!/bin/bash
# ============================================================
# VECR Garage - Auto Format Script
# 全Pythonサービスの自動フォーマットを実行
# ============================================================

set -e  # エラー時に即座に終了

echo "🎨 Running auto-formatter for all services..."
echo "============================================================"

# 対象サービスディレクトリ
SERVICES=(
    "backend-db-registration"
    "backend-llm-response"
    "member-manager"
)

# 各サービスのフォーマット
for SERVICE in "${SERVICES[@]}"; do
    echo ""
    echo "📦 Formatting ${SERVICE}..."
    echo "------------------------------------------------------------"

    if [ -d "/workspace/${SERVICE}" ]; then
        cd "/workspace/${SERVICE}"

        # Black フォーマット実行
        if black . ; then
            echo "✅ ${SERVICE}: Formatted successfully"
        else
            echo "❌ ${SERVICE}: Format failed"
        fi
    else
        echo "⚠️  ${SERVICE}: Directory not found, skipping..."
    fi
done

echo ""
echo "============================================================"
echo "✅ All services formatted successfully!"
