# ============================================================
# VECR Garage - Secrets Management
# ============================================================
# .secrets.baselineの管理とマージコンフリクト解決を自動化
#
# 📋 使用方法:
#   make secrets-help              - ヘルプ表示
#   make secrets-baseline-update   - ベースライン更新
#   make secrets-baseline-merge    - マージコンフリクト解決
#   make secrets-check             - 秘密鍵チェック
#   make secrets-audit             - ベースライン監査
# ============================================================

.PHONY: secrets-help
secrets-help: ## Secrets管理のヘルプを表示
	@echo "🔒 Secrets Management Commands"
	@echo "============================================================"
	@echo "make secrets-baseline-update  - ベースラインを更新（新規スキャン）"
	@echo "make secrets-baseline-merge   - マージコンフリクト解決"
	@echo "make secrets-check            - 秘密鍵検出チェック"
	@echo "make secrets-audit            - ベースライン監査（定期レビュー用）"
	@echo ""
	@echo "📋 Workflow Examples:"
	@echo "------------------------------------------------------------"
	@echo "1. 通常の更新:"
	@echo "   make secrets-baseline-update"
	@echo "   git diff .secrets.baseline  # 変更内容を確認"
	@echo "   git add .secrets.baseline"
	@echo "   git commit -m 'update: .secrets.baseline更新'"
	@echo ""
	@echo "2. マージコンフリクト時:"
	@echo "   git pull  # コンフリクト発生"
	@echo "   make secrets-baseline-merge"
	@echo "   git add .secrets.baseline"
	@echo "   git commit -m 'merge: .secrets.baseline統合'"
	@echo ""
	@echo "3. 定期監査（四半期ごと推奨）:"
	@echo "   make secrets-audit"
	@echo "   # 各エントリを確認し、不要なものを削除"
	@echo ""
	@echo "⚠️  重要な注意事項:"
	@echo "------------------------------------------------------------"
	@echo "- ベースライン更新後は必ず内容を確認してください"
	@echo "- 本物の秘密鍵が含まれていないか慎重にチェック"
	@echo "- 疑わしい場合はコミットせず、チームで相談"
	@echo "============================================================"

.PHONY: secrets-baseline-update
secrets-baseline-update: ## .secrets.baselineを更新（新規スキャン）
	@echo "📊 Updating .secrets.baseline..."
	@$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner sh -c '\
		cp .secrets.baseline .secrets.baseline.backup 2>/dev/null || true && \
		detect-secrets scan --baseline .secrets.baseline --update && \
		echo "" && \
		echo "✅ Baseline updated successfully!" && \
		echo "📝 Next steps:" && \
		echo "   1. git diff .secrets.baseline  # 変更内容を確認" && \
		echo "   2. git add .secrets.baseline   # 問題なければステージング" && \
		echo "   3. git commit                  # コミット"'

.PHONY: secrets-baseline-merge
secrets-baseline-merge: ## マージコンフリクト時のベースライン再構築
	@echo "🔄 Resolving .secrets.baseline merge conflict..."
	@$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner sh -c '\
		if ! git show HEAD:.secrets.baseline > .secrets.baseline.ours 2>/dev/null; then \
			echo "❌ Error: Not in a merge conflict state"; \
			exit 1; \
		fi && \
		git show MERGE_HEAD:.secrets.baseline > .secrets.baseline.theirs 2>/dev/null && \
		echo "📋 Merging both baselines..." && \
		python3 -c "\
import json; \
ours = json.load(open(\".secrets.baseline.ours\")); \
theirs = json.load(open(\".secrets.baseline.theirs\")); \
ours[\"results\"].update(theirs[\"results\"]); \
json.dump(ours, open(\".secrets.baseline\", \"w\"), indent=2)" && \
		detect-secrets scan --baseline .secrets.baseline --update && \
		rm -f .secrets.baseline.ours .secrets.baseline.theirs && \
		echo "" && \
		echo "✅ Merge conflict resolved!" && \
		echo "📝 Next steps:" && \
		echo "   1. git diff .secrets.baseline  # マージ結果を確認" && \
		echo "   2. git add .secrets.baseline   # 問題なければステージング" && \
		echo "   3. git commit                  # マージコミット完了"'

.PHONY: secrets-check
secrets-check: ## 秘密鍵検出チェック（baselineを考慮）
	@echo "🔍 Checking for secrets (with baseline)..."
	@$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner \
		detect-secrets scan --baseline .secrets.baseline

.PHONY: secrets-audit
secrets-audit: ## ベースライン内の誤検知を監査（定期レビュー用）
	@echo "🔍 Auditing .secrets.baseline..."
	@echo "💡 Tip: Review each entry carefully and mark as 'real secret' if needed"
	@echo "============================================================"
	@$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner \
		detect-secrets audit .secrets.baseline

.PHONY: secrets-baseline-init
secrets-baseline-init: ## 新規プロジェクト用：ベースライン初期化
	@echo "🆕 Initializing .secrets.baseline..."
	@$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner sh -c '\
		detect-secrets scan --baseline .secrets.baseline && \
		echo "" && \
		echo "✅ Baseline initialized!" && \
		echo "📝 Please review and commit: git add .secrets.baseline"'
