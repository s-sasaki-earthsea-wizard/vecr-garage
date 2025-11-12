# トラブルシューティング

## コンテナ関連

### コンテナが起動しない場合

**症状**: `make docker-up`でコンテナが起動しない

**解決策**:

```bash
# 1. クリーン＆再ビルド
make docker-clean
make docker-build-up

# 2. ログ確認
make docker-logs

# 3. 個別サービスログ確認
docker logs vecr-garage-backend-db-registration
docker logs vecr-garage-backend-llm-response
docker logs vecr-garage-db-member
docker logs vecr-garage-storage
```

### コンテナが頻繁に再起動する

**症状**: `docker ps`で`Restarting`状態が続く

**解決策**:

```bash
# 1. ログでエラー原因を特定
docker logs vecr-garage-<service-name>

# 2. ヘルスチェック確認
docker ps --format "table {{.Names}}\t{{.Status}}"

# 3. サービス再起動
make docker-restart
```

## データベース関連

### データベース接続エラー

**症状**: `connection refused`や`could not connect to server`エラー

**解決策**:

```bash
# 1. ヘルスチェック確認
docker ps --format "table {{.Names}}\t{{.Status}}"
# db-memberが(healthy)であることを確認

# 2. 手動ヘルスチェック
docker exec vecr-garage-db-member pg_isready -U testuser

# 3. PostgreSQLログ確認
docker logs vecr-garage-db-member

# 4. 再起動
make docker-restart
```

### テーブルが存在しない

**症状**: `relation "human_members" does not exist`エラー

**解決策**:

```bash
# 1. テーブル確認
make db-member-psql
\dt

# 2. マイグレーション実行（未実装の場合は手動作成）
# TODO: マイグレーションスクリプト実装

# 3. コンテナ再ビルド
make docker-clean
make docker-build-up
```

### データが登録されない

**症状**: YMLファイルをアップロードしてもDBに反映されない

**解決策**:

```bash
# 1. backend-db-registrationログ確認
docker logs vecr-garage-backend-db-registration

# 2. Webhook設定確認
docker exec vecr-garage-storage mc event list myminio/vecr-garage-storage

# 3. ETag重複チェック確認
# .envファイルで WEBHOOK_ETAG_CHECK_ENABLED=false を設定

# 4. 再起動
make docker-restart
```

## MinIO関連

### Webhookが動作しない

**症状**: ファイルアップロードしてもWebhook通知が来ない

**解決策**:

```bash
# 1. MinIOのWebhook設定確認
docker exec vecr-garage-storage mc admin config get myminio notify_webhook

# 2. イベント通知設定確認
docker exec vecr-garage-storage mc event list myminio/vecr-garage-storage

# 3. backend-db-registrationログ確認
docker logs vecr-garage-backend-db-registration

# 4. 手動でWebhook設定を再実行
docker exec vecr-garage-storage /scripts/webhook-configurator.sh

# 5. 再起動
make docker-restart
```

### MinIO Consoleにアクセスできない

**症状**: `http://localhost:9001`にアクセスできない

**解決策**:

```bash
# 1. ポート確認
lsof -i :9001

# 2. コンテナ状態確認
docker ps | grep storage

# 3. MinIOログ確認
docker logs vecr-garage-storage

# 4. ポート競合の場合は別プロセスを停止
kill -9 <PID>
```

## Discord Bot関連

### Botが起動しない

**症状**: Discord Botがオンラインにならない

**解決策**:

```bash
# 1. Bot起動ログ確認
make discord-bot-logs

# 2. 設定ファイル確認
cat config/discord_tokens.json

# 3. 環境変数確認
docker exec vecr-garage-backend-llm-response env | grep DISCORD

# 4. Discord Developer Portal設定確認
# - MESSAGE CONTENT INTENT が有効か
# - Bot Tokenが正しいか
# - Botがサーバーに招待されているか

# 5. 再起動
make docker-restart
```

### Botが応答しない（Mention Mode）

**症状**: @メンションしても応答がない

**解決策**:

```bash
# 1. チャンネルID確認
# config/discord_tokens.jsonの"mention_mode"にチャンネルIDが含まれているか

# 2. ログ確認
make discord-bot-logs

# 3. Bot権限確認
# - View Channels
# - Send Messages
# - Read Message History

# 4. Claude API設定確認
make claude-test
```

### Botが応答しない（AutoThread Mode）

**症状**: 新着投稿に自動応答しない

**解決策**:

```bash
# 1. チャンネルID確認
# config/discord_tokens.jsonの"auto_thread_mode"にチャンネルIDが含まれているか

# 2. ログ確認（無限ループ防止が働いていないか）
make discord-bot-logs

# 3. Bot自身のメッセージを無視しているか確認
# ログで"Bot自身のメッセージは無視"と表示されているか
```

### Times Modeが投稿しない

**症状**: 1日1回の自動投稿が実行されない

**解決策**:

