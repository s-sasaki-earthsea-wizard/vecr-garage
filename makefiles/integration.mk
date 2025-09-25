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
	@echo "🎉 All system integration tests passed successfully!"
	@echo ""
	@echo "💡 Future: Additional service tests will be added here"
	@echo "   - backend-llm-response-test-integration"
	@echo "   - member-manager-test-integration"