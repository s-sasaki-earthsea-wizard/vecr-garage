# VECR Garage

## 概要

人間とAIアシスタントエンジニアが協働する仮想スタートアップオフィス、
VECRガレージのオフィス環境をDockerコンテナで構築するプロジェクトです。

現在、バックエンド、データベース、ストレージの3つのサービスで構成されています。
(ユーザー管理サービス、チャットログサービスは将来的に開発予定のスコープです)

## 開発環境

- OS: Ubuntu 24.04.1 LTS
- Docker: 27.3.1
- Docker Compose: v2.29.7
- AWS CLI: 2.27.61

## インストール方法

### AWS CLI のインストール

AWS CLI は MinIO ストレージとの操作に必要です。以下の手順でインストールしてください：

#### Ubuntu/Debian の場合

```bash
# AWS CLI v2 のダウンロード
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# アーカイブの解凍
unzip awscliv2.zip

# インストール
sudo ./aws/install

# インストール確認
aws --version

# 不要ファイルの削除
rm -rf aws awscliv2.zip
```

### プロジェクトのセットアップ

1. リポジトリをクローン
```bash
git clone https://github.com/s-sasaki-earthsea-wizard/vecr-garage.git
cd vecr-garage
```

2. 環境変数ファイルの作成
```bash
cp .env.example .env
```

- 環境変数は実際のものに書き換えてください

3. Discord Webhook設定（オプション）
```bash
# Webhook設定ファイルを作成
cp config/discord_webhooks.example.json config/discord_webhooks.json

# Webhook URLを実際のものに書き換える
# config/discord_webhooks.json を編集

# .envrcファイルをコピー（自動読み込み用）
cp .envrc.example .envrc
```

4. コンテナのビルドと起動

```bash
make docker-build-up
```

**Note**: `.envrc`が存在する場合、`make docker-up`/`docker-build-up`実行時に自動的にDiscord Webhook設定が読み込まれます。

## 使い方

### コンテナの操作

- コンテナの起動: `make docker-up`
- コンテナの停止: `make docker-down`
- コンテナの再起動: `make docker-restart`
- ログの確認: `make docker-logs`
- コンテナの状態確認: `make docker-ps`

### 各サービスへのアクセス

#### `backend-db-registration` サービス

`storage`サービスのバケットに配置されているファイルを読み込み、
メンバーのデータベースである`db-member`へのインサートを行うサービスです。

以下のコマンドでコンテナのシェルに入ることができます:

```bash
make backend-db-registration-shell
```

詳細は`backend-db-registration`サービスの[README](./backend-db-registration/README.md)を参照してください。

#### storage サービス

チームメンバーのプロフィールやカスタムプロンプトを配置するサービスです。
MinIOによって提供されており、以下の方法でアクセスできます:

- `http://localhost:9001`にブラウザでアクセス
- または`make storage-shell`でターミナルからアクセス

##### AWS CLI を使用したファイル操作

AWS CLIを使用してMinIOストレージにファイルをコピーできます:

```bash
# AWS CLIプロファイルの設定（初回のみ）
make s3-setup-profile

# サンプルファイルのコピー
make s3-cp-sample

# 個別ファイルのコピー
make s3-cp LOCAL_FILE=./path/to/file.yml S3_KEY=data/human_members/file.yml

# ストレージ内のファイル一覧表示
make s3-ls
```

##### テストケース構造

**新しいディレクトリ構造**: 

- `data/samples/`: 正常系テストファイル（実際の登録用データ）
  - `human_members/`: 人間メンバー（rin.yml, syota.yml）
  - `virtual_members/`: 仮想メンバー（darcy.yml, kasen.yml）

- `data/test_cases/`: 異常系テストファイル（バリデーション検証用）
  - `human_members/`: バリデーションエラーテスト
    - `invalid_missing_name.yml`: nameフィールド欠損
    - `invalid_empty_file.yml`: 空ファイル
  - `virtual_members/`: バリデーションエラーテスト
    - `invalid_missing_name.yml`: nameフィールド欠損  
    - `invalid_missing_model.yml`: llm_modelフィールド欠損

##### ユニットテスト実行

```bash
# backend-db-registrationサービスのテスト実行
$ make backend-db-registration-test
Running tests for backend-db-registration service...
============================= test session starts ==============================
25 passed in 2.94s
Tests completed!
```

