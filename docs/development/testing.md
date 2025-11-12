# テスト戦略

## 包括的テストシステム（✅ 実装完了）

**実装目的**: ユニットテストからE2Eテストまでを統合した包括的品質保証システム

### 🏗️ テストシステム構成

#### テストファイル構成

- `makefiles/backend-db-registration-tests.mk`: backend-db-registration専用テスト集約
- `makefiles/yml-file-operations.mk`: YMLファイル操作統合システム
- `makefiles/integration.mk`: サービス横断統合テスト

#### 既存のpytestユニットテストを活用

- 25の包括的テストケース（正常・異常系）
- docker exec による実際のコンテナ内実行
- 実データベース接続での検証

### 🧪 テストターゲット体系

#### backend-db-registration専用テスト

```bash
# ユニットテストのみ
make backend-db-registration-test-unit

# 正常系E2Eテスト（DB登録確認）
make backend-db-registration-test-samples

# 異常系エラーハンドリング（HTTP 400確認）
make backend-db-registration-test-cases

# 上記すべて統合実行
make backend-db-registration-test-integration
```

#### backend-llm-response専用テスト

```bash
# Discord Webhook動作確認
make discord-verify

# Claude API接続テスト
make claude-test

# Discord Bot設定テスト
make discord-bot-test-config
```

#### システム統合テスト

```bash
# 全サービス統合テスト
make test-integration
```

### ✅ テスト結果

#### 包括的テスト実行結果

- **Unit Tests**: 25 tests passed（pytest container execution）
- **Sample Processing**: Human & Virtual member DB registration confirmed
- **Error Handling**: HTTP 400 validation errors properly handled
- **E2E Integration**: File upload → Webhook → DB registration verified

#### 自動クリーンアップ

- テストファイル自動削除
- 副作用なしの隔離されたテスト実行

### 🎯 実現した価値

#### テストカバレッジ

- **Unit Level**: コアロジックの品質保証
- **Integration Level**: Webhook処理の動作確認
- **E2E Level**: ファイルからDB登録までの全工程検証

#### 開発効率向上

- 段階的実行可能（個別テスト対応）
- 既存pytestリソースの最大活用
- 統合実行での包括的品質確認

## テストケース設計

### 正常系テスト

**Sample Files**:

- `data/samples/human_members/`: 人間メンバーの正常な登録ファイル
- `data/samples/virtual_members/`: 仮想メンバーの正常な登録ファイル

**実行方法**:

```bash
# 全サンプルファイルをコピー＆DB登録確認
make backend-db-registration-test-samples
```

### 異常系テスト

**Test Cases**:

- `data/test_cases/human_members/`: 人間メンバーの異常系テストケース
  - `invalid_missing_name.yml`: nameフィールド欠損（ValidationError）
  - `invalid_empty_file.yml`: 空ファイル（'NoneType' object エラー）
- `data/test_cases/virtual_members/`: 仮想メンバーの異常系テストケース
  - `invalid_missing_name.yml`: nameフィールド欠損（ValidationError）
  - `invalid_missing_model.yml`: llm_modelフィールド欠損（ValidationError）

**実行方法**:

```bash
# 異常系ファイルをコピー＆エラーハンドリング確認
make backend-db-registration-test-cases
```

## バリデーション処理

### エラーハンドリング設計

**責任分離**:

- `process_file_event`: 純粋なファイル処理の責任（単一責任の原則）
- `handle_webhook`: 例外処理とエラーログの統一管理
- ValidationError、DatabaseError、その他の例外を適切に分離
- 異常系ファイルは確実にエラーとして検出され、HTTP 400で応答

**実装例**:

```python
# backend-db-registration/src/services/webhook_file_watcher.py

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    try:
        # ファイル処理
        result = process_file_event(event_data)
        return jsonify(result), 200
    except ValidationError as e:
        logger.error(f"バリデーションエラー: {e}")
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        logger.error(f"データベースエラー: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        return jsonify({"error": "Internal server error"}), 500
```

## pytest実行

### backend-db-registrationユニットテスト

```bash
# コンテナ内でpytest実行
docker exec -it vecr-garage-backend-db-registration pytest tests/

# または
make backend-db-registration-test-unit
```

### backend-llm-responseユニットテスト

```bash
# コンテナ内でpytest実行
docker exec -it vecr-garage-backend-llm-response pytest tests/
```

## 型チェック・リンター

### Python（各backendサービス内で実行）

```bash
# 型チェック
mypy src/

# リンター
ruff check src/

# フォーマッター
black src/
```

### 実行例（backend-db-registration）

```bash
# シェル接続
make backend-db-registration-shell

# コンテナ内で実行
mypy src/
ruff check src/
black src/
```

## YMLファイル操作統合システム

### ファイル操作の統一管理（✅ 実装完了）

**実装目的**: samples.mkとtest-cases.mkの重複排除とファイル操作の一元化

#### 利用可能なコマンド

**Sample Files (正常系)**:

```bash
make samples-copy              # 全サンプルファイルコピー
make samples-copy-human        # 人間メンバーのみ
make samples-copy-virtual      # 仮想メンバーのみ
make samples-copy-single FILE=filename.yml  # 個別ファイル
make samples-clean             # サンプルファイル削除
make samples-verify            # 登録確認
```

**Test Cases (異常系)**:

```bash
make test-cases-copy           # 全テストケースコピー
make test-cases-copy-human     # 人間メンバーのみ
make test-cases-copy-virtual   # 仮想メンバーのみ
make test-cases-copy-single FILE=filename.yml  # 個別ファイル
make test-cases-clean          # テストケース削除
make test-cases-verify         # エラー応答確認
```

## CI/CD統合（将来実装）

### GitHub Actions（計画中）

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build containers
        run: make docker-build-up
      - name: Run integration tests
        run: make test-integration
      - name: Run unit tests
        run: |
          make backend-db-registration-test-unit
          docker exec vecr-garage-backend-llm-response pytest tests/
```

## 関連ドキュメント

- [Webhook自動化システム](../architecture/webhook-automation.md)
- [データベース設計](../architecture/database.md)
- [よく使うコマンド](commands.md)
