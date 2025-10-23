# Discord統合

## 概要

VECR Garageプロジェクトは、2つのDiscord統合機能を提供しています：

1. **Discord Webhook通知**: backend-llm-responseからDiscordへのメッセージ送信
2. **Discord Bot**: @メンション応答、自動会話応答、1日1回自動投稿

## Discord Webhook通知システム

### セキュアなWebhook管理（✅ 実装完了）

**実装目的**: Discordへのテストメッセージ送信機能（将来的に各種通知機能を追加予定）

### 🏗️ アーキテクチャ設計

**セキュリティ重視の設計**:

1. **JSONファイル管理**: `config/discord_webhooks.json`（視認性・編集性◎）
2. **.envrc自動変換**: JSONを環境変数に変換
3. **Makefile統合**: `make docker-up/build-up`で自動読み込み
4. **環境変数渡し**: コンテナにファイルをマウントせず環境変数のみ（セキュア）

**ファイル構成**:

```
config/
├── discord_webhooks.json          # 実際のWebhook URL（.gitignore対象）
└── discord_webhooks.example.json  # サンプル（リポジトリ管理）

.envrc                              # 環境変数変換スクリプト（.gitignore対象）
.envrc.example                      # サンプル（リポジトリ管理）
```

### 🎯 実装内容

**コアモジュール**:

- `backend-llm-response/src/config/webhook_config_parser.py`: JSON/環境変数パーサー
- `backend-llm-response/src/config/webhook_validator.py`: URL形式・データ構造バリデーター
- `backend-llm-response/src/services/discord_notifier.py`: メッセージ送信サービス
- `makefiles/discord.mk`: Discord操作コマンド集約

**REST APIエンドポイント**:

- `GET /api/discord/webhooks`: Webhook一覧取得
- `POST /api/discord/test/<webhook_name>`: テストメッセージ送信
- `POST /api/discord/send/<webhook_name>`: カスタムメッセージ送信
- `POST /api/discord/broadcast`: 全Webhook同時配信

**Makeターゲット**:

```bash
make discord-webhooks-list        # Webhook一覧表示
make discord-verify               # 動作確認（推奨）
make discord-test-kasen          # 個別テスト送信
make discord-test-karasuno_endo  # 個別テスト送信
make discord-test-rusudan        # 個別テスト送信
make discord-test-all            # 全Webhook同時送信
make discord-send-message        # カスタムメッセージ
make discord-help                # コマンド一覧
```

### セットアップ手順

#### 1. Discord Webhook作成

1. Discordサーバーの設定を開く
2. 「連携サービス」→「Webhook」→「新しいWebhook」
3. Webhook名とチャンネルを設定
4. Webhook URLをコピー

#### 2. 設定ファイル作成

```bash
# サンプルファイルをコピー
cp config/discord_webhooks.example.json config/discord_webhooks.json

# Webhook URLを記入
# {
#   "kasen_times": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL",
#   "karasuno_endo_times": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL",
#   "rusudan_times": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
# }
```

#### 3. 起動

```bash
# .envrcが自動的に読み込まれる
make docker-build-up

# 動作確認
make discord-verify
```

### 🔒 セキュリティ対策

**ファイル流出防止**:

- `config/discord_webhooks.json`: .gitignoreで保護
- `.envrc`: .gitignoreで保護
- コンテナにファイルをマウントせず、環境変数として渡す

**将来の拡張性**:

- AWS Secrets Managerへの移行準備完了
- 環境変数ベースの設計により、CI/CD環境でも同様に動作

## Discord Bot統合

### backend-llm-responseサービスによるDiscord Bot実装（✅ 実装完了）

**実装目的**: Discordチャンネルで@メンションを検知し、Claude APIで応答するBot機能

### 🏗️ アーキテクチャ設計

**Discord Botクラス**:

- `backend-llm-response/src/services/discord_bot.py`
- discord.py 2.4.0を使用
- Message Content Intentを有効化（Privileged Intent）
- 指定チャンネルでの@メンション検知と自動応答
- Claude APIとの統合（ClaudeClientを使用）

