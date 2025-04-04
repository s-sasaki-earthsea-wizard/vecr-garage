# backend-db-registration

DB操作を行うサービスです。

- ストレージへのファイルアップロード、または更新を検知
- アップロードされたファイルをもとにDBへの登録

を行う機能をここで実装する予定です。

現在、以下のコマンドでメンバーDBへの接続を確認しています。

```bash
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\conninfo"
```
