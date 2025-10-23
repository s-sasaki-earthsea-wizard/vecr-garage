# よく使うコマンド

## Docker操作

### コンテナ起動・停止

```bash
# コンテナ起動
make docker-up

# コンテナ停止
make docker-down

# 再起動
make docker-restart

# ビルド＆起動
make docker-build-up

# クリーン＆ビルド
make docker-clean
make docker-build-up
```

### ログ・状態確認

```bash
# ログ確認
make docker-logs

# 状態確認
make docker-ps

# 特定サービスのログ
docker logs vecr-garage-backend-db-registration
docker logs vecr-garage-backend-llm-response
docker logs vecr-garage-db-member
docker logs vecr-garage-storage
docker logs vecr-garage-member-manager
```

## サービスアクセス

### シェル接続

```bash
# backend-db-registrationシェル
make backend-db-registration-shell

# backend-llm-responseシェル
make backend-llm-response-shell

# MinIOシェル
make storage-shell
```

### データベース接続

```bash
# PostgreSQLクライアント
make db-member-psql

# または直接接続
docker exec -it vecr-garage-db-member psql -U testuser -d member_db
```

## データベース確認

### テーブル操作

```sql
-- テーブル一覧表示
\dt

-- テーブル構造確認
\d human_members
\d virtual_members

-- データ確認
SELECT * FROM human_members;
SELECT * FROM virtual_members;

-- 件数確認
SELECT COUNT(*) FROM human_members;
SELECT COUNT(*) FROM virtual_members;

-- 終了
\q
```

### クエリ例

```sql
-- 最新5件のメンバーを取得
SELECT name, role, created_at FROM human_members
ORDER BY created_at DESC LIMIT 5;

-- 特定のスキルを持つメンバーを検索
SELECT name, skills FROM human_members
WHERE 'Python' = ANY(skills);

-- 仮想メンバーのモデル別集計
SELECT llm_model, COUNT(*) FROM virtual_members
GROUP BY llm_model;
```

## テスト実行

### backend-db-registrationテスト

```bash
# ユニットテストのみ
make backend-db-registration-test-unit

# 正常系E2Eテスト
make backend-db-registration-test-samples

# 異常系テスト
make backend-db-registration-test-cases

# 統合テスト
make backend-db-registration-test-integration
```

### システム統合テスト

```bash
# 全サービス統合テスト
make test-integration
```

## Discord操作

### Webhook通知

```bash
# Webhook一覧表示
make discord-webhooks-list

# 動作確認（推奨）
make discord-verify

# 個別テスト送信
make discord-test-kasen
make discord-test-karasuno_endo
make discord-test-rusudan

# 全Webhook同時送信
make discord-test-all

# カスタムメッセージ送信
make discord-send-message WEBHOOK=kasen_times MESSAGE="テストメッセージ"
```

### Discord Bot

```bash
# Bot起動ログ確認
make discord-bot-logs

# Bot状態確認
make discord-bot-status

# Bot設定テスト
make discord-bot-test-config

# ヘルプ表示
make discord-bot-help
```

## Claude API

```bash
# 接続テスト
make claude-test

# カスタムプロンプト送信
make claude-prompt PROMPT="Pythonで素数判定する関数を書いてください"

# ヘルプ表示
make claude-help
```

## YMLファイル操作

### Sample Files（正常系）

```bash
# 全サンプルファイルコピー
make samples-copy

# 人間メンバーのみ
make samples-copy-human

# 仮想メンバーのみ
make samples-copy-virtual

# 個別ファイルコピー
make samples-copy-single FILE=syota.yml

# サンプルファイル削除
make samples-clean

# 登録確認
make samples-verify
```

### Test Cases（異常系）

```bash
# 全テストケースコピー
make test-cases-copy

# 人間メンバーのみ
make test-cases-copy-human

# 仮想メンバーのみ
make test-cases-copy-virtual

# 個別ファイルコピー
make test-cases-copy-single FILE=invalid_missing_name.yml

# テストケース削除
make test-cases-clean

# エラー応答確認
make test-cases-verify
```

## MinIO操作

### MinIO Console

```bash
# ブラウザでアクセス
open http://localhost:9001

# 認証情報
# ユーザー名: minioadmin
# パスワード: minioadmin
```

### MinIO Client (mc)

```bash
# MinIOシェル接続
make storage-shell

# コンテナ内で実行
mc ls myminio/vecr-garage-storage/human_members/
mc ls myminio/vecr-garage-storage/virtual_members/

# ファイルアップロード
mc cp /path/to/file.yml myminio/vecr-garage-storage/human_members/

# ファイル削除
mc rm myminio/vecr-garage-storage/human_members/file.yml

# Webhook設定確認
mc admin config get myminio notify_webhook

# イベント通知設定確認
mc event list myminio/vecr-garage-storage
```

## トラブルシューティング

### コンテナが起動しない場合

```bash
# クリーン＆再ビルド
make docker-clean
make docker-build-up

# ログ確認
make docker-logs

# 個別サービスログ
docker logs vecr-garage-backend-db-registration
```

### データベース接続エラー

```bash
# ヘルスチェック確認
docker ps --format "table {{.Names}}\t{{.Status}}"
# db-memberが(healthy)であることを確認

# 手動ヘルスチェック
docker exec vecr-garage-db-member pg_isready -U testuser

# 再起動
make docker-restart
```

### ポート競合

```bash
# 使用中のポート確認
lsof -i :3000
lsof -i :3001
lsof -i :5432
lsof -i :8000
lsof -i :9000
lsof -i :9001

# プロセス停止
kill -9 <PID>
```

### Webhookが動作しない場合

```bash
# 1. MinIOのWebhook設定確認
docker exec vecr-garage-storage mc admin config get myminio notify_webhook

# 2. イベント通知設定確認
docker exec vecr-garage-storage mc event list myminio/vecr-garage-storage

# 3. backend-db-registrationログ確認
docker logs vecr-garage-backend-db-registration

# 4. 再起動
make docker-restart
```

## ヘルプ表示

```bash
# Makefile全体のヘルプ
make help

# Discord関連コマンド
make discord-help

# Discord Bot関連コマンド
make discord-bot-help

# Claude API関連コマンド
make claude-help
```

## 関連ドキュメント

- [サービス構成](../architecture/services.md)
- [テスト戦略](testing.md)
- [トラブルシューティング](troubleshooting.md)