**設定管理**:

- `config/discord_tokens.json`: Bot TokenとチャンネルID管理（モード別）
- JSON直接読み込み（環境変数を経由しない）
- 複数Bot対応（Bot名ごとに設定を分離）

**設定フォーマット**:

```json
{
    "🤖🍡華扇": {
        "bot_token": "YOUR_BOT_TOKEN_HERE",
        "channels": {
            "mention_mode": ["1356872662831333452"],
            "auto_thread_mode": ["1356872551019577395"],
            "times_mode": ["1356872662831333452"]
        }
    }
}
```

**モジュール構成**:

- `config/discord/config_loader.py`: JSON読み込み
- `config/discord/config_validator.py`: 設定バリデーション
- `config/discord/config_parser.py`: 公開API（Facade）

### 🤖 Bot動作仕様

#### 1. Mention Mode（@メンション対応）

**動作**:

- Botへの@メンションを検知
- メンション部分を除去してプロンプトを抽出
- Claude APIで応答生成
- 2000文字制限対応（超過時は省略表示）
- Discordチャンネルに返信

**対象チャンネル**: `config/discord_tokens.json`の`mention_mode`で指定

#### 2. AutoThread Mode（新着投稿自動応答）

**動作**:

- Bot自身以外の新着投稿を検知
- チャンネルの過去20件の会話履歴を取得
- 会話の文脈を含めてClaude APIに送信
- @メンション付きで自動返信（`message.reply()`使用）
- 無限ループ防止（Bot自身のメッセージは無視）

**対象チャンネル**: `config/discord_tokens.json`の`auto_thread_mode`で指定

**将来の改善計画**:

- [ ] **会話履歴管理の改善**（優先度: 高）
  - **現在の課題**: 過去20件の履歴を一律取得するため、終わった話題が繰り返される
  - **解決策の選択肢**:
    1. **DynamoDB統合**: ユーザーごとに会話セッションを管理（最も推奨）
    2. **トピック検出**: LLMで会話の区切りを判定し、関連する履歴のみ取得
    3. **時間ベースフィルタリング**: 直近N分間の会話のみを対象
    4. **スレッド活用**: 話題ごとにスレッドを分け、スレッド単位で履歴管理

#### 3. Times Mode（1日1回自動投稿）

**動作**:

- **本番モード**: JST 9:00-18:00の間に1日1回ランダムな話題で投稿
- **テストモード**: 短いインターバルで繰り返し投稿（機能テスト用）
- APScheduler + pytzによるJST対応スケジューラー
- jitterによるランダム投稿時刻（9時間幅、本番モードのみ）
- 話題リスト管理（`prompts/times_topics.json`）
- 1日1回フラグ管理（日付ベース、本番モードのみ）
- Claude APIで応答生成→Discord投稿
- 2000文字制限対応（超過時は省略表示）

**対象チャンネル**: `config/discord_tokens.json`の`times_mode`で指定

**環境変数設定（.env）**:

```bash
# 【本番モード】 TIMES_TEST_MODE=false (またはコメントアウト)
#   - 動作: 毎日JST 9:00-18:00の間に1回ランダム投稿
#   - 1日1回制御: 有効
TIMES_TEST_MODE=false

# 【テストモード】 TIMES_TEST_MODE=true
#   - 動作: 指定インターバルで繰り返し投稿
#   - 1日1回制御: 無効（何度でも投稿可能）
#   - 用途: 機能テスト、動作確認
# TIMES_TEST_MODE=true
# TIMES_TEST_INTERVAL=60  # テスト時の投稿間隔（秒）
```

**将来の改善計画**:

- [ ] **話題管理の改善**（優先度: 中）
  - **現在の実装**: JSONファイルにベタ書き（テスト用暫定処置）
  - **改善案**:
    1. **データベース管理**: PostgreSQLに話題テーブルを作成
    2. **動的更新**: 管理画面から話題の追加・編集・削除
    3. **カテゴリ分類**: 技術/趣味/日常などのカテゴリ別管理
    4. **重み付け**: 話題ごとに出現頻度を制御
    5. **履歴管理**: 過去に投稿した話題を記録し、重複を避ける

