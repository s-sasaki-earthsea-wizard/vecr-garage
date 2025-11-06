# backend-db-registration

DB操作を行うサービスです。

- ストレージへのファイルアップロード、または更新を検知
- アップロードされたファイルをもとにDBへの登録

を行う機能をここで実装する予定です。

## ログ設定

このサービスでは、統一されたログ設定を使用しています。ログレベルやログファイルの設定は環境変数で制御できます。

### 環境変数

- `LOG_LEVEL`: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）- デフォルト: INFO
- `LOG_FILE`: ログファイルのパス（指定しない場合はコンソール出力のみ）

### 使用例

```bash
# デバッグレベルのログを出力
export LOG_LEVEL=DEBUG

# ログファイルに出力
export LOG_FILE=logs/vecr-office.log

# サービスを起動
make start-api
```

### ログ設定の統一

各モジュールでは `utils.logging_config.setup_logging()` 関数を使用してログ設定を行います。これにより、サービス全体で一貫したログレベルとフォーマットが適用されます。

## 接続チェック

`backend-db-registration`コンテナのシェルで以下のコマンドを実行することで
他のサービスとの接続チェックを行えます。

### db-memberサービスとの接続チェック

現在、以下のコマンドでdb-memberサービスへの接続を確認しています。

```bash
make db-member-connection
```

接続成功時には以下のようなメッセージが表示されます:

```bash
You are connected to database "member_db" as user "testuser" on host "db-member" (address "172.18.0.3") at port "5432".
```

### storageサービスとの接続チェック

以下のコマンドで`storage`サービスとの接続チェックを行えます。
この例ではバケットの中のサンプルデータの読み込みを行っています。

```bash
make show_sample_data_in_bucket
```

このコマンドは`src/storage/storage_client.py`スクリプトを実行し、以下の処理を行います：

1. MinIOストレージへの接続チェック
2. 指定されたバケットの存在確認
3. サンプルデータ（`data/human_members/Syota.yml`と`data/virtual_members/Kasen.yml`）の読み込み

成功した時、以下のようなメッセージが表示されます:

```bash
✅ Successfully connected to storage!
Syota data: {'name': 'Syota', 'bio': "I'm a human member."}
Kasen data: {'name': '華扇', 'custom_prompt': "I'm a virtual member.", 'llm_model': 'claude-3-5-sonnet-20240620'}
```

#### 必要な環境変数

このスクリプトを実行するには、以下の環境変数が設定されている必要があります：

- `STORAGE_HOST`: MinIOサーバーのホスト名
- `STORAGE_PORT`: MinIOサーバーのポート番号
- `MINIO_ROOT_USER`: MinIOのアクセスキー
- `MINIO_ROOT_PASSWORD`: MinIOのシークレットキー
- `MINIO_BUCKET_NAME`: 使用するバケット名

#### レコードの登録方法

storage サービスへ、DBにインサートしたい情報のファイルを配置してください。

詳細は`storage`サービスの[README](./storage/README.md)を参照してください。

##### ファイル監視サービス（Webhookベース）

ファイル監視サービスを使用すると、ストレージ内のYAMLファイルをリアルタイムで検知します。

**使用方法:**

```bash
# 本番環境: Dockerコンテナが自動的にFastAPIサーバーを起動
docker-compose -p vecr-garage up -d backend-db-registration

# 開発環境: 手動でFastAPIサーバーを起動
make start-api

# Webhook設定を行う
python src/scripts/setup_webhook.py setup
```

**Webhookエンドポイント:**

- `POST /webhook/file-change` - ファイル変更通知を受け取る
- `GET /webhook/status` - Webhookサービスの状態を確認
- `POST /webhook/test` - Webhook機能のテスト

**Webhook設定スクリプト:**

```bash
# Webhook設定を作成
python src/scripts/setup_webhook.py setup

# Webhook接続をテスト
python src/scripts/setup_webhook.py test

# Webhook設定一覧を表示
python src/scripts/setup_webhook.py list

# Webhook設定を削除
python src/scripts/setup_webhook.py remove <webhook_id>
```

**監視対象:**

- `data/human_members/` ディレクトリ内のYAMLファイル
- `data/virtual_members/` ディレクトリ内のYAMLファイル

