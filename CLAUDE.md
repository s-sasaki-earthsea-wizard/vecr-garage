# VECR Garage プロジェクトガイド

## プロジェクト概要

人間とAIアシスタントエンジニアが協働する仮想スタートアップオフィス「VECRガレージ」のDockerベース環境です。

## 言語設定

このプロジェクトでは**日本語**での応答を行ってください。コード内のコメント、ログメッセージ、エラーメッセージ、ドキュメンテーション文字列なども日本語で記述してください。

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
# backend-db-registrationのテスト（統合Makefileターゲット使用）
make backend-db-registration-test

# backend-llm-responseのテスト
docker exec -it vecr-garage-backend-llm-response pytest tests/
```

#### テストケース設計

**正常系テスト**:
- `data/samples/human_members/`: 人間メンバーの正常な登録ファイル
- `data/samples/virtual_members/`: 仮想メンバーの正常な登録ファイル

**異常系テスト**:
- `data/test_cases/human_members/`: 人間メンバーの異常系テストケース
  - `invalid_missing_name.yml`: nameフィールド欠損（ValidationError）
  - `invalid_empty_file.yml`: 空ファイル（'NoneType' object エラー）
- `data/test_cases/virtual_members/`: 仮想メンバーの異常系テストケース
  - `invalid_missing_name.yml`: nameフィールド欠損（ValidationError）
  - `invalid_missing_model.yml`: llm_modelフィールド欠損（ValidationError）

#### バリデーション処理

**エラーハンドリング設計**:
- `process_file_event`: 純粋なファイル処理の責任（単一責任の原則）
- `handle_webhook`: 例外処理とエラーログの統一管理
- ValidationError、DatabaseError、その他の例外を適切に分離
- 異常系ファイルは確実にエラーとして検出され、HTTP 400で応答

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

## 開発ガイドライン

### ドキュメント更新プロセス

機能追加やPhase完了時には、以下のドキュメントを同期更新する：

1. **CLAUDE.md**: プロジェクト全体状況、Phase完了記録、技術仕様
2. **README.md**: ユーザー向け機能概要、実装状況、使用方法
3. **Makefile**: コマンドヘルプテキスト（## コメント）の更新
4. **makefiles/**: コマンドヘルプテキスト（## コメント）の更新

### コミットメッセージ規約

#### コミット粒度
- **1コミット = 1つの主要な変更**: 複数の独立した機能や修正を1つのコミットにまとめない
- **論理的な単位でコミット**: 関連する変更は1つのコミットにまとめる
- **段階的コミット**: 大きな変更は段階的に分割してコミット

#### プレフィックスと絵文字
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
# ローカル環境（認証が必要）
http://localhost:8000/

# ログインページに自動リダイレクト
http://localhost:8000/login

# 認証情報は .env.example の ADMIN_USERNAME / ADMIN_PASSWORD を参照
# デフォルト: Admin / SamplePassword

# Dockerコンテナ内で実行
docker exec -it vecr-garage-member-manager python app.py
```

## 認証システム

### 認証戦略ロードマップ

#### Phase 1: モックアップ認証（✅ 実装済み）
**目的**: UI/UX検証・プロトタイピング
- 環境変数ベースの簡易認証
- セッション管理（Flask-Session）
- ログイン/ログアウト機能
- パスワード表示切り替えボタン（👁️/🙈）

```bash
# 環境変数設定例（.env.exampleから.envにコピーして使用）
ADMIN_USERNAME=Admin
ADMIN_PASSWORD=SamplePassword
SECRET_KEY=vecr-garage-secret-key-development-only-2025
```

**実装済み機能:**
- 美しいログインページデザイン
- セッション管理とリダイレクト
- 全API保護（@login_required）
- ログアウト機能

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

## Webhook自動化システム

### MinIO Webhook設定の完全自動化（✅ 実装完了）

**実装目的**: リポジトリクローン時の完全な再現性確保と手動設定の完全排除

#### 🚀 3段階自動化アーキテクチャ

**完全自動化プロセス**: `make docker-build-up` → 手動作業ゼロでWebhookシステム稼働

