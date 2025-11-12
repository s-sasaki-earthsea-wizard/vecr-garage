# サービス構成

## サービス概要

VECR Garageプロジェクトは、以下の6つのコンテナサービスで構成されています。

### backend-db-registration (port: 3000)

**役割**: ストレージからメンバーデータをDBに登録

**技術スタック**:

- Python 3.11
- Flask
- SQLAlchemy
- PostgreSQL接続

**主な機能**:

- MinIO Webhookイベント受信
- YMLファイル解析とバリデーション
- メンバーデータのDB登録（UPSERT処理）
- エラーハンドリングとログ記録

**関連ドキュメント**:

- [Webhook自動化システム](webhook-automation.md)
- [データベース設計](database.md)

### backend-llm-response (port: 3001)

**役割**: LLM応答の送受信処理

**技術スタック**:

- Python 3.11
- Flask
- Anthropic Claude API
- discord.py 2.4.0
- APScheduler

**主な機能**:

- Claude APIとの連携
- Discord Bot統合（3つのモード）
  - Mention Mode: @メンション応答
  - AutoThread Mode: 自動会話応答
  - Times Mode: 1日1回自動投稿
- Discord Webhook通知

**関連ドキュメント**:

- [Discord Bot統合](../integrations/discord.md)
- [Claude API連携](../integrations/claude-api.md)

### db-member (port: 5432)

**役割**: PostgreSQLメンバーデータベース

**技術スタック**:

- PostgreSQL 15
- ヘルスチェック機能

**テーブル構成**:

- `human_members`: 人間メンバー情報
- `virtual_members`: 仮想メンバー（AI）情報

**関連ドキュメント**:

- [データベース設計](database.md)

### storage (port: 9000/9001)

**役割**: MinIOオブジェクトストレージ

**技術スタック**:

- MinIO
- S3互換API

**主な機能**:

- メンバープロフィールYMLファイルストレージ
- Webhook通知（S3イベント）
- バケット管理

**アクセス**:

- API: `http://localhost:9000`
- Console: `http://localhost:9001`

**関連ドキュメント**:

- [MinIO設定](../integrations/minio.md)
- [Webhook自動化システム](webhook-automation.md)

### member-manager (port: 8000)

**役割**: Django Webインターフェース

**技術スタック**:

- Flask
- Flask-Session
- JavaScript（モックUI）

**現在の実装状況**:

- モックアップ版（開発中）
- 環境変数ベース認証
- ハードコードされたデータ表示

**将来の実装計画**:

- PostgreSQL実連携
- Jinjaテンプレート動的レンダリング
- SQLAlchemy ORM統合

**関連ドキュメント**:

- [認証システム](../integrations/authentication.md)

### db-chat-log (port: 4566)

**役割**: LocalStack/DynamoDBチャットログ

**技術スタック**:

- LocalStack
- DynamoDB

**実装状況**: 未実装（準備中）

**将来の実装計画**:

- 会話履歴の永続化
- Discord Bot会話ログ管理
- セッション管理の改善

## サービス依存関係

```text
db-member (healthy)
  ├─→ backend-db-registration
  └─→ member-manager

storage (healthy)
  ├─→ minio-setup
  └─→ backend-db-registration

minio-setup (completed)
  └─→ minio-restarter

minio-restarter (completed)
  └─→ webhook-configurator

db-chat-log (起動中)
  └─→ backend-llm-response (将来)
```

## 環境変数

`.env`ファイルで管理：

```bash
# データベース設定
MEMBER_DB_NAME=member_db
MEMBER_DB_USER=testuser
MEMBER_DB_PASSWORD=password

# MinIO設定
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_BUCKET_NAME=vecr-garage-storage

# 認証設定
ADMIN_USERNAME=Admin
ADMIN_PASSWORD=SamplePassword
SECRET_KEY=vecr-garage-secret-key-development-only-2025

# Claude API設定
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_API_VERSION=2023-06-01
ANTHROPIC_MAX_TOKENS=4096

# Discord Bot設定
DISCORD_BOT_NAME=🤖🍡華扇

# Times Mode設定
TIMES_TEST_MODE=false
TIMES_TEST_INTERVAL=60
```

## ヘルスチェック

```bash
# 全サービスの状態確認
docker ps --format "table {{.Names}}\t{{.Status}}"

# 個別サービス確認
make backend-db-registration-shell
make backend-llm-response-shell
make db-member-psql
make storage-shell
```

## セキュリティ注意事項

- 本番環境では`.env`の認証情報を必ず変更する
- MinIOのデフォルト認証情報を使用しない
- データベースパスワードは強力なものに変更する
- APIエンドポイントには適切な認証を実装する
