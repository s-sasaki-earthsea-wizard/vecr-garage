# MinIO設定

## MinIOオブジェクトストレージ

**役割**: メンバープロフィールYMLファイルのストレージとWebhook通知

### アクセス情報

**API エンドポイント**:

- `http://localhost:9000` (S3互換API)

**Console Web UI**:

- `http://localhost:9001` (管理画面)

**認証情報**:

```bash
ユーザー名: minioadmin
パスワード: minioadmin
```

⚠️ **セキュリティ注意**: 本番環境では必ずデフォルト認証情報を変更すること

### バケット構成

**バケット名**: `vecr-garage-storage`

**ディレクトリ構造**:

```
vecr-garage-storage/
├── human_members/          # 人間メンバーYMLファイル
│   ├── syota.yml
│   ├── rin.yml
│   └── ...
└── virtual_members/        # 仮想メンバーYMLファイル
    ├── kasen.yml
    ├── darcy.yml
    └── ...
```

### MinIO Client (mc) 操作

#### シェル接続

```bash
# MinIOシェル接続
make storage-shell

# または
docker exec -it vecr-garage-storage sh
```

#### 基本コマンド

**ファイル一覧**:

```bash
# バケット一覧
mc ls myminio/

# 人間メンバーファイル一覧
mc ls myminio/vecr-garage-storage/human_members/

# 仮想メンバーファイル一覧
mc ls myminio/vecr-garage-storage/virtual_members/
```

**ファイルアップロード**:

```bash
# ローカルファイルをアップロード
mc cp /path/to/file.yml myminio/vecr-garage-storage/human_members/

# ディレクトリごとアップロード
mc cp --recursive /path/to/dir/ myminio/vecr-garage-storage/human_members/
```

**ファイルダウンロード**:

```bash
# ファイルをダウンロード
mc cp myminio/vecr-garage-storage/human_members/syota.yml /tmp/

# ディレクトリごとダウンロード
mc cp --recursive myminio/vecr-garage-storage/human_members/ /tmp/members/
```

**ファイル削除**:

```bash
# 単一ファイル削除
mc rm myminio/vecr-garage-storage/human_members/test.yml

# ディレクトリごと削除
mc rm --recursive myminio/vecr-garage-storage/test_dir/
```

**ファイル詳細表示**:

```bash
# ファイルメタデータ表示
mc stat myminio/vecr-garage-storage/human_members/syota.yml
```

### Webhook設定

#### Webhook設定確認

```bash
# Webhook設定表示
docker exec vecr-garage-storage mc admin config get myminio notify_webhook

# 出力例:
# notify_webhook:1 endpoint="http://backend-db-registration:3000/webhook" queue_dir="" queue_limit="0"
```

#### イベント通知設定確認

```bash
# イベント設定一覧
docker exec vecr-garage-storage mc event list myminio/vecr-garage-storage

# 出力例:
# arn:minio:sqs::1:webhook  s3:ObjectCreated:*  Filter: suffix=""
```

#### サポートされるイベント

- `s3:ObjectCreated:Put`: PUTによるファイル作成
- `s3:ObjectCreated:Post`: POSTによるファイル作成
- `s3:ObjectCreated:Copy`: COPYによるファイル作成
- `s3:ObjectCreated:CompleteMultipartUpload`: マルチパートアップロード完了
- `s3:ObjectCreated:*`: 上記すべて（現在の設定）

### 自動セットアップ

**完全自動化**: 詳細は [Webhook自動化システム](../architecture/webhook-automation.md) を参照

**処理フロー**:

1. `minio-setup`: バケット作成、サンプルデータコピー、webhook設定
2. `minio-restarter`: MinIO再起動（設定反映）
3. `webhook-configurator`: イベント設定とテスト実行

**実行コマンド**:

```bash
# 完全自動セットアップ
make docker-build-up
```

### S3互換API使用例

#### Python (boto3)

```python
import boto3

# MinIO接続設定
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    region_name='us-east-1'
)

# ファイルアップロード
s3_client.upload_file(
    '/path/to/local/file.yml',
    'vecr-garage-storage',
    'human_members/new_member.yml'
)

# ファイルダウンロード
s3_client.download_file(
    'vecr-garage-storage',
    'human_members/syota.yml',
    '/tmp/syota.yml'
)

# ファイル一覧取得
response = s3_client.list_objects_v2(
    Bucket='vecr-garage-storage',
    Prefix='human_members/'
)
for obj in response.get('Contents', []):
    print(obj['Key'])
```