1. **minio-setup** → MinIO基本設定、サンプルデータコピー、webhook設定適用
2. **minio-restarter** → MinIO再起動（設定反映のため）
3. **webhook-configurator** → イベント設定とテスト実行

**docker-compose.ymlサービス依存関係**:
```yaml
minio-setup:
  depends_on: [storage: service_healthy]
minio-restarter:
  depends_on: [minio-setup: service_completed_successfully]
webhook-configurator:
  depends_on: [minio-restarter: service_completed_successfully]
```

#### 🔧 主な技術改善

**自動化の実現方法**:
1. **外部スクリプト分離**: docker-composeエントリーポイントの保守性向上
2. **Docker-in-Docker**: minio-restarterサービスによるコンテナ間制御
3. **イベント対応拡張**: `s3:ObjectCreated:Copy`イベントサポート追加
4. **環境変数制御**: `WEBHOOK_ETAG_CHECK_ENABLED`による重複チェック制御

**影響ファイル**:
- `scripts/minio-setup.sh`: MinIO初期化（webhook設定のみ、イベント設定は除外）
- `scripts/webhook-configurator.sh`: イベント設定とリトライロジック（新規作成）
- `backend-db-registration/src/services/webhook_file_watcher.py`: Copy イベント対応とETag制御
- `docker-compose.yml`: 3段階サービス依存関係実装

#### 🧪 テスト結果

**完全再現性テスト** (`make docker-down` → `make docker-build-up`):
- ✅ 人間メンバー: 2件自動登録 (Syota, Rin)
- ✅ 仮想メンバー: 2件自動登録 (華扇, Darcy)
- ✅ 異常系ファイル: HTTP 400で適切にエラー処理
- ✅ 手動作業: 完全にゼロ

**環境変数設定**:
```bash
# ETag重複チェック機能の有効/無効制御
# 本番環境: true (重複処理を防ぐ)
# 開発環境: false (DBリセット後の再処理を可能にする)
WEBHOOK_ETAG_CHECK_ENABLED=false

# docker-compose起動時のWebhook自動設定を制御
WEBHOOK_AUTO_SETUP_ENABLED=true
```

**現在の動作**:
- `WEBHOOK_ETAG_CHECK_ENABLED=false`: 同じファイルでも毎回処理実行（開発環境向け）
- `WEBHOOK_ETAG_CHECK_ENABLED=true`: 重複ファイルはスキップ（本番環境向け）
- 自動的なMinIOバケット作成、サンプルデータコピー、Webhook設定
- s3:ObjectCreated:* イベント（Put, Post, CompleteMultipartUpload, Copy）の完全サポート

**技術的改善**:
- TTY問題の適切な処理とフォールバック機能
- リトライロジックによる堅牢性向上
- 詳細なログ出力による運用性向上
- 設定の外部化による保守性向上
- Docker-in-Dockerによるコンテナ間操作の実現

#### 🎯 完全自動化の達成

**ユーザー要求**:「手動での設定は一切排除してください。環境の再現性が失われます。docker-compose.ymlやMakefileの更新のみを行い、make docker-build-upで環境が再現されるようにしてください」

✅ **達成状況**: 完全達成 - 手動作業ゼロで環境が完全再現される

## 包括的テストシステム

### backend-db-registrationテスト統合アーキテクチャ（✅ 実装完了）

**実装目的**: ユニットテストからE2Eテストまでを統合した包括的品質保証システム

#### 🏗️ テストシステム構成

**テストファイル構成**:
- `makefiles/backend-db-registration-tests.mk`: backend-db-registration専用テスト集約
- `makefiles/yml-file-operations.mk`: YMLファイル操作統合システム
- `makefiles/integration.mk`: サービス横断統合テスト

**既存のpytestユニットテストを活用**:
- 25の包括的テストケース（正常・異常系）
- docker exec による実際のコンテナ内実行
- 実データベース接続での検証

#### 🧪 テストターゲット体系

**backend-db-registration専用テスト**:
```makefile
backend-db-registration-test-unit         # ユニットテストのみ
backend-db-registration-test-samples      # 正常系E2Eテスト（DB登録確認）
backend-db-registration-test-cases        # 異常系エラーハンドリング（HTTP 400確認）
backend-db-registration-test-integration  # 上記すべて統合実行
```

