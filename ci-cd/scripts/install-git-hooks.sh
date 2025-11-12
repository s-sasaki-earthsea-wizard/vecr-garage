#!/bin/bash
# ============================================================
# VECR Garage - Git Hooks Installer
# CI/CDコンテナを使用するpre-commit hookをインストール
# ============================================================

set -e

echo "============================================================"
echo "🔗 Installing Git Hooks (CI Runner Integration)"
echo "============================================================"
echo ""

# プロジェクトルートディレクトリを検出
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "📂 Project root: $PROJECT_ROOT"
echo ""

# .git/hooksディレクトリ確認
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"
if [ ! -d "$HOOKS_DIR" ]; then
    echo "❌ ERROR: .git/hooks directory not found"
    echo "   Make sure you are in a git repository"
    exit 1
fi

# pre-commit hookファイルパス
PRE_COMMIT_HOOK="$HOOKS_DIR/pre-commit"

# 既存のhookのバックアップ
if [ -f "$PRE_COMMIT_HOOK" ]; then
    BACKUP_FILE="$PRE_COMMIT_HOOK.backup.$(date +%Y%m%d_%H%M%S)"
    echo "📦 Backing up existing pre-commit hook to:"
    echo "   $BACKUP_FILE"
    mv "$PRE_COMMIT_HOOK" "$BACKUP_FILE"
    echo ""
fi

# 新しいpre-commit hookを作成
cat > "$PRE_COMMIT_HOOK" << 'EOF'
#!/bin/sh
# ============================================================
# VECR Garage - Pre-commit Hook (CI Runner Integration)
# このフックはci-runnerコンテナ内でpre-commitを実行します
# ============================================================

# プロジェクトルートに移動
cd "$(git rev-parse --show-toplevel)"

# ci-runnerコンテナでpre-commit実行
echo "🔍 Running pre-commit in ci-runner container..."
make ci-pre-commit-run-staged

# 終了コードを保持
exit $?
EOF

# 実行権限付与
chmod +x "$PRE_COMMIT_HOOK"

echo "✅ Pre-commit hook installed successfully!"
echo ""
echo "============================================================"
echo "📋 What happens on 'git commit':"
echo "============================================================"
echo ""
echo "  1. This hook triggers automatically"
echo "  2. Starts ci-runner container (if not running)"
echo "  3. Runs pre-commit checks on staged files"
echo "  4. Blocks commit if checks fail"
echo ""
echo "============================================================"
echo "💡 Manual Testing:"
echo "============================================================"
echo ""
echo "  make ci-pre-commit-run         - Run on all files"
echo "  make ci-pre-commit-run-staged  - Run on staged files"
echo ""
echo "============================================================"
