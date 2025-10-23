# ============================================================
# VECR Garage - CI/CD Makefile
# コード品質チェックとフォーマット自動化
# ============================================================

.PHONY: ci-build lint format lint-fix typecheck ci-all ci-shell ci-help test-pre-commit-install test-pre-commit-secrets test-pre-commit-all pre-commit-help

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

# ============================================================
# Pre-commit Hooks テスト
# ============================================================

test-pre-commit-install: ## Install pre-commit hooks (required for local testing)
	@echo "📦 Installing pre-commit..."
	@if command -v pre-commit >/dev/null 2>&1; then \
		echo "✅ pre-commit is already installed"; \
		pre-commit --version; \
	else \
		echo "⚠️  pre-commit is not installed. Installing..."; \
		pip install pre-commit; \
	fi
	@echo ""
	@echo "🔗 Installing pre-commit hooks to .git/hooks/..."
	@pre-commit install
	@echo "✅ Pre-commit hooks installed successfully"

test-pre-commit-secrets: ## Test pre-commit hooks secrets detection
	@echo "============================================================"
	@echo "🔒 Pre-commit Hooks Secrets検出テスト"
	@echo "============================================================"
	@echo ""
	@# pre-commitがインストールされているか確認
	@if ! command -v pre-commit >/dev/null 2>&1; then \
		echo "❌ ERROR: pre-commit is not installed"; \
		echo "   Run: make test-pre-commit-install"; \
		exit 1; \
	fi
	@echo "テスト1: Anthropic API Key 検出テスト"
	@echo "-------------------------------------------------------------"
	@echo "ANTHROPIC_API_KEY=sk-ant-test-12345-real-key" > test_secrets_anthropic.py
	@git add test_secrets_anthropic.py 2>/dev/null || true
	@if ! pre-commit run detect-secrets --files test_secrets_anthropic.py 2>&1; then \
		echo "✅ SUCCESS: Anthropic API Key が検出されました（pre-commitがブロック）"; \
		git reset HEAD test_secrets_anthropic.py 2>/dev/null || true; \
		rm -f test_secrets_anthropic.py; \
	else \
		echo "❌ FAILED: Anthropic API Key が検出されませんでした"; \
		git reset HEAD test_secrets_anthropic.py 2>/dev/null || true; \
		rm -f test_secrets_anthropic.py; \
		exit 1; \
	fi
	@echo ""
	@echo "テスト2: Discord Bot Token 検出テスト"
	@echo "-------------------------------------------------------------"
	@echo "DISCORD_BOT_TOKEN=MTxxxxxxxxxxxxxxxxxx.xxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxx" > test_secrets_discord.py
	@git add test_secrets_discord.py 2>/dev/null || true
	@if ! pre-commit run detect-secrets --files test_secrets_discord.py 2>&1; then \
		echo "✅ SUCCESS: Discord Bot Token が検出されました（pre-commitがブロック）"; \
		git reset HEAD test_secrets_discord.py 2>/dev/null || true; \
		rm -f test_secrets_discord.py; \
	else \
		echo "❌ FAILED: Discord Bot Token が検出されませんでした"; \
		git reset HEAD test_secrets_discord.py 2>/dev/null || true; \
		rm -f test_secrets_discord.py; \
		exit 1; \
	fi
	@echo ""
	@echo "テスト3: Discord Webhook URL 検出テスト"
	@echo "-------------------------------------------------------------"
	@echo "https://discord.com/api/webhooks/1234567890123456789/abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOP" > test_secrets_webhook.py
	@git add test_secrets_webhook.py 2>/dev/null || true
	@if ! pre-commit run detect-secrets --files test_secrets_webhook.py 2>&1; then \
		echo "✅ SUCCESS: Discord Webhook URL が検出されました（pre-commitがブロック）"; \
		git reset HEAD test_secrets_webhook.py 2>/dev/null || true; \
		rm -f test_secrets_webhook.py; \
	else \
		echo "❌ FAILED: Discord Webhook URL が検出されませんでした"; \
		git reset HEAD test_secrets_webhook.py 2>/dev/null || true; \
		rm -f test_secrets_webhook.py; \
		exit 1; \
	fi
	@echo ""
	@echo "テスト4: SSH秘密鍵 検出テスト"
	@echo "-------------------------------------------------------------"
	@echo "-----BEGIN RSA PRIVATE KEY-----" > test_secrets_ssh.py
	@echo "MIIEpAIBAAKCAQEA1234567890abcdefghijklmnopqrstuvwxyz" >> test_secrets_ssh.py
	@echo "-----END RSA PRIVATE KEY-----" >> test_secrets_ssh.py
	@git add test_secrets_ssh.py 2>/dev/null || true
	@if ! pre-commit run detect-private-key --files test_secrets_ssh.py 2>&1; then \
		echo "✅ SUCCESS: SSH秘密鍵 が検出されました（pre-commitがブロック）"; \
		git reset HEAD test_secrets_ssh.py 2>/dev/null || true; \
		rm -f test_secrets_ssh.py; \
	else \
		echo "❌ FAILED: SSH秘密鍵 が検出されませんでした"; \
		git reset HEAD test_secrets_ssh.py 2>/dev/null || true; \
		rm -f test_secrets_ssh.py; \
		exit 1; \
	fi
	@echo ""
	@echo "テスト5: exampleファイルは許可されることを確認"
	@echo "-------------------------------------------------------------"
	@echo "ANTHROPIC_API_KEY=sk-ant-example-value" > test_secrets.example.txt
	@git add test_secrets.example.txt 2>/dev/null || true
	@if pre-commit run detect-secrets --files test_secrets.example.txt 2>&1; then \
		echo "✅ SUCCESS: exampleファイルは除外されました（pre-commitが許可）"; \
		git reset HEAD test_secrets.example.txt 2>/dev/null || true; \
		rm -f test_secrets.example.txt; \
	else \
		echo "❌ FAILED: exampleファイルがブロックされました"; \
		git reset HEAD test_secrets.example.txt 2>/dev/null || true; \
		rm -f test_secrets.example.txt; \
		exit 1; \
	fi
	@echo ""
	@echo "============================================================"
	@echo "✅ 全てのSecretsテストが成功しました！"
	@echo "============================================================"

