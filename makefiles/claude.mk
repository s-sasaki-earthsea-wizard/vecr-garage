# ------------------------------------------------------------
# Claude API 関連コマンド
# ------------------------------------------------------------

# Claude API URL（.envのLLM_BASE_URLを使用）
CLAUDE_API_BASE := $(LLM_BASE_URL)/api/claude

.PHONY: claude-help claude-test claude-prompt

claude-help: ## Display Claude API commands help
	@echo "=============================================================="
	@echo "Claude API コマンド"
	@echo "=============================================================="
	@echo ""
	@echo "【基本コマンド】"
	@echo "  make claude-test              Claude APIの動作確認"
	@echo "  make claude-help              このヘルプを表示"
	@echo ""
	@echo "【プロンプト送信】"
	@echo "  make claude-prompt PROMPT=\"<テキスト>\""
	@echo "    例: make claude-prompt PROMPT=\"こんにちは！\""
	@echo ""
	@echo "=============================================================="

claude-test: ## Test Claude API connection
	@echo "🤖 Claude API接続テスト中..."
	@docker exec vecr-garage-backend-llm-response python3 -c "\
from services.claude_client import ClaudeClient; \
result = ClaudeClient().send_test_message(); \
print('✅ 接続成功!' if result['success'] else '❌ 接続失敗'); \
print(f\"モデル: {result['model']}\"); \
print(f\"プロンプト: {result['prompt']}\"); \
print(f\"応答:\n{result['response']}\" if result['success'] else f\"エラー: {result.get('error')}\"); \
"

claude-prompt: ## Send custom prompt to Claude API (Usage: make claude-prompt PROMPT="Hello")
	@if [ -z "$(PROMPT)" ]; then \
		echo "❌ エラー: PROMPT パラメータが必要です"; \
		echo ""; \
		echo "使用例:"; \
		echo "  make claude-prompt PROMPT=\"こんにちは！\""; \
		exit 1; \
	fi
	@echo "🤖 Claude APIにプロンプトを送信中..."
	@echo "プロンプト: $(PROMPT)"
	@echo ""
	@docker exec vecr-garage-backend-llm-response python3 -c "\
from services.claude_client import ClaudeClient; \
response = ClaudeClient().send_message('$(PROMPT)'); \
print('📝 応答:'); \
print(response); \
"