**利点:**

- リアルタイムでのファイル変更検知
- ポーリング不要でリソース効率が良い
- スケーラブルな設計
- エラーハンドリングとログ機能
- 重複イベントの検出と防止
- **自動起動**: Dockerコンテナ起動時にAPIサーバーが自動的に開始

**テスト:**

```bash
# Webhook機能のテスト
make test-webhook

# 個別テスト
python src/scripts/test_webhook.py --test health
python src/scripts/test_webhook.py --test human
```

##### 登録モードの選択

**バッチ処理モード（推奨）:**

- 全てのファイルを一つのトランザクションで処理
- 一つでもバリデーションエラーがあれば、全ての変更がロールバック
- データの整合性を保証

```bash
# 全てのメンバーを登録（バッチ処理）
make register-members

# 人間メンバーのみ登録（バッチ処理）
make register-human-members

# 仮想メンバーのみ登録（バッチ処理）
make register-virtual-members
```

**単独処理モード:**

- 各ファイルを個別に処理
- エラーがあっても他のファイルの処理を続行
- 部分的な成功を許容

```bash
# 全てのメンバーを登録（単独処理）
make register-members-single
```

##### 処理例

**バッチ処理モード（成功例）:**

```bash
=== Batch Registration Mode ===
Processing all files in a single transaction.
If any file has validation errors, all changes will be rolled back.

=== Processing Human Members (Batch Mode) ===
Found 2 human member files:
  - data/human_members/Syota.yml
  - data/human_members/Rin.yml
✅ Successfully processed 2 human members.

=== Processing Virtual Members (Batch Mode) ===
Found 2 virtual member files:
  - data/virtual_members/Kasen.yml
  - data/virtual_members/Darcy.yml
✅ Successfully processed 2 virtual members.

=== Final Summary ===
🎉 All processing completed successfully!
   Human members: 2/2 processed
   Virtual members: 2/2 processed
   Total: 4/4 members processed
```

**バッチ処理モード（エラー例）:**

```bash
=== Processing Human Members (Batch Mode) ===
Found 2 human member files:
  - data/human_members/Syota.yml
  - data/human_members/Rin.yml
❌ Validation error for data/human_members/Rin.yml: Required fields missing in human member YAML: name
❌ Batch registration failed: Required fields missing in human member YAML: name
All changes have been rolled back.
Continuing with virtual member processing...

=== Processing Virtual Members (Batch Mode) ===
Found 2 virtual member files:
  - data/virtual_members/Kasen.yml
  - data/virtual_members/Darcy.yml
✅ Successfully processed 2 virtual members.

=== Final Summary ===
⚠️  Partial processing completed:
   ❌ Human members: Failed
   ✅ Virtual members: 2/2 processed
   Total: 2/4 members processed
```

**単独処理モード（部分成功例）:**

```bash
=== Single Registration Mode ===
Processing files individually. Each file is processed separately.
Valid files will be registered even if some files have errors.

=== Processing Human Members (Single Mode) ===
Found 2 human member files:
  - data/human_members/Syota.yml
  - data/human_members/Rin.yml

Processing: data/human_members/Syota.yml
✅ Successfully processed: data/human_members/Syota.yml

Processing: data/human_members/Rin.yml
❌ Failed to process data/human_members/Rin.yml: Required fields missing in human member YAML: name

--- Human Members Summary ---
✅ Successfully processed: 1
❌ Failed to process: 1
```

成功した時、以下のようなメッセージが表示がされます：

```bash
INFO:operations.member_registration:Human member Syota registered successfully.
INFO:operations.member_registration:Virtual member 華扇 registered successfully.
INFO:__main__:All member registration completed
```

db-memberサービスで以下のSQL文を入力：

```sql
--人間メンバーの場合
SELECT * FROM human_members;

--仮想メンバーの場合
SELECT * FROM virtual_members;
```bash

登録完了時、以下のような結果が返ってくる事を期待しています：

