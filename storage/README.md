# VECR-garage-storage

## 概要

ストレージサービスのREADMEです。
アバターや背景の画像、DBにインサートするためのJSON, YAMLなどを置く予定です。

## バケットへのアクセス

### ブラウザを使う方法

- ブラウザで以下のアドレスにアクセス
  - <http://localhost:9001/>

### シェルからのアクセス

以下のコマンドでコンテナの中に入り:

```bash
make storage-shell
```

コンテナ内で以下を実行

```bash
mc alias set myminio http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}
mc ls myminio
```
