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

以下のコマンドを実行：

```bash
make register-members

##人間メンバーのみの場合
make register-human-members

##仮想メンバーのみの場合
make register-virtual-members
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
```

登録完了時、以下のような結果が返ってくる事を期待しています：

```
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

現在のスクリプトはストレージの接続チェックとサンプルデータの読み込みを行う処理が同時に実行されており、
将来的には両者の分離を行います (ストレージのオブジェクトを読み込み、DBへのインサートを行う処理を実装する時に)