```text
 member_id |             member_uuid              | member_name |          created_at           |          updated_at
-----------+--------------------------------------+-------------+-------------------------------+-------------------------------
         1 | 13e60657-717e-40da-8900-c6ddbec796b0 | Syota       | 2025-04-29 15:47:41.417381+00 | 2025-04-29 15:47:41.417409+00
(1 row)

 member_id |             member_uuid              | member_name |          created_at          |          updated_at           
-----------+--------------------------------------+-------------+------------------------------+-------------------------------
         1 | 2313a16f-29d4-4934-a821-b0981cbf224b | 華扇        | 2025-04-29 15:47:41.43336+00 | 2025-04-29 15:47:41.433365+00
(1 row)
```

#### エラーが発生した場合

エラーが発生した場合は、以下の点を確認してください：

1. 環境変数が正しく設定されているか
2. MinIOサーバーが起動しているか
3. 指定されたバケットが存在するか
4. 読み込もうとしているファイルが存在するか

#### ロールバック機能とバリデーション機能

データベースへのレコード登録時に、以下の機能が追加されました：

**バリデーション機能:**

- YAMLファイルの必須フィールドチェック
- YAML形式の構文チェック

**ロールバック機能:**

- データベース操作失敗時の自動ロールバック
- 詳細なエラーメッセージの表示
- エラーの原因と対処法の提示

**テスト機能:**

```bash
make test-rollback-functionality
```

このコマンドで、バリデーション機能とロールバック機能をテストできます。

**エラー例:**

```text
❌ Validation error for human member registration from data/human_members/invalid_human.yml: Required fields missing in human member YAML: name
   Missing fields: name

❌ Database error for virtual member registration from data/virtual_members/invalid_virtual.yml: Failed to create virtual member 'TestMember': (psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "virtual_members_member_name_key"
   Original error: (psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "virtual_members_member_name_key"
```

現在のスクリプトはストレージの接続チェックとサンプルデータの読み込みを行う処理が同時に実行されており、
将来的には両者の分離を行います (ストレージのオブジェクトを読み込み、DBへのインサートを行う処理を実装する時に)

#### テストコードの実行方法

ルートディレクトリで実行する場合：

```bash
make backend-db-registration-test
```

コンテナ内で実行する場合：

```bash
make test
```bash

どちらも以下のような結果が返ってくることを期待しています：

```text
============================================================================= test session starts ==============================================================================
platform linux -- Python 3.12.11, pytest-8.0.2, pluggy-1.6.0 -- /usr/local/bin/python3.12
cachedir: .pytest_cache
rootdir: /app
collected 16 items                                                                                                                                                             

tests/test_database.py::test_create_human_member PASSED                                                                                                                  [  6%]
tests/test_database.py::test_create_virtual_member PASSED                                                                                                                [ 12%]
tests/test_database.py::test_get_nonexistent_human_member PASSED                                                                                                         [ 18%]
tests/test_database.py::test_get_nonexistent_virtual_member PASSED                                                                                                       [ 25%]
tests/test_member_registration.py::test_register_human_member_from_yaml PASSED                                                                                           [ 31%]
tests/test_member_registration.py::test_register_virtual_member_from_yaml PASSED                                                                                         [ 37%]
tests/test_member_registration.py::test_register_human_member_invalid_yaml PASSED                                                                                        [ 43%]
tests/test_member_registration.py::test_register_virtual_member_invalid_yaml PASSED                                                                                      [ 50%]
tests/test_rollback_functionality.py::test_human_member_validation PASSED                                                                                                [ 56%]
tests/test_rollback_functionality.py::test_virtual_member_validation PASSED                                                                                              [ 62%]
tests/test_rollback_functionality.py::test_successful_registration PASSED                                                                                                [ 68%]
tests/test_rollback_functionality.py::test_validation_directly PASSED                                                                                                    [ 75%]
tests/test_storage_client.py::test_storage_connection_check PASSED                                                                                                       [ 81%]
tests/test_storage_client.py::test_read_human_member_yaml PASSED                                                                                                         [ 87%]
tests/test_storage_client.py::test_read_virtual_member_yaml PASSED                                                                                                       [ 93%]
tests/test_storage_client.py::test_read_nonexistent_yaml PASSED                                                                                                          [100%]

============================================================================== 16 passed in 0.89s ==============================================================================
```
