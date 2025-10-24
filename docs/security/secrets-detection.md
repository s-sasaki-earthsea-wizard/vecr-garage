# Secrets検知システム

## 概要

VECR Garageプロジェクトでは、2段階の秘密鍵検出システムを採用しています：

1. **detect-secrets**: 高精度な秘密鍵パターン検出
2. **gitleaks**: 900以上のパターンで強力な検出

これにより、API キー、トークン、パスワード等の機密情報の誤コミットを防止します。

## アーキテクチャ

### システム構成図

```text
┌─────────────────────────────────────────┐
│         Developer Workflow              │
├─────────────────────────────────────────┤
│                                         │
│  git add .                              │
│  git commit  ──────┐                    │
│                    │                    │
│                    ▼                    │
│         ┌──────────────────┐            │
│         │ Pre-commit Hooks │            │
│         └──────────────────┘            │
│                    │                    │
│         ┌──────────┴──────────┐         │
│         ▼                     ▼         │
│  ┌─────────────┐      ┌──────────────┐ │
│  │detect-secrets│      │  gitleaks    │ │
│  │(新規検出のみ)│      │ (900+パターン)│ │
│  └─────────────┘      └──────────────┘ │
│         │                     │         │
│         └──────────┬──────────┘         │
│                    ▼                    │
│            ✅ or ❌ 判定                 │
│                                         │
└─────────────────────────────────────────┘

         手動実行（baseline更新時）
┌─────────────────────────────────────────┐
│  make secrets-baseline-update           │
│         ▼                               │
│  ┌─────────────────────┐                │
│  │ detect-secrets scan │                │
│  │   --baseline        │                │
│  │   --update          │                │
│  └─────────────────────┘                │
│         ▼                               │
│  .secrets.baseline 更新                 │
└─────────────────────────────────────────┘
```

### 2段階検出の役割分担

| ツール | 役割 | 実行タイミング | Baseline使用 |
|--------|------|----------------|--------------|
| **detect-secrets** | 既知のfalse-positiveを除外した新規検出 | Pre-commit hook | ❌ 比較のみ |
| **gitleaks** | 包括的な秘密鍵パターン検出 | Pre-commit hook | - |
| **detect-secrets** | Baseline更新・監査 | 手動実行 | ✅ 更新 |

## .secrets.baseline 運用戦略

### バージョニングの判断

#### ✅ バージョニングするメリット

1. **CI/CD環境での一貫性**: 全環境で同じfalse-positive管理
2. **チーム開発の効率化**: 同じ誤検知で何度も警告されない
3. **新規メンバーの即戦力化**: 環境構築時にbaselineが自動取得

#### ⚠️ リスクと対策

| リスク | 対策 |
|--------|------|
| 本物の秘密鍵を誤登録 | 更新時の必須確認フロー |
| False-negativeの発生 | 四半期ごとの定期監査 |
| マージコンフリクト | 自動マージツール提供 |

### Pre-commit Hookでの運用方針

**重要な設計判断**: Pre-commit hookでは`.secrets.baseline`を**更新しない**

#### 理由

