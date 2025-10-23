# VECR Garage プロジェクトガイド

## 📖 ドキュメントナビゲーション

このドキュメントはVECR Garageプロジェクトのマスターインデックスです。詳細な技術ドキュメントは各リンク先を参照してください。

### アーキテクチャ

- [サービス構成](docs/architecture/services.md) - 6つのコンテナサービスの詳細
- [データベース設計](docs/architecture/database.md) - PostgreSQL/DynamoDBテーブル設計
- [Webhook自動化システム](docs/architecture/webhook-automation.md) - MinIO Webhook完全自動化

### 開発ガイド

- [テスト戦略](docs/development/testing.md) - ユニット〜E2E統合テスト
- [よく使うコマンド](docs/development/commands.md) - Docker/Make/CLI操作集
- [トラブルシューティング](docs/development/troubleshooting.md) - よくある問題と解決策

### 外部連携

- [Discord統合](docs/integrations/discord.md) - Webhook通知＋Bot統合
- [Claude API連携](docs/integrations/claude-api.md) - Anthropic Claude API実装
- [MinIO設定](docs/integrations/minio.md) - オブジェクトストレージ操作
- [認証システム](docs/integrations/authentication.md) - 3段階認証ロードマップ

---

## プロジェクト概要

人間とAIアシスタントエンジニアが協働する仮想スタートアップオフィス「VECRガレージ」のDockerベース環境です。

### サービス構成（概要）

- **backend-db-registration** (port: 3000): ストレージからメンバーデータをDBに登録
- **backend-llm-response** (port: 3001): LLM応答の送受信処理
- **db-member** (port: 5432): PostgreSQLメンバーデータベース
- **storage** (port: 9000/9001): MinIOオブジェクトストレージ
- **member-manager** (port: 8000): Django Webインターフェース
- **db-chat-log** (port: 4566): LocalStack/DynamoDBチャットログ

詳細: [サービス構成](docs/architecture/services.md)

---

## 言語設定

このプロジェクトでは**日本語**での応答を行ってください。コード内のコメント、ログメッセージ、エラーメッセージ、ドキュメンテーション文字列なども日本語で記述してください。

---

## クイックスタート

### 環境起動

```bash
# コンテナ起動
make docker-build-up

# 状態確認
make docker-ps

# ログ確認
make docker-logs
```

### 動作確認

```bash
# 統合テスト実行
make test-integration

# PostgreSQL接続
make db-member-psql

# Discord Bot ログ確認
make discord-bot-logs
```

詳細: [よく使うコマンド](docs/development/commands.md)

---

## 開発ルール

### コーディング規約

- Python: PEP 8準拠
- 関数名: snake_case
- クラス名: PascalCase
- 定数: UPPER_SNAKE_CASE
- Docstring: Google Style

### データベース操作

- トランザクション処理を必須とする
- エラー時は必ずロールバック
- SQLAlchemyのセッション管理を適切に行う

詳細: [データベース設計](docs/architecture/database.md)

### テスト

```bash
# backend-db-registrationのテスト
make backend-db-registration-test-integration

# 全サービス統合テスト
make test-integration
```

詳細: [テスト戦略](docs/development/testing.md)

---

## Git運用

### ブランチ戦略

