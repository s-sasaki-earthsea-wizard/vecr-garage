# 機密情報管理ガイドライン

## 📋 概要

VECR Garageプロジェクトでは、APIキー、トークン、Webhook URL等の機密情報を適切に管理するため、以下のガイドラインを定めています。

---

## 🚫 絶対にコミットしてはいけないファイル

以下のファイルは**機密情報を含むため、Gitにコミットしてはいけません**：

| ファイル | 内容 | 対策 |
|---------|------|------|
| `.env` | 環境変数（実際の値） | `.gitignore`に記載済み |
| `.envrc` | direnv設定（実際の値） | `.gitignore`に記載済み |
| `config/discord_webhooks.json` | Discord Webhook URL | `.gitignore`に記載済み |
| `config/discord_tokens.json` | Discord Bot トークン | `.gitignore`に記載済み |
| 任意の`*_secret*`, `*_token*`, `*_credentials*`ファイル | 認証情報 | 命名規則で判別 |

---

## ✅ 保護されている機密情報の種類

### 1. API キー

- **Anthropic API Key**: Claude APIアクセス用
  - 環境変数: `ANTHROPIC_API_KEY`
  - 例: `sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
  - 保存場所: `.env`（Git管理外）

### 2. Discord 関連

- **Discord Webhook URL**
  - 形式: `https://discord.com/api/webhooks/{ID}/{TOKEN}`
  - 保存場所: `config/discord_webhooks.json`（Git管理外）
  - サンプル: `config/discord_webhooks.example.json`（Git管理）

- **Discord Bot Token**
  - 形式: `MTxxxxxxxxxxxxxxxxxx.xxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxx`
  - 保存場所: `config/discord_tokens.json`（Git管理外）
  - サンプル: `config/discord_tokens.example.json`（Git管理）

- **Discord Channel ID**
  - 形式: 18-19桁の数値
  - 保存場所: `config/discord_tokens.json`（Git管理外）

### 3. データベース認証情報

- **PostgreSQL パスワード**: `MEMBER_DB_PASSWORD`
- **MinIO 認証情報**: `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`
- **セッション秘密鍵**: `SECRET_KEY`

すべて `.env` ファイルに保存され、Git管理外です。

---

## 📝 コミット前チェックリスト

コミット前に必ず以下を確認してください：

- [ ] **Pre-commit Hooksがインストール済み**

  ```bash
  pip install pre-commit
  pre-commit install
  ```

- [ ] **`git status`で機密ファイルが含まれていないことを確認**

  ```bash
  git status
  # .env, .envrc, config/discord_*.json が表示されないこと
  ```

- [ ] **`git diff --cached`で機密情報がないことを目視確認**

  ```bash
  git diff --cached
  # APIキー、トークン、Webhook URLが含まれていないこと
  ```

- [ ] **exampleファイルと実際のファイルが同期されている**
  - `.env.example` ⇔ `.env`
  - `config/discord_webhooks.example.json` ⇔ `config/discord_webhooks.json`
  - `config/discord_tokens.example.json` ⇔ `config/discord_tokens.json`
  - `.envrc.example` ⇔ `.envrc`

---

## 🔧 開発環境セットアップ手順

### 1. リポジトリクローン後の初回セットアップ

```bash
# 1. リポジトリをクローン
git clone https://github.com/s-sasaki-earthsea-wizard/vecr-garage.git
cd vecr-garage

# 2. 環境変数ファイルを作成
cp .env.example .env

# 3. Discord設定ファイルを作成
cp config/discord_webhooks.example.json config/discord_webhooks.json
cp config/discord_tokens.example.json config/discord_tokens.json

# 4. direnv設定を作成（オプション）
cp .envrc.example .envrc

# 5. 各ファイルに実際の値を設定
# .env を編集: ANTHROPIC_API_KEY, データベースパスワード等
# config/discord_webhooks.json を編集: 実際のWebhook URL
# config/discord_tokens.json を編集: 実際のBot Token
```

### 2. Pre-commit Hooksのセットアップ（必須）

