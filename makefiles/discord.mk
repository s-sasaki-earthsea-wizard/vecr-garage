# ------------------------------------------------------------
# Discord Webhook 関連コマンド
# ------------------------------------------------------------

# Discord Webhook API URL（.envのLLM_BASE_URLを使用）
DISCORD_API_BASE := $(LLM_BASE_URL)/api/discord

# jqの存在確認
JQ_EXISTS := $(shell command -v jq 2> /dev/null)

# JSON整形ヘルパー（jqが無い場合はそのまま表示）
ifdef JQ_EXISTS
    FORMAT_JSON = | jq .
else
    FORMAT_JSON =
    $(warning jqがインストールされていません。JSON出力が整形されません)
endif

.PHONY: discord-help discord-webhooks-list discord-test-kasen discord-test-all discord-send-message discord-verify

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
	@echo "【テスト送信】"
	@echo "  make discord-test-kasen       kasen_times Webhookにテスト送信"
	@echo "  make discord-test-all         全Webhookにテスト送信"
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

discord-verify: ## Verify Discord webhook integration (list webhooks and send test message)
	@echo "=============================================================="
	@echo "🔍 Discord Webhook連携 動作確認"
	@echo "=============================================================="
	@echo ""
	@echo "【ステップ1】Webhook一覧取得"
	@echo "--------------------------------------------------------------"
	@curl -s $(DISCORD_API_BASE)/webhooks $(FORMAT_JSON)
	@echo ""
	@echo "【ステップ2】テストメッセージ送信"
	@echo "--------------------------------------------------------------"
	@curl -s -X POST $(DISCORD_API_BASE)/test/kasen_times $(FORMAT_JSON)
	@echo ""
	@echo "=============================================================="
	@echo "✅ Discord連携の動作確認が完了しました"
	@echo "   Discordチャンネルにメッセージが届いているか確認してください"
	@echo "=============================================================="