#### AWS CLI

```bash
# MinIOエイリアス設定
aws configure set aws_access_key_id minioadmin
aws configure set aws_secret_access_key minioadmin
aws configure set region us-east-1

# ファイル一覧
aws --endpoint-url http://localhost:9000 s3 ls s3://vecr-garage-storage/human_members/

# ファイルアップロード
aws --endpoint-url http://localhost:9000 s3 cp file.yml s3://vecr-garage-storage/human_members/

# ファイルダウンロード
aws --endpoint-url http://localhost:9000 s3 cp s3://vecr-garage-storage/human_members/syota.yml /tmp/
```

### Web UIでの操作

1. ブラウザで `http://localhost:9001` にアクセス
2. ユーザー名: `minioadmin` / パスワード: `minioadmin` でログイン
3. 左メニューから「Buckets」→「vecr-garage-storage」を選択
4. ファイルのアップロード/ダウンロード/削除が可能

**主な機能**:

- ファイルブラウザ
- ファイルアップロード（ドラッグ＆ドロップ対応）
- ファイルダウンロード
- ファイル削除
- バケット管理
- ユーザー管理
- アクセス制御（ポリシー設定）

### バックアップ・リストア

#### バックアップ（ミラーリング）

```bash
# MinIOバケット全体をローカルにバックアップ
mc mirror myminio/vecr-garage-storage /backup/vecr-garage-storage

# 差分バックアップ（--overwrite=newer）
mc mirror --overwrite=newer myminio/vecr-garage-storage /backup/vecr-garage-storage
```

#### リストア

```bash
# ローカルバックアップからMinIOにリストア
mc mirror /backup/vecr-garage-storage myminio/vecr-garage-storage
```

### セキュリティ設定

#### 本番環境での推奨設定

1. **認証情報変更**:

```bash
# .envファイル
MINIO_ROOT_USER=your-secure-username
MINIO_ROOT_PASSWORD=your-secure-password-min-8-chars
```

2. **HTTPS有効化**:

```bash
# 証明書配置
mkdir -p /path/to/certs
# server.crt, server.key を配置

# docker-compose.yml
volumes:
  - /path/to/certs:/root/.minio/certs
```

3. **アクセスポリシー設定**:

```bash
# 読み取り専用ポリシー作成
mc admin policy add myminio readonly-policy /path/to/readonly-policy.json

# ユーザーにポリシー適用
mc admin policy set myminio readonly-policy user=readonly-user
```

4. **監査ログ有効化**:

```bash
# docker-compose.yml
environment:
  - MINIO_AUDIT_WEBHOOK_ENABLE=on
  - MINIO_AUDIT_WEBHOOK_ENDPOINT=http://audit-service:8080
```

### モニタリング

#### ストレージ使用量確認

```bash
# バケット使用量
mc du myminio/vecr-garage-storage

# 詳細表示
mc du --recursive myminio/vecr-garage-storage
```

#### ヘルスチェック

```bash
# MinIOヘルスチェック
docker exec vecr-garage-storage mc admin info myminio

# コンテナヘルスチェック
docker ps --format "table {{.Names}}\t{{.Status}}" | grep storage
```

### トラブルシューティング

詳細は [トラブルシューティング](../development/troubleshooting.md#minio関連) を参照

**よくある問題**:

- Webhook通知が届かない → イベント設定確認
- ファイルアップロードできない → 認証情報確認
- Console にアクセスできない → ポート9001の競合確認

### 環境変数

```bash
# .envファイル
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_BUCKET_NAME=vecr-garage-storage

# Webhook自動設定制御
WEBHOOK_AUTO_SETUP_ENABLED=true
```

### 関連ドキュメント

- [Webhook自動化システム](../architecture/webhook-automation.md)
- [サービス構成](../architecture/services.md)
- [よく使うコマンド](../development/commands.md)
- [MinIO公式ドキュメント](https://min.io/docs/minio/linux/index.html)