**テストケース概要**:
- 正常系: 4つのサンプルファイルからの正常な登録テスト
- 異常系: 5つの異常系ファイルでのバリデーションエラー検証テスト
- 合計25テストケース（既存16 + 新規9）が全て成功

##### ストレージ操作結果

```bash
# ファイル一覧の確認
$ make s3-ls
Listing files in MinIO storage bucket...
                           PRE data/
2025-09-11 09:22:35        38 data/samples/human_members/rin.yml
2025-09-11 09:22:35        40 data/samples/human_members/syota.yml
2025-09-11 09:22:35        72 data/samples/virtual_members/darcy.yml
2025-09-11 09:22:35        93 data/samples/virtual_members/kasen.yml
2025-09-11 09:22:35       143 data/test_cases/human_members/invalid_missing_bio.yml
```

詳細は`storage`サービスの[README](./storage/README.md)を参照してください。

#### db-member サービス

人間メンバー、仮装メンバーの両方を含めたチームメンバーのデータベースです。
以下のコマンドでアクセスできます:

```bash
db-member-psql
```

#### member-manager サービス

メンバー管理のWebインターフェースです。認証システム付きで以下の機能を提供：

**アクセス方法:**
```bash
# ブラウザでアクセス（認証が必要）
http://localhost:8000/

# ログインページ（自動リダイレクト）
http://localhost:8000/login
```

**認証情報:**
`.env.example`ファイルの`ADMIN_USERNAME`と`ADMIN_PASSWORD`を参照してください。

デフォルト:
- ユーザー名: `Admin`
- パスワード: `SamplePassword`

**機能:**
- メンバーデータのテーブル表示・編集
- レコードの追加・更新・削除
- 認証システム（ログイン/ログアウト）
- パスワード表示切り替え機能

#### Discord Webhook通知

Discord Webhookを使用してメッセージを送信する機能を提供しています。

**セットアップ:**
```bash
# 1. Webhook設定ファイルを作成
cp config/discord_webhooks.example.json config/discord_webhooks.json

# 2. 実際のWebhook URLを設定
vim config/discord_webhooks.json

# 3. .envrcをコピー（自動読み込み用）
cp .envrc.example .envrc

# 4. コンテナ起動（自動的にWebhookが読み込まれる）
make docker-up
```

**使用可能なコマンド:**
```bash
# Webhook一覧表示
make discord-webhooks-list

# 動作確認（推奨）
make discord-verify

# 個別テスト送信
make discord-test-kasen
make discord-test-karasuno_endo
make discord-test-rusudan

# 全Webhookへ同時送信
make discord-test-all

# カスタムメッセージ送信
make discord-send-message WEBHOOK=kasen_times MESSAGE="Hello from VECR Garage!"

# コマンド一覧表示
make discord-help

# 統合テスト（Discord Webhook含む）
make test-integration
```

**セキュリティ:**
- `config/discord_webhooks.json`は`.gitignore`で保護
- `.envrc`も`.gitignore`で保護
- コンテナにはファイルをマウントせず、環境変数として渡す
- AWS Secrets Managerへの移行準備完了

**統合テスト:**
- `make test-integration`でDiscord Webhookテストも自動実行
- HTTP 204レスポンス確認（送信成功）
- 実際のメッセージ到達は各Discordチャンネルで目視確認推奨

#### Claude API連携

Claude APIを使用してプロンプトを送信し、応答を取得する機能を提供しています。

**セットアップ:**
```bash
# 1. .envファイルにAPIキーを設定
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_API_VERSION=2023-06-01
ANTHROPIC_MAX_TOKENS=4096

# 2. コンテナ起動（自動的にAPIキーが読み込まれる）
make docker-up
```

**使用可能なコマンド:**
```bash
# 接続テスト
make claude-test

# カスタムプロンプト送信
make claude-prompt PROMPT="こんにちは！"

# コマンド一覧表示
make claude-help
```

**実行例:**
```bash
$ make claude-prompt PROMPT="Pythonで素数判定する関数を書いてください"
🤖 Claude APIにプロンプトを送信中...
プロンプト: Pythonで素数判定する関数を書いてください

📝 応答:
[Claude APIからのコード生成結果が表示されます]
```