```bash
# Pre-commitのインストール
pip install pre-commit

# Hooksのインストール
pre-commit install

# 初回スキャン（全ファイル）
pre-commit run --all-files
```

### 3. 動作確認

```bash
# テスト: 機密情報を含むファイルをコミット試行
echo "ANTHROPIC_API_KEY=sk-ant-real-key-12345" > test_secret.txt
git add test_secret.txt
git commit -m "test"

# 期待される結果: Secrets検知で自動ブロック
# ❌ Anthropic APIキーが検出されました！
```

---

## 🚨 万が一コミットしてしまった場合

### 即座に実施すること

1. **プッシュを停止**

   ```bash
   # まだpushしていない場合は絶対にpushしない
   ```

2. **セキュリティ担当者に連絡**
   - GitHub Issues または Slack で即座に報告

3. **漏洩した認証情報を無効化・再生成**
   - Discord Webhook: サーバー設定から削除・再作成
   - Discord Bot Token: Discord Developer Portal で再生成
   - Anthropic API Key: Anthropic Console で無効化・再生成

4. **直前のコミットから削除（pushしていない場合）**

   ```bash
   # 最新のコミットを取り消し
   git reset HEAD~1

   # 機密ファイルを除外して再コミット
   git add .
   git reset -- .env config/discord_*.json .envrc
   git commit -m "修正: 機密情報を除外"
   ```

### すでにpushしてしまった場合

**⚠️ 重要**: この操作はリポジトリ履歴を書き換えるため、チーム全体への周知が必要です。

```bash
# 1. 機密情報を無効化・再生成（必須）

# 2. Git履歴から完全削除（git filter-repo使用）
pip install git-filter-repo

# 機密ファイルを履歴から削除
git-filter-repo --path .env --invert-paths --force
git-filter-repo --path config/discord_webhooks.json --invert-paths --force
git-filter-repo --path config/discord_tokens.json --invert-paths --force
git-filter-repo --path .envrc --invert-paths --force

# 3. リモートを再設定
git remote add origin https://github.com/s-sasaki-earthsea-wizard/vecr-garage.git

# 4. 強制プッシュ（チームに事前通知必須！）
git push origin --force --all
```

### チームメンバーへの周知内容

```
【重要】Gitリポジトリ履歴の書き換えを実施しました

機密情報漏洩のため、Gitリポジトリ履歴を書き換えました。
以下の手順で最新の状態に同期してください：

1. 現在の作業をコミット・退避
   git stash

2. ローカルブランチを削除
   git fetch origin
   git reset --hard origin/main

3. 退避した作業を復元
   git stash pop

ご協力をお願いします。
```

---

## 🛡️ CI/CDによる自動チェック

### GitHub Actionsによる保護

このプロジェクトでは、GitHub Actionsで以下のチェックを実施しています：

1. **Secrets スキャン** (`.github/workflows/security-scan.yml`)
   - `detect-secrets` による機密情報検出
   - Discord Webhook URL の検出
   - Anthropic API Key の検出

2. **機密ファイルチェック** (`.github/workflows/ci.yml`)
   - `.env`, `.envrc`, `config/discord_*.json` のコミット検出

3. **Exampleファイル存在確認**
   - `.env.example`, `config/*.example.json` の存在確認

**すべてのチェックがグリーンになるまでマージできません。**

---

## 📚 参考資料

- [Pre-commit公式ドキュメント](https://pre-commit.com/)
- [detect-secrets公式ドキュメント](https://github.com/Yelp/detect-secrets)
- [git-filter-repo公式ドキュメント](https://github.com/newren/git-filter-repo)
- [Discord Webhook セキュリティ](https://discord.com/developers/docs/resources/webhook)
- [Anthropic API セキュリティ](https://docs.anthropic.com/claude/reference/api-security)

---

## ✅ まとめ

### 基本原則

1. **機密情報は絶対にGitにコミットしない**
2. **exampleファイルはダミー値のみ**
3. **Pre-commit Hooksを必ず使用**
4. **万が一の場合は即座に無効化・報告**

### 質問・相談

機密情報管理について不明な点があれば、セキュリティ担当者またはプロジェクトリーダーに相談してください。