- feature/* - 新機能開発
- fix/* - バグ修正
- refactor/* - リファクタリング
- docs/* - ドキュメント更新

### コミットメッセージ規約

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

#### コミット粒度

- **1コミット = 1つの主要な変更**: 複数の独立した機能や修正を1つのコミットにまとめない
- **論理的な単位でコミット**: 関連する変更は1つのコミットにまとめる
- **段階的コミット**: 大きな変更は段階的に分割してコミット

#### Claude Code署名

Claude Codeを使用してコミットする場合は、必ず以下の署名を含める：

```text
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 開発ガイドライン

### ドキュメント更新プロセス

機能追加やPhase完了時には、以下のドキュメントを同期更新する：

1. **CLAUDE.md**: プロジェクト全体状況、Phase完了記録、技術仕様
2. **README.md**: ユーザー向け機能概要、実装状況、使用方法
3. **Makefile**: コマンドヘルプテキスト（## コメント）の更新
4. **makefiles/**: コマンドヘルプテキスト（## コメント）の更新
5. **docs/**: 詳細技術ドキュメントの更新

---

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

# Webhook設定
WEBHOOK_ETAG_CHECK_ENABLED=false
WEBHOOK_AUTO_SETUP_ENABLED=true
```

詳細: [サービス構成](docs/architecture/services.md)

---

## セキュリティ注意事項

- 本番環境では`.env`の認証情報を必ず変更する
- MinIOのデフォルト認証情報を使用しない
- データベースパスワードは強力なものに変更する
- APIエンドポイントには適切な認証を実装する

詳細: [認証システム](docs/integrations/authentication.md)

---

## 実装完了Phase記録

<details>
<summary>✅ MinIO Webhook自動化システム（クリックで展開）</summary>

**実装目的**: リポジトリクローン時の完全な再現性確保と手動設定の完全排除

**達成状況**: ✅ 完全達成 - 手動作業ゼロで環境が完全再現される

**3段階自動化アーキテクチャ**:

1. **minio-setup**: MinIO基本設定、サンプルデータコピー、webhook設定適用
2. **minio-restarter**: MinIO再起動（設定反映のため）
3. **webhook-configurator**: イベント設定とテスト実行

詳細: [Webhook自動化システム](docs/architecture/webhook-automation.md)

</details>

<details>
<summary>✅ 包括的テストシステム（クリックで展開）</summary>

**実装目的**: ユニットテストからE2Eテストまでを統合した包括的品質保証システム

**テスト結果**:

- **Unit Tests**: 25 tests passed（pytest container execution）
- **Sample Processing**: Human & Virtual member DB registration confirmed
- **Error Handling**: HTTP 400 validation errors properly handled
- **E2E Integration**: File upload → Webhook → DB registration verified

詳細: [テスト戦略](docs/development/testing.md)

</details>

<details>
<summary>✅ Discord統合（Webhook + Bot）（クリックで展開）</summary>

**Discord Webhook通知システム**:

- セキュアなWebhook管理（JSONファイル + 環境変数）
- REST API エンドポイント
- Make ターゲット統合

**Discord Bot統合**:

- **Mention Mode**: @メンション応答
- **AutoThread Mode**: 新着投稿自動応答
- **Times Mode**: 1日1回自動投稿（本番/テストモード切り替え対応）

詳細: [Discord統合](docs/integrations/discord.md)

</details>

<details>
<summary>✅ Claude API連携（クリックで展開）</summary>

**ClaudeClient実装**:

- Anthropic公式Pythonライブラリ使用
- 環境変数による設定管理
- Discord Botとの統合

**利用可能なコマンド**:

- `make claude-test` - 接続テスト
- `make claude-prompt PROMPT="テキスト"` - カスタムプロンプト送信

詳細: [Claude API連携](docs/integrations/claude-api.md)

</details>

<details>
<summary>✅ YMLファイル操作統合システム（クリックで展開）</summary>

**実装目的**: samples.mkとtest-cases.mkの重複排除とファイル操作の一元化

**統合効果**:

- AWS S3操作コードの共通化
- 1ファイルでの統一管理
- 既存コマンドの完全互換

詳細: [テスト戦略](docs/development/testing.md#ymlファイル操作統合システム)

</details>

<details>
<summary>✅ 認証システム（モックアップ版）（クリックで展開）</summary>

**Phase 1: モックアップ認証**:

- 環境変数ベースの簡易認証
- Flask-Session によるセッション管理
- ログイン/ログアウト機能
- パスワード表示切り替えボタン

**将来の実装計画**:

- Phase 2: Flask-Login + bcrypt + Redis
- Phase 3: AWS Cognito + MFA + JWT

詳細: [認証システム](docs/integrations/authentication.md)

</details>

<details>
<summary>✅ CI/CD Docker化システム（クリックで展開）</summary>

**実装目的**: 開発環境の完全な再現性確保とローカル依存の排除

**達成状況**: ✅ 完全達成 - すべてのコード品質チェックをci-runnerコンテナで実行

**実装内容**:

1. **ci-runnerコンテナ統合**: 既存のci-runnerサービスを活用
2. **pre-commitフック自動化**: Git Hooks経由でコンテナ内実行
3. **レガシーターゲット削除**: ローカル環境依存のMakeターゲットを完全削除
4. **スクリプト管理**: ci-cd/scripts/配下に実行スクリプトを配置

**利用可能なコマンド**:

- `make ci-pre-commit-run` - 全ファイルに対してpre-commit実行
- `make ci-pre-commit-run-staged` - ステージ済みファイルのみ実行
- `make ci-pre-commit-install` - Git Hooksインストール

**検証内容**:

- Black, Ruff, mypy, markdownlint
- detect-secrets（API Key漏洩検知）
- Gitコンテナ内実行（safe.directory設定）
- Node.js依存解決（libatomic1追加）

</details>

---

## 一時的な実装事項

### name-based UPSERT処理（暫定実装）

**実装目的**: ETag重複チェック問題の解決とDBリセット後の再登録対応

**現在の動作**:

- 同名メンバーが存在する場合: `updated_at`フィールドを現在時刻で更新
- 存在しない場合: 新規作成
- ETag制御によりDBリセット後の再処理が可能

**将来の実装計画**:

- file_uri（ファイルパス）をプライマリーキーとした本格的なUPSERT
- PostgreSQLの`ON CONFLICT DO UPDATE`句の活用
- ファイル単位での厳密な重複管理

詳細: [データベース設計](docs/architecture/database.md)

---

## 今後の開発予定

### 実装完了

- [x] member-managerのモックUI実装
- [x] 認証システム（モックアップ版）実装
- [x] name-based UPSERT処理（暫定実装）
- [x] MinIO Webhook自動化システム完全実装
- [x] ETag重複チェック制御機能実装
- [x] 3段階自動化アーキテクチャ実装（完全再現性達成）
- [x] s3:ObjectCreated:Copy イベント対応
- [x] 包括的テストシステム実装（ユニット〜E2E統合）
- [x] YMLファイル操作の統合システム実装
- [x] Discord Webhook通知システム実装（backend-llm-response）
- [x] Claude API連携実装（backend-llm-response）
- [x] Discord Bot統合実装（@メンション検知＋Claude API応答）
- [x] Discord Bot AutoThreadモード実装（新着投稿自動応答＋会話履歴管理）
- [x] Discord Bot Timesモード実装（1日1回自動投稿＋APScheduler統合）
- [x] Discord Bot Times Modeテスト機能実装（本番/テストモード切り替え）
- [x] CI/CD Docker化システム実装（完全コンテナベース実行）

### 実装予定

- [ ] Discord Bot Times Mode話題管理の改善（データベース化、カテゴリ分類等）
- [ ] Discord Bot会話履歴管理の改善（DynamoDB統合、トピック検出等）
- [ ] file_uri-based UPSERT処理（本格実装）
- [ ] member-managerとデータベースの実連携
- [ ] Jinjaテンプレートによる動的表示
- [ ] Flask-Login + bcryptによる認証強化
- [ ] チャットログ機能の実装（DynamoDB）
- [ ] Discord Bot機能拡張（複数Bot、スレッド対応、コンテキスト保持）
- [ ] LLM連携機能の強化（メンバープロフィールとの統合）
- [ ] Discord通知機能の拡張（定期通知、エラー通知、リッチエンベッド等）
- [ ] AWS Secrets Managerへの移行
- [ ] 本番環境用の設定追加

---

## ヘルプ・トラブルシューティング

### よく使うコマンド

```bash
# ヘルプ表示
make help
make ci-help
make discord-help
make discord-bot-help
make claude-help

# CI/CDコード品質チェック
make ci-pre-commit-run

# 統合テスト
make test-integration

# トラブルシューティング
make docker-clean
make docker-build-up
```

詳細: [よく使うコマンド](docs/development/commands.md)

### トラブルが発生した場合

詳細: [トラブルシューティング](docs/development/troubleshooting.md)

---

## ライセンス

このプロジェクトは開発中です。ライセンスについては後日決定します。
