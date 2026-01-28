# Lambda関数関連のMakeターゲット
# SAM CLIを使用したローカル開発・テスト

# ============================================================
# ヘルプ
# ============================================================

.PHONY: lambda-help
lambda-help: ## Lambda関連コマンドのヘルプを表示
	@echo ""
	@echo "🚀 Lambda関連コマンド"
	@echo "============================================================"
	@echo ""
	@echo "📦 ビルド:"
	@echo "  make lambda-build                    SAM CLIでLambda関数をビルド"
	@echo ""
	@echo "🧪 ローカルテスト:"
	@echo "  make lambda-invoke-human             人間メンバー登録イベントでローカル実行"
	@echo "  make lambda-invoke-virtual           仮想メンバー登録イベントでローカル実行"
	@echo "  make lambda-invoke EVENT=<file>      任意のイベントファイルでローカル実行"
	@echo ""
	@echo "🔍 検証:"
	@echo "  make lambda-validate                 SAMテンプレートの検証"
	@echo ""
	@echo "📋 その他:"
	@echo "  make lambda-logs                     Lambda関数のログを表示（デプロイ後）"
	@echo ""

# ============================================================
# 変数定義
# ============================================================

LAMBDA_DIR := backend-db-registration
SAM_TEMPLATE := $(LAMBDA_DIR)/template.yaml
EVENTS_DIR := $(LAMBDA_DIR)/events

# ============================================================
# ビルド
# ============================================================

.PHONY: lambda-build
lambda-build: ## SAM CLIでLambda関数をビルド
	@echo "📦 Lambda関数をビルド中..."
	cd $(LAMBDA_DIR) && sam build --template template.yaml
	@echo "✅ ビルド完了"

# ============================================================
# ローカルテスト
# ============================================================

.PHONY: lambda-invoke-human
lambda-invoke-human: ## 人間メンバー登録イベントでローカル実行
	@echo "🧪 人間メンバー登録イベントでLambda関数をローカル実行..."
	cd $(LAMBDA_DIR) && sam local invoke MemberRegistrationFunction \
		--event events/s3_put_human_member.json \
		--env-vars env.json 2>/dev/null || \
	cd $(LAMBDA_DIR) && sam local invoke MemberRegistrationFunction \
		--event events/s3_put_human_member.json

.PHONY: lambda-invoke-virtual
lambda-invoke-virtual: ## 仮想メンバー登録イベントでローカル実行
	@echo "🧪 仮想メンバー登録イベントでLambda関数をローカル実行..."
	cd $(LAMBDA_DIR) && sam local invoke MemberRegistrationFunction \
		--event events/s3_put_virtual_member.json \
		--env-vars env.json 2>/dev/null || \
	cd $(LAMBDA_DIR) && sam local invoke MemberRegistrationFunction \
		--event events/s3_put_virtual_member.json

.PHONY: lambda-invoke
lambda-invoke: ## 任意のイベントファイルでローカル実行 (EVENT=<file>)
ifndef EVENT
	@echo "❌ エラー: EVENT変数が指定されていません"
	@echo "使用例: make lambda-invoke EVENT=events/s3_put_human_member.json"
	@exit 1
endif
	@echo "🧪 $(EVENT) でLambda関数をローカル実行..."
	cd $(LAMBDA_DIR) && sam local invoke MemberRegistrationFunction \
		--event $(EVENT)

# ============================================================
# 検証
# ============================================================

.PHONY: lambda-validate
lambda-validate: ## SAMテンプレートの検証
	@echo "🔍 SAMテンプレートを検証中..."
	cd $(LAMBDA_DIR) && sam validate --template template.yaml
	@echo "✅ テンプレート検証完了"

# ============================================================
# ログ
# ============================================================

.PHONY: lambda-logs
lambda-logs: ## Lambda関数のログを表示（デプロイ後）
	@echo "📋 Lambda関数のログを表示..."
	sam logs --name vecr-garage-dev-member-registration --tail
