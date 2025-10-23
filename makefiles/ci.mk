# ============================================================
# VECR Garage - CI/CD Makefile
# コード品質チェックとフォーマット自動化
# ============================================================

.PHONY: ci-build lint format lint-fix typecheck ci-all ci-shell ci-help ci-pre-commit-run ci-pre-commit-run-staged ci-pre-commit-install markdown-lint markdown-fix

# CI/CDコンテナのビルド
ci-build: ## Build CI/CD container image
	@echo "🏗️  Building CI/CD container..."
	$(COMPOSE) -p $(PROJECT_NAME) build ci-runner

# Lintチェック（エラーで停止）
lint: ## Run linters for all services
	@echo "🔍 Running linters..."
	$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner /ci-scripts/lint.sh

# フォーマット自動修正
format: ## Auto-format code for all services
	@echo "🎨 Formatting code..."
	$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner /ci-scripts/format.sh

# Lint自動修正
lint-fix: ## Auto-fix linting issues for all services
	@echo "🔧 Fixing linting issues..."
	$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner /ci-scripts/lint-fix.sh

# 型チェック
typecheck: ## Run type checking for all services
	@echo "🔍 Running type checker..."
	$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner /ci-scripts/typecheck.sh

# フォーマットチェック（修正なし）
format-check: ## Check code formatting without modifying files
	@echo "🎨 Checking code format..."
	$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner bash -c "black --check backend-* member-manager"

# CI全体実行（GitHub Actions相当）
ci-all: lint format-check typecheck markdown-lint ## Run all CI checks (lint + format-check + typecheck + markdown-lint)
	@echo ""
	@echo "============================================================"
	@echo "✅ All CI checks passed!"
	@echo "============================================================"

# ============================================================
# Markdown リント・フォーマット（CI Runnerコンテナで実行）
# ============================================================

markdown-lint: ## Check Markdown files formatting (ci-runner container)
	@echo "📝 Checking Markdown formatting in CI container..."
	$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner pre-commit run markdownlint --all-files

markdown-fix: ## Auto-fix Markdown files formatting (ci-runner container)
	@echo "🔧 Fixing Markdown formatting in CI container..."
	$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner bash -c "pre-commit run markdownlint --all-files || true"
	@echo "✅ Markdown formatting fixed!"

# CI/CDコンテナのシェル起動（デバッグ用）
ci-shell: ## Open a shell in CI/CD container for debugging
	@echo "🐚 Opening CI/CD container shell..."
	$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner /bin/bash

# ============================================================
# Pre-commit Hooks（CI Runnerコンテナ実行）
# ============================================================

ci-pre-commit-run: ## Run pre-commit hooks in ci-runner container (all files)
	@echo "🔍 Running pre-commit in CI container (all files)..."
	$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner /ci-scripts/pre-commit-run.sh --all-files

ci-pre-commit-run-staged: ## Run pre-commit hooks in ci-runner container (staged files only)
	@echo "🔍 Running pre-commit in CI container (staged files)..."
	$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner /ci-scripts/pre-commit-run.sh

ci-pre-commit-install: ## Install git hooks to use ci-runner container
	@echo "🔗 Installing git hooks (CI Runner integration)..."
	@/bin/bash ci-cd/scripts/install-git-hooks.sh

# CI/CDコマンドヘルプ
ci-help: ## Show CI/CD commands help
	@echo "============================================================"
	@echo "VECR Garage - CI/CD Commands (ci-runner container)"
	@echo "============================================================"
	@echo ""
	@echo "🏗️  Setup:"
	@echo ""
	@echo "  make ci-build                  - Build CI container image"
	@echo "  make ci-pre-commit-install     - Install git hooks (recommended)"
	@echo ""
	@echo "🔍 Code Quality Checks (all run in ci-runner container):"
	@echo ""
	@echo "  make lint                      - Run linters (ruff)"
	@echo "  make format                    - Auto-format code (black)"
	@echo "  make lint-fix                  - Auto-fix linting issues"
	@echo "  make format-check              - Check formatting (no changes)"
	@echo "  make typecheck                 - Run type checker (mypy)"
	@echo "  make markdown-lint             - Check Markdown formatting"
	@echo "  make markdown-fix              - Auto-fix Markdown formatting"
	@echo "  make ci-all                    - Run all CI checks ⭐"
	@echo ""
	@echo "🐳 Pre-commit Hooks (ci-runner container):"
	@echo ""
	@echo "  make ci-pre-commit-run         - Run pre-commit (all files)"
	@echo "  make ci-pre-commit-run-staged  - Run pre-commit (staged files)"
	@echo ""
	@echo "🛠️  Debug:"
	@echo ""
	@echo "  make ci-shell                  - Open container shell"
	@echo "  make ci-help                   - Show this help"
	@echo ""
	@echo "============================================================"
	@echo "💡 Recommended Workflow:"
	@echo "============================================================"
	@echo ""
	@echo "  【初回セットアップ】"
	@echo "  1. make ci-build               - Build container"
	@echo "  2. make ci-pre-commit-install  - Install git hooks"
	@echo ""
	@echo "  【開発中】"
	@echo "  1. make format                 - Auto-format your code"
	@echo "  2. make lint-fix               - Auto-fix linting issues"
	@echo "  3. make markdown-fix           - Auto-fix Markdown"
	@echo "  4. make ci-all                 - Run all checks ⭐"
	@echo "  5. git commit                  - Hooks run automatically!"
	@echo ""
	@echo "============================================================"
	@echo "ℹ️  All commands run in ci-runner container for consistency"
	@echo "============================================================"
