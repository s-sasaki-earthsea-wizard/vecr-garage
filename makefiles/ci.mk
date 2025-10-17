# ============================================================
# VECR Garage - CI/CD Makefile
# コード品質チェックとフォーマット自動化
# ============================================================

.PHONY: ci-build lint format lint-fix typecheck ci-all ci-shell ci-help

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
ci-all: lint format-check typecheck ## Run all CI checks (lint + format-check + typecheck)
	@echo ""
	@echo "============================================================"
	@echo "✅ All CI checks passed!"
	@echo "============================================================"

# CI/CDコンテナのシェル起動（デバッグ用）
ci-shell: ## Open a shell in CI/CD container for debugging
	@echo "🐚 Opening CI/CD container shell..."
	$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner /bin/bash

# CI/CDコマンドヘルプ
ci-help: ## Show CI/CD commands help
	@echo "============================================================"
	@echo "VECR Garage - CI/CD Commands"
	@echo "============================================================"
	@echo ""
	@echo "📋 Available Commands:"
	@echo ""
	@echo "  make ci-build        - Build CI/CD container image"
	@echo "  make lint            - Run linters (ruff) for all services"
	@echo "  make format          - Auto-format code (black) for all services"
	@echo "  make lint-fix        - Auto-fix linting issues"
	@echo "  make format-check    - Check formatting without modifying files"
	@echo "  make typecheck       - Run type checker (mypy)"
	@echo "  make ci-all          - Run all CI checks (recommended before PR)"
	@echo "  make ci-shell        - Open CI/CD container shell for debugging"
	@echo "  make ci-help         - Show this help message"
	@echo ""
	@echo "============================================================"
	@echo "💡 Recommended Workflow:"
	@echo "============================================================"
	@echo ""
	@echo "  1. make format       - Auto-format your code"
	@echo "  2. make lint-fix     - Auto-fix linting issues"
	@echo "  3. make ci-all       - Run all checks before commit"
	@echo "  4. git commit        - Commit your changes"
	@echo ""
	@echo "============================================================"
