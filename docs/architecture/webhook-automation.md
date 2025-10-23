# Webhook自動化システム

## MinIO Webhook設定の完全自動化（✅ 実装完了）

**実装目的**: リポジトリクローン時の完全な再現性確保と手動設定の完全排除

### 🚀 3段階自動化アーキテクチャ

**完全自動化プロセス**: `make docker-build-up` → 手動作業ゼロでWebhookシステム稼働

#### 1. minio-setup

**役割**: MinIO基本設定、サンプルデータコピー、webhook設定適用

**処理内容**:

- MinIOバケット作成
- サンプルYMLファイルのコピー
- Webhook設定ファイル適用（`/root/.mc/config.json`）

**実装ファイル**: `scripts/minio-setup.sh`

#### 2. minio-restarter

**役割**: MinIO再起動（設定反映のため）

**処理内容**:

- Docker-in-Dockerによるコンテナ再起動
- Webhook設定の有効化

**技術的特徴**:

- `/var/run/docker.sock`マウントによるコンテナ間制御
- Alpine + docker-cliベースの軽量イメージ

#### 3. webhook-configurator

**役割**: イベント設定とテスト実行

**処理内容**:

- S3イベント通知設定（`s3:ObjectCreated:*`）
- リトライロジック（最大10回、5秒間隔）
- 動作確認テスト

**実装ファイル**: `scripts/webhook-configurator.sh`

### docker-compose.ymlサービス依存関係

```yaml
minio-setup:
  depends_on:
    storage:
      condition: service_healthy

minio-restarter:
  depends_on:
    minio-setup:
      condition: service_completed_successfully

webhook-configurator:
  depends_on:
    minio-restarter:
      condition: service_completed_successfully
```

### 🔧 主な技術改善

#### 自動化の実現方法

1. **外部スクリプト分離**: docker-composeエントリーポイントの保守性向上
2. **Docker-in-Docker**: minio-restarterサービスによるコンテナ間制御
3. **イベント対応拡張**: `s3:ObjectCreated:Copy`イベントサポート追加
4. **環境変数制御**: `WEBHOOK_ETAG_CHECK_ENABLED`による重複チェック制御

#### 影響ファイル

- `scripts/minio-setup.sh`: MinIO初期化（webhook設定のみ、イベント設定は除外）
- `scripts/webhook-configurator.sh`: イベント設定とリトライロジック（新規作成）
- `backend-db-registration/src/services/webhook_file_watcher.py`: Copy イベント対応とETag制御
- `docker-compose.yml`: 3段階サービス依存関係実装

### 🧪 テスト結果

#### 完全再現性テスト

**手順**: `make docker-down` → `make docker-build-up`

**結果**:

- ✅ 人間メンバー: 2件自動登録 (Syota, Rin)
- ✅ 仮想メンバー: 2件自動登録 (華扇, Darcy)
- ✅ 異常系ファイル: HTTP 400で適切にエラー処理
- ✅ 手動作業: 完全にゼロ

#### 環境変数設定

```bash
# ETag重複チェック機能の有効/無効制御
# 本番環境: true (重複処理を防ぐ)
# 開発環境: false (DBリセット後の再処理を可能にする)
WEBHOOK_ETAG_CHECK_ENABLED=false

# docker-compose起動時のWebhook自動設定を制御
WEBHOOK_AUTO_SETUP_ENABLED=true
```

#### 現在の動作

- `WEBHOOK_ETAG_CHECK_ENABLED=false`: 同じファイルでも毎回処理実行（開発環境向け）
- `WEBHOOK_ETAG_CHECK_ENABLED=true`: 重複ファイルはスキップ（本番環境向け）
- 自動的なMinIOバケット作成、サンプルデータコピー、Webhook設定
- s3:ObjectCreated:* イベント（Put, Post, CompleteMultipartUpload, Copy）の完全サポート

### 技術的改善

- TTY問題の適切な処理とフォールバック機能
- リトライロジックによる堅牢性向上
- 詳細なログ出力による運用性向上
- 設定の外部化による保守性向上
- Docker-in-Dockerによるコンテナ間操作の実現

### 🎯 完全自動化の達成

**ユーザー要求**:「手動での設定は一切排除してください。環境の再現性が失われます。docker-compose.ymlやMakefileの更新のみを行い、make docker-build-upで環境が再現されるようにしてください」

✅ **達成状況**: 完全達成 - 手動作業ゼロで環境が完全再現される

## Webhookイベント処理フロー

```
1. MinIOバケットへのファイルアップロード
   ↓
2. S3イベント通知（s3:ObjectCreated:*）
   ↓
3. MinIO Webhook → backend-db-registration (POST http://backend-db-registration:3000/webhook)
   ↓
4. webhook_file_watcher.py: イベント受信
   ↓
5. ETag重複チェック（WEBHOOK_ETAG_CHECK_ENABLED=trueの場合）
   ↓
6. YMLファイル取得＆バリデーション
   ↓
7. データベース登録（UPSERT）
   ↓
8. HTTP 200 (成功) / HTTP 400 (バリデーションエラー) レスポンス
```

## トラブルシューティング

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

### ETag重複チェック問題

**症状**: DBリセット後にファイルが再処理されない

**解決策**:

```bash
# .envファイルでETagチェックを無効化
WEBHOOK_ETAG_CHECK_ENABLED=false

# コンテナ再起動
make docker-restart
```

## 関連ドキュメント

- [サービス構成](services.md)
- [MinIO設定](../integrations/minio.md)
- [テスト戦略](../development/testing.md)