### セットアップ手順

#### 1. Discord Developer Portal設定

1. <https://discord.com/developers/applications> にアクセス
2. 「New Application」でBot作成
3. 「Bot」タブでTokenを取得
4. **Privileged Gateway Intents**で以下を有効化:
   - ✅ MESSAGE CONTENT INTENT（必須）
   - ✅ SERVER MEMBERS INTENT（推奨）
5. 「OAuth2」→「URL Generator」でBot招待URL生成
   - Scopes: `bot`
   - Bot Permissions:
     - View Channels
     - Send Messages
     - Read Message History
     - Create Public Threads
     - Send Messages in Threads
6. 生成されたURLでBotをDiscordサーバーに招待

#### 2. 設定ファイル作成

```bash
# サンプルファイルをコピー
cp config/discord_tokens.example.json config/discord_tokens.json

# Bot Tokenとチャンネル IDを記入
# チャンネルIDの取得方法:
# 1. Discordで開発者モードを有効化（設定→詳細設定→開発者モード）
# 2. チャンネルを右クリック→「IDをコピー」
```

#### 3. 起動

```bash
# コンテナ起動
make docker-build-up

# Bot起動ログ確認
make discord-bot-logs
```

### 📦 依存関係

**requirements.txt追加**:

- `discord.py==2.4.0`: Discord Bot公式ライブラリ
- `APScheduler==3.10.4`: Python用ジョブスケジューリングライブラリ
- `pytz==2024.1`: タイムゾーン処理ライブラリ

**docker-compose.yml設定**:

```yaml
backend-llm-response:
  volumes:
    - ./config/discord_tokens.json:/app/config/discord_tokens.json:ro
  environment:
    - DISCORD_BOT_NAME=${DISCORD_BOT_NAME:-🤖🍡華扇}
  restart: unless-stopped
```

### 🎯 利用可能なMakeコマンド

```bash
# Discord Botコマンドヘルプ
make discord-bot-help

# Discord Botログ表示
make discord-bot-logs

# Discord Bot状態確認
make discord-bot-status

# Discord Bot設定テスト
make discord-bot-test-config
```

### ✅ 動作確認

**起動確認**:

- ✅ Bot設定読み込み成功（discord_tokens.json）
- ✅ Discord Gatewayへの接続成功
- ✅ Bot起動完了: `🤖🍡華扇#8670`
- ✅ Mentionモード対象チャンネル: 1個
- ✅ AutoThreadモード対象チャンネル: 1個
- ✅ Timesモード対象チャンネル: 1個
- ✅ TimesSchedulerスケジューラー起動完了

**動作確認**:

- ✅ @メンション検知成功（Mention Mode）
- ✅ 新着投稿自動応答成功（AutoThread Mode）
- ✅ 会話履歴の文脈理解確認
- ✅ 1日1回自動投稿スケジュール設定完了（Times Mode）
- ✅ 話題リスト読み込み成功（20件）
- ✅ Claude API連携応答成功
- ✅ 2000文字制限対応確認

### 🎯 今後の拡張予定

**共通機能**:

- [ ] 複数Botの同時起動（Bot名ごとの独立プロセス）
- [ ] スレッド対応（スレッド内での会話継続）
- [ ] リアクション機能（絵文字によるコマンド操作）
- [ ] メンバープロフィール連携（db-memberとの統合）
- [ ] リッチエンベッド対応（構造化された応答表示）
- [ ] Slash Commands実装（/kasen <prompt>等）

## トラブルシューティング

### Discord Webhook

詳細は [トラブルシューティング](../development/troubleshooting.md#discord-webhook関連) を参照

### Discord Bot

詳細は [トラブルシューティング](../development/troubleshooting.md#discord-bot関連) を参照

## 関連ドキュメント

- [Claude API連携](claude-api.md)
- [サービス構成](../architecture/services.md)
- [よく使うコマンド](../development/commands.md)