test-pre-commit-all: test-pre-commit-install test-pre-commit-secrets ## Run all pre-commit hooks tests
	@echo ""
	@echo "============================================================"
	@echo "✅ 全てのPre-commit Hooksテストが完了しました！"
	@echo "============================================================"

# Pre-commitコマンドヘルプ
pre-commit-help: ## Show pre-commit commands help
	@echo "============================================================"
	@echo "VECR Garage - Pre-commit Hooks Commands"
	@echo "============================================================"
	@echo ""
	@echo "📋 Available Commands:"
	@echo ""
	@echo "  make test-pre-commit-install  - Install pre-commit hooks"
	@echo "  make test-pre-commit-secrets  - Test secrets detection"
	@echo "  make test-pre-commit-all      - Run all pre-commit tests"
	@echo "  make pre-commit-help          - Show this help message"
	@echo ""
	@echo "============================================================"
	@echo "💡 Recommended Workflow:"
	@echo "============================================================"
	@echo ""
	@echo "  1. make test-pre-commit-install  - Install pre-commit"
	@echo "  2. make test-pre-commit-secrets  - Verify secrets detection"
	@echo "  3. git commit                    - Pre-commit runs automatically"
	@echo ""
	@echo "============================================================"
	@echo "🔒 What Gets Detected:"
	@echo "============================================================"
	@echo ""
	@echo "  ✓ Anthropic API Keys (sk-ant-xxxxx)"
	@echo "  ✓ Discord Bot Tokens (MTxxxxxxxxxx.xxxxxx.xxx)"
	@echo "  ✓ Discord Webhook URLs (discord.com/api/webhooks/...)"
	@echo "  ✓ SSH Private Keys (-----BEGIN RSA PRIVATE KEY-----)"
	@echo "  ✓ AWS Access Keys"
	@echo "  ✓ Database passwords in non-.env files"
	@echo ""
	@echo "============================================================"

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