```bash
# 1. テストモードで動作確認
# .envで TIMES_TEST_MODE=true に設定
sed -i 's/TIMES_TEST_MODE=false/TIMES_TEST_MODE=true/' .env
make docker-restart

# 2. ログ確認（60秒ごとに投稿されることを確認）
make discord-bot-logs

# 3. 本番モードに戻す
sed -i 's/TIMES_TEST_MODE=true/TIMES_TEST_MODE=false/' .env
make docker-restart

# 4. スケジューラー起動確認
# ログに"TimesScheduler起動完了"が表示されているか確認
```

## Claude API関連

### API接続エラー

**症状**: `AuthenticationError`や`APIConnectionError`

**解決策**:

```bash
# 1. APIキー確認
cat .env | grep ANTHROPIC_API_KEY

# 2. 環境変数確認
docker exec vecr-garage-backend-llm-response env | grep ANTHROPIC

# 3. 接続テスト
make claude-test

# 4. APIキーが有効か確認
# https://console.anthropic.com/ でAPIキーをチェック

# 5. 再起動
make docker-restart
```

### レート制限エラー

**症状**: `RateLimitError`

**解決策**:

```bash
# 1. リクエスト頻度を下げる
# Times Modeのテストモードを無効化
TIMES_TEST_MODE=false

# 2. Anthropic Consoleで利用状況確認
# https://console.anthropic.com/

# 3. 必要に応じてプラン変更
```

## Discord Webhook関連

### Webhook通知が届かない

**症状**: `make discord-test-all`でHTTP 204だがメッセージが届かない

**解決策**:

```bash
# 1. Webhook URL確認
cat config/discord_webhooks.json

# 2. Discord側でWebhook削除されていないか確認
# Discordサーバー設定 > 連携サービス > Webhook で確認

# 3. 動作確認
make discord-verify

# 4. ログ確認
docker logs vecr-garage-backend-llm-response
```

## ポート競合

### ポート3000が使用中

**症状**: `bind: address already in use`エラー

**解決策**:

```bash
# 1. 使用中のポート確認
lsof -i :3000

# 2. プロセス停止
kill -9 <PID>

# 3. または別プロセスを停止

# 4. コンテナ起動
make docker-up
```

### ポート5432が使用中（PostgreSQL）

**症状**: ローカルのPostgreSQLと競合

**解決策**:

```bash
# 1. ローカルのPostgreSQL停止
sudo systemctl stop postgresql

# 2. または docker-compose.ymlでポート変更
# ports:
#   - "15432:5432"  # 外部ポートを変更
```

## 環境変数関連

### .envファイルが読み込まれない

**症状**: 環境変数がコンテナ内で設定されていない

**解決策**:

```bash
# 1. .envファイル存在確認
ls -la .env

# 2. .env.exampleからコピー
cp .env.example .env

# 3. コンテナ再起動
make docker-restart

# 4. 環境変数確認
docker exec vecr-garage-backend-db-registration env
```

### direnv/.envrcが読み込まれない

**症状**: Discord Webhook環境変数が設定されていない

**解決策**:

```bash
# 1. direnv許可
direnv allow

# 2. .envrc生成
# config/discord_webhooks.jsonが存在することを確認

# 3. 手動で環境変数エクスポート
source .envrc

# 4. コンテナ再起動
make docker-build-up
```

## パフォーマンス関連

### コンテナが遅い

**症状**: コマンド実行やレスポンスが遅い

**解決策**:

```bash
# 1. リソース使用状況確認
docker stats

# 2. 不要なコンテナ削除
docker container prune

# 3. 不要なイメージ削除
docker image prune

# 4. Docker Desktopのリソース設定確認
# CPU、メモリの割り当てを増やす
```

## ログ関連

### ログが大量に出力される

**症状**: ディスク容量が圧迫される

**解決策**:

```bash
# 1. ログサイズ確認
docker system df

# 2. ログクリア
docker logs vecr-garage-<service-name> --tail 0

# 3. ログローテーション設定
# docker-compose.ymlに追加
# logging:
#   driver: "json-file"
#   options:
#     max-size: "10m"
#     max-file: "3"
```

## その他

### makeコマンドが動作しない

**症状**: `make: command not found`

**解決策**:

```bash
# Ubuntu/Debian
sudo apt-get install make

# macOS
xcode-select --install
```

### Git関連エラー

**症状**: コミットやプッシュができない

**解決策**:

```bash
# 1. Git設定確認
git config --list

# 2. ユーザー情報設定
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 3. リモートURL確認
git remote -v

# 4. SSH鍵設定（GitHub）
ssh-keygen -t ed25519 -C "your.email@example.com"
cat ~/.ssh/id_ed25519.pub
# GitHubに公開鍵を追加
```

## ヘルプ情報

```bash
# Makefile全体のヘルプ
make help

# Discord関連
make discord-help

# Discord Bot関連
make discord-bot-help

# Claude API関連
make claude-help
```

## 関連ドキュメント

- [よく使うコマンド](commands.md)
- [サービス構成](../architecture/services.md)
- [テスト戦略](testing.md)