**システム統合テスト**:
```makefile
test-integration  # 全サービス統合（現在はbackend-db-registrationのみ）
```

#### ✅ テスト結果

**包括的テスト実行結果**:
- **Unit Tests**: 25 tests passed（pytest container execution）
- **Sample Processing**: Human & Virtual member DB registration confirmed
- **Error Handling**: HTTP 400 validation errors properly handled
- **E2E Integration**: File upload → Webhook → DB registration verified

**自動クリーンアップ**:
- テストファイル自動削除
- 副作用なしの隔離されたテスト実行

#### 🎯 実現した価値

**テストカバレッジ**:
- **Unit Level**: コアロジックの品質保証
- **Integration Level**: Webhook処理の動作確認
- **E2E Level**: ファイルからDB登録までの全工程検証

**開発効率向上**:
- 段階的実行可能（個別テスト対応）
- 既存pytestリソースの最大活用
- 統合実行での包括的品質確認

## YMLファイル操作統合システム

### ファイル操作の統一管理（✅ 実装完了）

**実装目的**: samples.mkとtest-cases.mkの重複排除とファイル操作の一元化

#### 📁 統合アーキテクチャ

**統合前の課題**:
- samples.mkとtest-cases.mkで類似処理の重複
- ファイル操作ロジックの分散
- 保守性の低下

**統合後の構成**:
- `makefiles/yml-file-operations.mk`: 全YMLファイル操作を統合
- samples.mk, test-cases.mk: 削除済み
- 完全な後方互換性を保持

#### 🎯 利用可能なコマンド

**Sample Files (正常系)**:
```makefile
samples-copy, samples-copy-human, samples-copy-virtual
samples-copy-single, samples-clean, samples-verify
```

**Test Cases (異常系)**:
```makefile
test-cases-copy, test-cases-copy-human, test-cases-copy-virtual
test-cases-copy-single, test-cases-clean, test-cases-verify
```

#### ✨ 統合効果

**重複排除**: AWS S3操作コードの共通化
**保守性向上**: 1ファイルでの統一管理
**機能性保持**: 既存コマンドの完全互換

## 一時的な実装事項

### name-based UPSERT処理（暫定実装）

**実装目的**: ETag重複チェック問題の解決とDBリセット後の再登録対応

**実装範囲**:
- `save_or_update_human_member()`: 人間メンバーのUPSERT処理
- `save_or_update_virtual_member()`: 仮想メンバーのUPSERT処理

**影響ファイル**:
- `backend-db-registration/src/db/database.py`: UPSERT関数実装
- `backend-db-registration/src/operations/member_registration.py`: UPSERT関数使用
- `backend-db-registration/src/services/webhook_file_watcher.py`: ETag制御ロジック実装

**現在の動作**:
- 同名メンバーが存在する場合: `updated_at`フィールドを現在時刻で更新
- 存在しない場合: 新規作成
- ETag制御によりDBリセット後の再処理が可能

**将来の実装計画**:
- file_uri（ファイルパス）をプライマリーキーとした本格的なUPSERT
- PostgreSQLの`ON CONFLICT DO UPDATE`句の活用
- ファイル単位での厳密な重複管理

## 今後の開発予定

- [x] member-managerのモックUI実装
- [x] 認証システム（モックアップ版）実装
- [x] name-based UPSERT処理（暫定実装）
- [x] **MinIO Webhook自動化システム完全実装**
- [x] **ETag重複チェック制御機能実装**
- [x] **3段階自動化アーキテクチャ実装（完全再現性達成）**
- [x] **s3:ObjectCreated:Copy イベント対応**
- [x] **包括的テストシステム実装（ユニット〜E2E統合）**
- [x] **YMLファイル操作の統合システム実装**
- [ ] file_uri-based UPSERT処理（本格実装）
- [ ] member-managerとデータベースの実連携
- [ ] Jinjaテンプレートによる動的表示
- [ ] Flask-Login + bcryptによる認証強化
- [ ] チャットログ機能の実装
- [ ] LLM連携機能の強化
- [ ] 本番環境用の設定追加
