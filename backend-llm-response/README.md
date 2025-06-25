# backend-llm-response

LLMを使用してメンバーの応答を生成するサービスです。

- DBに登録されたメンバー情報を取得
- 取得した情報をもとにLLMを使用して応答を生成

を行う機能をここで実装する予定です。

## 接続チェック

`backend-llm-response`コンテナのシェルで以下のコマンドを実行することで
他のサービスとの接続チェックを行えます。

### db-memberサービスとの接続チェック

現在、以下のコマンドでdb-memberサービスへの接続を確認しています。

```bash
make db-member-connection
```

接続成功時には以下のようなメッセージが表示されます:

```bash
✅ Database connection established successfully.
```

## メンバーレスポンスの生成

以下のコマンドでメンバーの応答を生成できます：

```bash
make generate-member-response
```

このコマンドは`src/services/member_service.py`スクリプトを実行し、以下の処理を行います：

1. db-memberサービスへの接続
2. 人間メンバーと仮想メンバーの情報を取得
3. 取得した情報をもとに応答を生成

成功した時、以下のようなメッセージが表示されます:

```bash
✅ Database connection established successfully.

=== メンバーレスポンス ===
人間メンバー: わたしの名前はSyotaです
仮想メンバー: あなたの名前は華扇です
=======================
```

### 必要な環境変数

このスクリプトを実行するには、以下の環境変数が設定されている必要があります：

- `MEMBER_DB_HOST`: PostgreSQLサーバーのホスト名
- `MEMBER_DB_PORT`: PostgreSQLサーバーのポート番号
- `MEMBER_DB_USER`: PostgreSQLのユーザー名
- `MEMBER_DB_PASSWORD`: PostgreSQLのパスワード
- `MEMBER_DB_NAME`: 使用するデータベース名

### エラーが発生した場合

エラーが発生した場合は、以下の点を確認してください：

1. 環境変数が正しく設定されているか
2. PostgreSQLサーバーが起動しているか
3. 指定されたデータベースが存在するか
4. 必要なテーブルとレコードが存在するか

現在のスクリプトはデータベースの接続チェックとメンバー情報の取得を行う処理が実装されており、
将来的にはLLMを使用した応答生成機能を追加する予定です。