**セキュリティ:**
- APIキーは`.env`で管理（.gitignore保護）
- コンテナに環境変数として渡される

#### TBD

- バックエンドサービス(LLM応答): `make backend-llm-response-shell`


## ネットワーク構成

- プロジェクト名: `vecr-garage`
- サービス構成:
  - backend
    - データベース操作やプロンプト生成、LLMからの応答の送受信を行います。
  - member-database
    - メンバー情報のデータベース、PostgreSQLを利用
  - storage 
    - ユーザーのアイコン画像やカスタムプロンプトを保存するストレージ、将来的なS3への以降を見越してMinIOを利用
  - chat-log-database 
    - メンバー間のチャットログのデータベース, 暫定的にlocalstack/DynamoDBを使用 (予定)
  - member-manager
      - ブラウザ操作でメンバー管理を行うWebインターフェース。認証システム付き。

各サービスはDocker Composeのネットワーク機能により、プロジェクト名をプレフィックスとしたネットワーク内で通信可能です。

## セキュリティ注意事項

### 本番環境での設定

本番環境で使用する際は、以下の設定を必ず変更してください：

1. **認証情報の変更**
   ```bash
   # .envファイルで以下を変更
   MEMBER_DB_PASSWORD=your-secure-password
   MINIO_ROOT_USER=your-secure-username
   MINIO_ROOT_PASSWORD=your-secure-password
   WEBHOOK_AUTH_TOKEN=your-secure-webhook-token
   ```

2. **Webhook認証の有効化**
   - `WEBHOOK_AUTH_TOKEN`を設定してWebhook認証を有効化
   - 未設定の場合は認証なしで動作（開発環境のみ推奨）

3. **ネットワークセキュリティ**
   - 本番環境では適切なファイアウォール設定
   - 必要に応じてVPNやプライベートネットワークの使用

### 開発環境

- 現在の設定は開発環境用です
- `.env`ファイルはGitにコミットされません
- 実際の認証情報は環境変数で管理されています

## その他

- 開発環境のクリーンアップ: `make docker-clean`
- ヘルプの表示: `make help`

_____

# VECR Office

The English README does not reflect the latest Japanese README.

## Overview

This project sets up a virtual startup office environment, VECR Garage, where humans and AI assistant engineers collaborate, using Docker containers.

It currently consists of three services: backend, database, and storage. (A user management service is planned for future development.)

## Development Environment

- OS: Ubuntu 24.04.1 LTS
- Docker: 27.3.1
- Docker Compose: v2.29.7
- AWS CLI: 2.27.61

## Installation Instructions

### AWS CLI Installation

AWS CLI is required for operations with MinIO storage. Please install it using the following steps:

#### For Ubuntu/Debian

```bash
# Download AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Extract the archive
unzip awscliv2.zip

# Install
sudo ./aws/install

# Verify installation
aws --version

# Clean up
rm -rf aws awscliv2.zip
```

### Project Setup

1. Clone the repository

```bash
git clone https://github.com/s-sasaki-earthsea-wizard/vecr-office.git
cd vecr-office
```

2. Create the environment variable file

```bash
cp .env.example .env
```

- Replace the environment variables with actual values.

3. Build and start the containers

```bash
make docker-build-up
```

## Usage

### Container Operations

- Start the containers: `make docker-up`
- Stop the containers: `make docker-down`
- Restart the containers: `make docker-restart`
- View logs: `make docker-logs`
- Check container status: `make docker-ps`

### Accessing Each Service

- Backend service: `make backend-shell`
- Database service: `make member-db-shell`
- Storage service: `make storage-shell`

### Network Configuration

- Project Name: vecr-office
- Service Configuration:
  - backend
    - Handles database operations, prompt generation, and sending/receiving responses from LLM.
  - member-database
    - Uses PostgreSQL for the member information database.
  - storage
    - Stores user icon images and custom prompts, using MinIO with future migration to S3 in mind.
  - chat-log-database
   - Uses localstack/DynamoDB temporarily for chat logs between members (planned).
  - member-manager
    - Allows DB operations and file uploads via the backend service using a browser (planned).

Each service can communicate within a network prefixed with the project name using Docker Compose's network feature.

## Miscellaneous

- Clean up the development environment: `make docker-clean`
- Display help: `make help`
