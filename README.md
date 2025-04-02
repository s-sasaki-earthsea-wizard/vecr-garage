# VECR Office

## 概要

人間とAIアシスタントエンジニアが協働する仮想スタートアップオフィス、
VECRガレージのオフィス環境をDockerコンテナで構築するプロジェクトです。

現在、バックエンド、データベース、ストレージの3つのサービスで構成されています。
(ユーザー管理サービス、チャットログサービスは将来的に開発予定のスコープです)

## 開発環境

- OS: Ubuntu 24.04.1 LTS
- Docker: 27.3.1
- Docker Compose: v2.29.7

## インストール方法

1. リポジトリをクローン
```bash
git clone https://github.com/s-sasaki-earthsea-wizard/vecr-office.git
cd vecr-office
```

2. 環境変数ファイルの作成
```bash
cp .env.example .env
```

- 環境変数は実際のものに書き換えてください

3. コンテナのビルドと起動

```bash
make docker-build-up
```

## 使い方

### コンテナの操作

- コンテナの起動: `make docker-up`
- コンテナの停止: `make docker-down`
- コンテナの再起動: `make docker-restart`
- ログの確認: `make docker-logs`
- コンテナの状態確認: `make docker-ps`

### 各サービスへのアクセス

- バックエンドサービス(DB操作): `make backend-db-operation-shell`
- バックエンドサービス(DB操作): `make backend-llm-response-shell`
- データベースサービス: `make member-db-shell`
- ストレージサービス: `make storage-shell`

## ネットワーク構成

- プロジェクト名: `vecr-office`
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
      - ブラウザ操作でバックエンドサービスを介してDB操作やファイルアップロードを行います (予定)。

各サービスはDocker Composeのネットワーク機能により、プロジェクト名をプレフィックスとしたネットワーク内で通信可能です。

## その他

- 開発環境のクリーンアップ: `make docker-clean`
- ヘルプの表示: `make help`

_____

# VECR Office

## Overview

This project sets up a virtual startup office environment, VECR Garage, where humans and AI assistant engineers collaborate, using Docker containers.

It currently consists of three services: backend, database, and storage. (A user management service is planned for future development.)

## Development Environment

- OS: Ubuntu 24.04.1 LTS
- Docker: 27.3.1
- Docker Compose: v2.29.7

## Installation Instructions

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
