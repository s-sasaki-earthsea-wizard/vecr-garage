# VECR Garage ドキュメント

このディレクトリには、VECR Garageプロジェクトの詳細な技術ドキュメントが含まれています。

## 📁 ドキュメント構成

### architecture/ - アーキテクチャドキュメント

システム設計とインフラストラクチャに関する詳細なドキュメント

- [services.md](architecture/services.md) - 6つのコンテナサービスの詳細仕様
- [database.md](architecture/database.md) - PostgreSQL/DynamoDBテーブル設計とデータモデル
- [webhook-automation.md](architecture/webhook-automation.md) - MinIO Webhook完全自動化システム

### development/ - 開発ガイド

開発者向けのガイドとリファレンス

- [testing.md](development/testing.md) - ユニット〜E2E統合テストの包括的ガイド
- [commands.md](development/commands.md) - Docker/Make/CLIコマンド操作集
- [troubleshooting.md](development/troubleshooting.md) - よくある問題と解決策

### integrations/ - 外部連携

外部サービスとの統合に関するドキュメント

- [discord.md](integrations/discord.md) - Discord Webhook通知＋Bot統合（3つのモード）
- [claude-api.md](integrations/claude-api.md) - Anthropic Claude API連携実装
- [minio.md](integrations/minio.md) - MinIOオブジェクトストレージ操作ガイド
- [authentication.md](integrations/authentication.md) - 3段階認証システムロードマップ

## 🚀 クイックリンク

### 初めての方へ

1. [プロジェクト概要](../CLAUDE.md) - マスターインデックス
2. [サービス構成](architecture/services.md) - システム全体像
3. [よく使うコマンド](development/commands.md) - 基本操作

### 開発者向け

1. [テスト戦略](development/testing.md) - テスト実行方法
2. [データベース設計](architecture/database.md) - DB操作ガイド
3. [トラブルシューティング](development/troubleshooting.md) - 問題解決

### 統合機能

1. [Discord統合](integrations/discord.md) - Webhook + Bot設定
2. [Claude API連携](integrations/claude-api.md) - LLM統合
3. [MinIO設定](integrations/minio.md) - ストレージ操作

## 📝 ドキュメント更新ガイドライン

### 更新タイミング

以下のタイミングでドキュメントを更新してください：

- 新機能の追加時
- Phase完了時
- アーキテクチャ変更時
- バグ修正で仕様変更がある場合

### 更新対象ファイル

機能追加やPhase完了時には、以下を同期更新：

1. **CLAUDE.md**: プロジェクト全体状況、Phase完了記録
2. **README.md**: ユーザー向け機能概要
3. **docs/**: 詳細技術ドキュメント
4. **Makefile**: コマンドヘルプテキスト（## コメント）

### 執筆スタイル

- **言語**: 日本語
- **形式**: GitHub Flavored Markdown
- **トーン**: 技術的かつ簡潔
- **コードブロック**: 言語指定必須（```bash,```python等）

### ドキュメントテンプレート

```markdown
# タイトル

## 概要

簡潔な説明（1-2段落）

## 実装内容

### 主な機能

- 機能1
- 機能2

### 技術スタック

- ライブラリ1
- ライブラリ2

## 使用方法

```bash
# コマンド例
make example-command
```

## トラブルシューティング

詳細: [トラブルシューティング](../development/troubleshooting.md)

## 関連ドキュメント

- [関連ドキュメント1](link1.md)
- [関連ドキュメント2](link2.md)

```

## 🔍 ドキュメント検索のヒント

### よくある質問とドキュメント

| 質問 | 参照ドキュメント |
|------|------------------|
| Dockerコンテナが起動しない | [トラブルシューティング](development/troubleshooting.md) |
| テストを実行したい | [テスト戦略](development/testing.md) |
| Discord Botが応答しない | [Discord統合](integrations/discord.md) |
| データベースに接続できない | [データベース設計](architecture/database.md) |
| MinIOファイルをアップロードしたい | [MinIO設定](integrations/minio.md) |
| 環境変数を設定したい | [サービス構成](architecture/services.md) |

## 📧 フィードバック

ドキュメントの改善提案やエラーを見つけた場合：

1. GitHubでIssueを作成
2. PRでドキュメント修正を提案

## ライセンス

このドキュメントは、VECR Garageプロジェクトの一部です。
