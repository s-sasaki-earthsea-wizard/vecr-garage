# ============================================================
# backend-llm-response サービス関連コマンド
# ============================================================

# API Base URLs
DISCORD_API_BASE := $(LLM_BASE_URL)/api/discord
CLAUDE_API_BASE := $(LLM_BASE_URL)/api/claude

# jqの存在確認
JQ_EXISTS := $(shell command -v jq 2> /dev/null)

# JSON整形ヘルパー（jqが無い場合はそのまま表示）
ifdef JQ_EXISTS
    FORMAT_JSON = | jq .
else
    FORMAT_JSON =
    $(warning jqがインストールされていません。JSON出力が整形されません)
endif

# ------------------------------------------------------------
# Discord Webhook 関連コマンド
# ------------------------------------------------------------

.PHONY: discord-help discord-webhooks-list discord-test-kasen discord-test-karasuno_endo discord-test-rusudan discord-test-all discord-send-message discord-verify

discord-help: ## Display Discord Webhook commands help
	@echo "=============================================================="
	@echo "Discord Webhook コマンド"
	@echo "=============================================================="
	@echo ""
	@echo "【基本コマンド】"
	@echo "  make discord-webhooks-list    登録されているWebhook一覧を表示"
	@echo "  make discord-verify           Discord連携の動作確認"
	@echo "  make discord-help             このヘルプを表示"
	@echo ""
	@echo "【テスト送信（個別）】"
	@echo "  make discord-test-kasen          kasen_times Webhookにテスト送信"
	@echo "  make discord-test-karasuno_endo  karasuno_endo_times Webhookにテスト送信"
	@echo "  make discord-test-rusudan        rusudan_times Webhookにテスト送信"
	@echo "  make discord-test-all            全Webhookにテスト送信"
	@echo ""
	@echo "【カスタム送信】"
	@echo "  make discord-send-message WEBHOOK=<name> MESSAGE=<text>"
	@echo "    例: make discord-send-message WEBHOOK=kasen_times MESSAGE=\"Hello!\""
	@echo ""
	@echo "=============================================================="

discord-webhooks-list: ## List all registered Discord webhooks
	@echo "📋 登録されているDiscord Webhookを取得中..."
	@curl -s $(DISCORD_API_BASE)/webhooks $(FORMAT_JSON)

discord-test-kasen: ## Send test message to kasen_times webhook
	@echo "📤 kasen_times Webhookにテストメッセージを送信中..."
	@curl -s -X POST $(DISCORD_API_BASE)/test/kasen_times $(FORMAT_JSON)

discord-test-karasuno_endo: ## Send test message to karasuno_endo_times webhook
	@echo "📤 karasuno_endo_times Webhookにテストメッセージを送信中..."
	@curl -s -X POST $(DISCORD_API_BASE)/test/karasuno_endo_times $(FORMAT_JSON)

discord-test-rusudan: ## Send test message to rusudan_times webhook
	@echo "📤 rusudan_times Webhookにテストメッセージを送信中..."
	@curl -s -X POST $(DISCORD_API_BASE)/test/rusudan_times $(FORMAT_JSON)

discord-test-all: ## Send test message to all registered webhooks
	@echo "📤 全Webhookにテストメッセージを送信中..."
	@curl -s -X POST $(DISCORD_API_BASE)/broadcast \
		-H "Content-Type: application/json" \
		-d '{"content": "🤖 VECR Garage 全Webhookテスト"}' $(FORMAT_JSON)

discord-send-message: ## Send custom message to specific webhook (Usage: make discord-send-message WEBHOOK=kasen_times MESSAGE="Hello")
	@if [ -z "$(WEBHOOK)" ] || [ -z "$(MESSAGE)" ]; then \
		echo "❌ エラー: WEBHOOK と MESSAGE パラメータが必要です"; \
		echo ""; \
		echo "使用例:"; \
		echo "  make discord-send-message WEBHOOK=kasen_times MESSAGE=\"Hello World\""; \
		exit 1; \
	fi
	@echo "📤 $(WEBHOOK) Webhookにメッセージを送信中..."
	@curl -s -X POST $(DISCORD_API_BASE)/send/$(WEBHOOK) \
		-H "Content-Type: application/json" \
		-d '{"content": "$(MESSAGE)"}' $(FORMAT_JSON)

discord-verify: ## Verify Discord webhook integration (list webhooks and send test message to all)
	@echo "=============================================================="
	@echo "🔍 Discord Webhook連携 動作確認"
	@echo "=============================================================="
	@echo ""
	@echo "【ステップ1】Webhook一覧取得"
	@echo "--------------------------------------------------------------"
	@curl -s $(DISCORD_API_BASE)/webhooks $(FORMAT_JSON)
	@echo ""
	@echo "【ステップ2】全Webhookへテストメッセージ送信"
	@echo "--------------------------------------------------------------"
	@curl -s -X POST $(DISCORD_API_BASE)/broadcast \
		-H "Content-Type: application/json" \
		-d '{"content": "🤖 VECR Garage 動作確認テスト"}' $(FORMAT_JSON)
	@echo ""
	@echo "=============================================================="
	@echo "✅ Discord連携の動作確認が完了しました"
	@echo "   全Discordチャンネルにメッセージが届いているか確認してください"
	@echo "=============================================================="

# ------------------------------------------------------------
# Claude API 関連コマンド
# ------------------------------------------------------------

.PHONY: claude-help claude-test claude-prompt claude-to-discord

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
	@echo "【Claude → Discord統合】"
	@echo "  make claude-to-discord WEBHOOK=<name> PROMPT=\"<テキスト>\""
	@echo "    例: make claude-to-discord WEBHOOK=kasen_times PROMPT=\"今日の天気は？\""
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

claude-to-discord: ## Send Claude API response to Discord (Usage: make claude-to-discord WEBHOOK=kasen_times PROMPT="Hello")
	@if [ -z "$(WEBHOOK)" ] || [ -z "$(PROMPT)" ]; then \
		echo "❌ エラー: WEBHOOK と PROMPT パラメータが必要です"; \
		echo ""; \
		echo "使用例:"; \
		echo "  make claude-to-discord WEBHOOK=kasen_times PROMPT=\"今日の天気は？\""; \
		exit 1; \
	fi
	@echo "🤖 Claude APIにプロンプトを送信中..."
	@echo "Webhook: $(WEBHOOK)"
	@echo "プロンプト: $(PROMPT)"
	@echo ""
	@docker exec vecr-garage-backend-llm-response python3 -c "from services.claude_discord_bridge import ClaudeDiscordBridge; result = ClaudeDiscordBridge().send_prompt_to_discord('$(WEBHOOK)', '''$(PROMPT)'''); print('✅ 成功!' if result['success'] else '❌ 失敗'); print(f\"Claude応答をDiscord（{result['webhook_name']}）に投稿しました\" if result['success'] else f\"エラー: {result.get('error')}\");"