1. **無限ループ問題の回避**
   - detect-secretsは実行時に`generated_at`タイムスタンプを更新
   - 新規ファイル追加時、毎回baseline更新→exit code 3→再ステージ→再実行の無限ループ
   - 参考: [detect-secrets Issue #212](https://github.com/Yelp/detect-secrets/issues/212)

2. **Developer Experience向上**
   - コミット時に予期しないbaseline変更を防ぐ
   - 意図的な更新のみを許可

3. **変更の透明性**
   - Baseline更新を明示的なコマンド実行に限定
   - レビュー時に変更理由が明確

#### 設定（.pre-commit-config.yaml）

```yaml
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.4.0
  hooks:
    - id: detect-secrets
      # baseline を使用しない（新規秘密鍵のみ検出）
      # args: ['--baseline', '.secrets.baseline']
      exclude: (makefiles/ci\.mk|\.gitleaks\.toml|\.secrets\.baseline)
```

## 運用フロー

### 1. 通常のコミット

```bash
# 開発者の通常ワークフロー
git add .
git commit -m "feat: 新機能追加"

# Pre-commit hookが自動実行
# → 新規秘密鍵があれば検出してブロック
# → なければコミット成功
```

**注意**: 既知のfalse-positive（baseline登録済み）は除外済みなので、警告されません。

### 2. Baseline更新

新しいfalse-positiveを追加する場合：

```bash
# Step 1: Baseline更新
make secrets-baseline-update

# Step 2: 変更内容を必ず確認
git diff .secrets.baseline

# 確認項目:
# - 本物の秘密鍵が含まれていないか
# - 追加されたファイル・行番号は妥当か
# - hash値が妥当か

# Step 3: 問題なければコミット
git add .secrets.baseline
git commit -m "update: .secrets.baseline更新 - XXXの誤検知を追加"
```

### 3. マージコンフリクト解決

複数の開発者がbaselineを更新した場合：

```bash
# マージ時にコンフリクト発生
git pull
# CONFLICT (content): Merge conflict in .secrets.baseline

# 自動マージツールを実行
make secrets-baseline-merge

# マージ結果を確認
git diff .secrets.baseline

# 問題なければコミット
git add .secrets.baseline
git commit
```

**内部動作**:

1. 両方のbaselineをPythonスクリプトでマージ
2. JSON `results`フィールドを統合
3. 最新スキャン結果で更新

### 4. 定期監査（四半期ごと推奨）

```bash
# Baseline内容を対話的にレビュー
make secrets-audit

# 各エントリを確認:
# - まだ必要か？
# - 本物の秘密鍵ではないか？
# - 削除すべきか？
```

## トラブルシューティング

### 問題1: 無限ループ（初回コミット時のみ）

**症状**:

```text
Secrets検知 (detect-secrets).............................................Failed
- hook id: detect-secrets
- exit code: 3

The baseline file was updated.
Probably to keep line numbers of secrets up-to-date.
Please `git add .secrets.baseline`, thank you.
```

何度`git add`しても同じエラーが繰り返される。

**原因**:

- `.secrets.baseline`を新規追加する際、`generated_at`タイムスタンプが毎回更新される
- これはdetect-secretsの既知の問題（[Issue #212](https://github.com/Yelp/detect-secrets/issues/212)）

**解決策**:
初回コミット時のみ`--no-verify`を使用：

```bash
git add .secrets.baseline
git commit --no-verify -m "feat: .secrets.baseline初回バージョニング"
```

**なぜこれで解決するか**:

- 1回コミットした後は、baselineがリポジトリに存在する
- 以降は行番号のみの更新なので、通常のワークフローで対応可能

### 問題2: Exit code 3の意味

**Exit Code一覧**:

| Code | 意味 | 対応 |
|------|------|------|
| 0 | 成功（秘密鍵なし） | なし |
| 1 | 秘密鍵検出 | 秘密鍵を削除してコミット |
| 3 | Baseline更新 | `git add .secrets.baseline` して再コミット |

Exit code 3は**エラーではなく通知**です。

### 問題3: 既知のfalse-positiveが再検出される

**症状**:
すでにbaselineに登録したはずのダミー値が警告される。

**原因**:
Pre-commit hookでbaselineを使用していない設定になっている。

**確認**:

```bash
# .pre-commit-config.yaml を確認
grep -A 3 "detect-secrets" .pre-commit-config.yaml
```

**期待される設定**:

```yaml
exclude: (makefiles/ci\.mk|\.gitleaks\.toml|\.secrets\.baseline)
```

既知のfalse-positiveファイルは`exclude`に追加してください。

## 利用可能なコマンド

### Makeターゲット

```bash
# ヘルプ表示
make secrets-help

# Baseline更新
make secrets-baseline-update

# マージコンフリクト解決
make secrets-baseline-merge

# 秘密鍵チェック
make secrets-check

# Baseline監査
make secrets-audit

# 新規プロジェクト用初期化
make secrets-baseline-init
```

### CI/CD統合

すべてのコマンドはci-runnerコンテナ内で実行されます：

```makefile
secrets-baseline-update:
 @$(COMPOSE) -p $(PROJECT_NAME) run --rm ci-runner sh -c '...'
```

**メリット**:

- ローカル環境に依存しない
- CI/CDとローカルで同じツールバージョン使用
- Dockerfileで完全再現可能

## 技術的意思決定記録（ADR）

### ADR-001: .secrets.baselineをバージョニングする

**日付**: 2025-10-24

**ステータス**: Accepted

**コンテキスト**:

- チーム開発で各メンバーが異なるfalse-positiveを持つ
- CI/CD環境でbaselineがないと誤検知が大量発生
- 新規メンバーの環境構築時にbaseline生成が必要

**決定**:
.secrets.baselineをGitで管理し、チーム全体で共有する。

**結果**:

- ✅ CI/CD環境での一貫性確保
- ✅ チーム開発の効率化
- ⚠️ 本物の秘密鍵の誤登録リスク → 更新時の必須確認フローで対応
- ⚠️ マージコンフリクト → 自動マージツールで対応

### ADR-002: Pre-commit hookでbaseline更新しない

**日付**: 2025-10-24

**ステータス**: Accepted

**コンテキスト**:

- detect-secretsの`--baseline`引数使用時、自動更新が発生
- 初回コミット時に無限ループが発生（[Issue #212](https://github.com/Yelp/detect-secrets/issues/212)）
- Developer Experienceの低下

**決定**:
Pre-commit hookでは`--baseline`引数を使用せず、新規秘密鍵のみ検出。
Baseline更新は手動実行（`make secrets-baseline-update`）に限定。

**結果**:

- ✅ 無限ループ問題の完全解決
- ✅ Developer Experience向上（コミット時の予期しない変更なし）
- ✅ 変更の透明性確保（意図的な更新のみ）
- ⚠️ 既知のfalse-positiveファイルを`exclude`に追加する必要あり

### ADR-003: 初回コミット時のみ`--no-verify`を許可

**日付**: 2025-10-24

**ステータス**: Accepted

**コンテキスト**:

- `.secrets.baseline`新規追加時、`generated_at`が毎回更新される
- 通常のワークフローでは回避不可能
- プロジェクトのルールでは`--no-verify`禁止

**決定**:
初回コミット時のみ例外として`--no-verify`を許可。
コミットメッセージに理由を明記することを必須とする。

**結果**:

- ✅ 初回セットアップを完了できる
- ✅ 以降は通常のワークフローで運用可能
- ✅ 例外的使用であることが明確に記録される

## よくある質問（FAQ）

### Q1: なぜ2つのツール（detect-secrets + gitleaks）を使うのか？

**A**: 相互補完による検出精度向上のためです。

- **detect-secrets**: 柔軟なbaseline管理、false-positive除外
- **gitleaks**: 900以上のパターン、網羅的検出

1つのツールでは見逃す可能性のある秘密鍵を、多層防御で検出します。

### Q2: Baselineに登録すべき基準は？

**A**: 以下の条件を**すべて**満たす場合のみ登録してください：

1. ✅ 本物の秘密鍵ではない（ダミー値、例、テストデータ）
2. ✅ コードベースに存在する正当な理由がある
3. ✅ 削除・変更が困難（フレームワークの制約、レガシーコード等）
4. ✅ チーム全員が「これは安全」と合意できる

**疑わしい場合は登録せず、コードを修正してください。**

### Q3: `.env`ファイルの扱いは？

**A**: `.env`ファイルは`.gitignore`で除外されるべきです。

```gitignore
# .gitignore
.env
.env.local
.env.*.local
```

Baselineに登録するのではなく、そもそもGit管理対象外にしてください。

### Q4: テストコード内のダミーAPIキーはどうするか？

**A**: 以下の優先順位で判断してください：

1. **最優先**: モック/スタブを使用（実際の値不要）
2. **次善**: 明らかに無効な値（`"dummy-api-key-for-testing"`）
3. **最終手段**: Baselineに登録（ファイルをexcludeに追加）

### Q5: CI/CDでも同じ設定で動くか？

**A**: はい。すべてのコマンドはci-runnerコンテナ内で実行されます。

```bash
# ローカル
make secrets-check

# CI/CD（同じDockerイメージ使用）
make secrets-check
```

環境差分はありません。

### Q6: Baseline監査の頻度は？

**A**: **四半期ごと（3ヶ月に1回）**を推奨します。

```bash
# 監査実行
make secrets-audit

# 確認項目:
# - 各エントリがまだ必要か
# - コードから削除されたエントリを除外
# - 新しい検出パターンで再評価
```

チームの規模やコミット頻度に応じて調整してください。

### Q7: 他のブランチでbaselineが更新されたらどうする？

**A**: マージ時に自動マージツールを使用してください：

```bash
git pull  # コンフリクト発生
make secrets-baseline-merge  # 自動マージ
git add .secrets.baseline
git commit
```

手動でマージしないでください。JSONフォーマットが壊れる可能性があります。

## 参考資料

### 公式ドキュメント

- [detect-secrets GitHub](https://github.com/Yelp/detect-secrets)
- [gitleaks GitHub](https://github.com/gitleaks/gitleaks)
- [pre-commit Framework](https://pre-commit.com/)

### 関連Issue・PR

- [detect-secrets Issue #212 - Baseline mutation problem](https://github.com/Yelp/detect-secrets/issues/212)
- [detect-secrets Issue #149 - Duplicate output messages](https://github.com/Yelp/detect-secrets/issues/149)

### プロジェクト内ドキュメント

- [CLAUDE.md - セキュリティ注意事項](../../CLAUDE.md#セキュリティ注意事項)
- [README.md - .secrets.baseline運用ガイドライン](../../README.md#secrets-baseline-運用ガイドライン)
- [makefiles/secrets.mk](../../makefiles/secrets.mk) - 実装詳細

### ベストプラクティス

- [OWASP - Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub - Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

## 更新履歴

| 日付 | バージョン | 変更内容 | 作成者 |
|------|-----------|---------|--------|
| 2025-10-24 | 1.0.0 | 初版作成 | Claude Code |

---

**メンテナンス責任者**: プロジェクトメンテナー全員

**次回レビュー予定**: 2026-01-24（3ヶ月後）
