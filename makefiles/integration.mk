# 統合テストのMakeタスク
# 全サービスの統合テストを実行する

.PHONY: test-integration

test-integration: ## Run comprehensive integration tests for all services
	@echo "🚀 Running full system integration test suite..."
	@echo "================================================"
	@echo "📋 Backend-DB-Registration Integration Tests"
	@echo "================================================"
	@make backend-db-registration-test-integration
	@echo ""
	@echo "================================================"
	@echo "📨 Backend-LLM-Response Integration Tests (Discord Webhook)"
	@echo "================================================"
	@make discord-verify
	@echo ""
	@echo "💡 Discord投稿の確認: 各Discordチャンネルでメッセージが届いているか目視確認してください"
	@echo ""
	@echo "🎉 All system integration tests passed successfully!"
	@echo ""
	@echo "💡 Future: Additional service tests will be added here"
	@echo "   - member-manager-test-integration"
