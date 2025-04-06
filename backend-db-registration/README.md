# backend-db-registration

DB操作を行うサービスです。

- ストレージへのファイルアップロード、または更新を検知
- アップロードされたファイルをもとにDBへの登録

を行う機能をここで実装する予定です。

## 接続チェック

`backend-db-registration`コンテナのシェルで以下のコマンドを実行することで
他のサービスとの接続チェックを行えます。

### db-memberサービスとの接続チェック

現在、以下のコマンドでdb-memberサービスへの接続を確認しています。

```bash
PGPASSWORD=$MEMBER_DB_PASSWORD psql -h $MEMBER_DB_HOST -p $MEMBER_DB_PORT -U $MEMBER_DB_USER -d $MEMBER_DB_NAME -c "\conninfo"
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

#### エラーが発生した場合

エラーが発生した場合は、以下の点を確認してください：

1. 環境変数が正しく設定されているか
2. MinIOサーバーが起動しているか
3. 指定されたバケットが存在するか
4. 読み込もうとしているファイルが存在するか

現在のスクリプトはストレージの接続チェックとサンプルデータの読み込みを行う処理が同時に実行されており、
将来的には両者の分離を行います (ストレージのオブジェクトを読み込み、DBへのインサートを行う処理を実装する時に)