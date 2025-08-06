# VECR Garage プロジェクトガイド

## プロジェクト概要

人間とAIアシスタントエンジニアが協働する仮想スタートアップオフィス「VECRガレージ」のDockerベース環境です。

## アーキテクチャ

### サービス構成

- **backend-db-registration** (port: 3000): ストレージからメンバーデータをDBに登録
- **backend-llm-response** (port: 3001): LLM応答の送受信処理
- **db-member** (port: 5432): PostgreSQLメンバーデータベース
- **storage** (port: 9000/9001): MinIOオブジェクトストレージ
- **member-manager** (port: 8000): Django Webインターフェース
- **db-chat-log** (port: 4566): LocalStack/DynamoDBチャットログ

## 開発ルール

### コーディング規約

- Python: PEP 8準拠
- 関数名: snake_case
- クラス名: PascalCase
- 定数: UPPER_SNAKE_CASE
- Docstring: Google Style

### ディレクトリ構造

```text
backend-*/
├── src/           # ソースコード
├── tests/         # テストコード
├── requirements.txt
└── Dockerfile
```

### データベース操作

- トランザクション処理を必須とする
- エラー時は必ずロールバック
- SQLAlchemyのセッション管理を適切に行う

### テスト

```bash
# backend-db-registrationのテスト
docker exec -it vecr-garage-backend-db-registration pytest tests/

# backend-llm-responseのテスト
docker exec -it vecr-garage-backend-llm-response pytest tests/
```

### 型チェック・リンター

```bash
# Python (各backendサービス内で実行)
mypy src/
ruff check src/
black src/
```

## よく使うコマンド

### Docker操作

```bash
make docker-up              # コンテナ起動
make docker-down            # コンテナ停止
make docker-restart         # 再起動
make docker-logs            # ログ確認
make docker-ps              # 状態確認
make docker-build-up        # ビルド＆起動
```

### サービスアクセス

```bash
make backend-db-registration-shell  # backend-db-registrationシェル
make backend-llm-response-shell     # backend-llm-responseシェル
make db-member-psql                 # PostgreSQLクライアント
make storage-shell                  # MinIOシェル
```

### データベース確認

```bash
# PostgreSQL接続
docker exec -it vecr-garage-db-member psql -U testuser -d member_db

# テーブル確認
\dt
\d human_members
\d virtual_members
```

## 環境変数

`.env`ファイルで管理：

- MEMBER_DB_NAME=member_db
- MEMBER_DB_USER=testuser
- MEMBER_DB_PASSWORD=password
- MINIO_ROOT_USER=minioadmin
- MINIO_ROOT_PASSWORD=minioadmin
- MINIO_BUCKET_NAME=vecr-garage-storage

## Git運用

- ブランチ戦略: feature/*, fix/*, refactor/*
- コミットメッセージ: 日本語可、動詞から始める
- PRはmainブランチへ

### コミットメッセージ規約

プレフィックスに応じた絵文字を付ける：

- ✨ feat: 新機能
- 🐛 fix: バグ修正
- 📚 docs: ドキュメント
- 🎨 style: コードスタイル修正
- ♻️ refactor: リファクタリング
- ⚡ perf: パフォーマンス改善
- ✅ test: テスト追加・修正
- 🔧 chore: ビルド・補助ツール
- 🚀 deploy: デプロイ
- 🔒 security: セキュリティ修正
- 📝 update: 更新・改善
- 🗑️ remove: 削除

**重要**: Claude Codeを使用してコミットする場合は、必ず以下の署名を含める：

```text
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## トラブルシューティング

### コンテナが起動しない場合

```bash
make docker-clean
make docker-build-up
```

### データベース接続エラー

```bash
# ヘルスチェック確認
docker ps --format "table {{.Names}}\t{{.Status}}"
# db-memberが(healthy)であることを確認
```

### ポート競合

```bash
# 使用中のポート確認
lsof -i :3000
lsof -i :5432
lsof -i :8000
lsof -i :9000
```

## セキュリティ注意事項

- 本番環境では`.env`の認証情報を必ず変更する
- MinIOのデフォルト認証情報を使用しない
- データベースパスワードは強力なものに変更する
- APIエンドポイントには適切な認証を実装する

## member-managerサービス

### 現在の実装状況（モックアップ）
- Flask + JavaScriptによるWebインターフェース
- ハードコードされたモックデータを使用
- テーブル選択、表示、編集、削除機能

### 将来の実装計画
- Jinjaテンプレートによる動的レンダリング
- PostgreSQLデータベースとの実際の連携
- SQLAlchemyによるORM実装
- MinIOストレージとの統合
- リアルタイムデータ同期

### アクセス方法
```bash
# ローカル環境
http://localhost:8000/

# Dockerコンテナ内で実行
docker exec -it vecr-garage-member-manager python app.py
```

## 認証システム

### 認証戦略ロードマップ

#### Phase 1: モックアップ認証（現在実装中）
**目的**: UI/UX検証・プロトタイピング
- 環境変数ベースの簡易認証
- セッション管理（Flask-Session）
- ログイン/ログアウト機能

```bash
# 環境変数設定例（.env.exampleから.envにコピーして使用）
ADMIN_USERNAME=vecr_admin
ADMIN_PASSWORD=vecr_secure_2025
```

#### Phase 2: セッションベース認証（次期実装）
**目的**: 開発・ステージング環境での実用化
- Flask-Login + Redis セッション管理
- CSRF保護（Flask-WTF）
- レート制限（Flask-Limiter）
- パスワードハッシュ化（bcrypt）

```python
# 技術スタック例
auth_stack = [
    "Flask-Login",      # セッション管理
    "Flask-WTF",        # CSRF保護
    "Flask-Limiter",    # レート制限
    "bcrypt",           # パスワードハッシュ化
    "Redis"             # セッションストア
]
```

#### Phase 3: 本番環境認証（将来実装）
**目的**: 本格運用・AWS統合
- AWS Cognito統合
- MFA（多要素認証）対応
- ソーシャルログイン連携
- JWT認証 + API Gateway

```yaml
# AWS統合サービス
aws_services:
  authentication: AWS Cognito
  secrets: AWS Secrets Manager
  certificates: AWS Certificate Manager
  deployment: EKS + ALB
```

### セキュリティ考慮事項

#### 現在のモックアップ段階
- ⚠️ 平文パスワード（開発専用）
- ⚠️ 簡易セッション管理
- ⚠️ HTTPS非対応（ローカル環境）

#### 将来の本番環境
- ✅ パスワードハッシュ化必須
- ✅ HTTPS通信強制
- ✅ セキュリティヘッダー設定
- ✅ 監査ログ記録

## 今後の開発予定

- [x] member-managerのモックUI実装
- [ ] member-managerとデータベースの実連携
- [ ] Jinjaテンプレートによる動的表示
- [ ] チャットログ機能の実装
- [ ] LLM連携機能の強化
- [ ] 本番環境用の設定追加
