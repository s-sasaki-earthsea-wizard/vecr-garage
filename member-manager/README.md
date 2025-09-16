# Member Manager Service

## 概要

VECR Garage メンバー管理サービスのWebインターフェースです。
現在はモックアップ版として実装されており、将来的にはPostgreSQLデータベースと連携予定です。

## 現在の実装状況（モックアップ）

### 技術スタック
- **バックエンド**: Flask 3.0.0
- **フロントエンド**: Vanilla JavaScript
- **スタイリング**: Pure CSS
- **データ**: ハードコードされたモックデータ

### 機能
- テーブル選択（プルダウンメニュー）
- データ表示（テーブル形式）
- レコード編集（モーダルダイアログ）
- レコード削除（確認ダイアログ付き）
- レコード追加
- YAMLファイル生成・アップロード機能

### 対応テーブル
- `human_members`: 人間メンバー情報
- `human_member_profiles`: 人間メンバープロフィール
- `virtual_members`: AIメンバー情報
- `virtual_member_profiles`: AIメンバープロフィール
- `member_relationships`: メンバー間の関係性

## YAMLファイル生成・アップロード機能

### 概要
新規レコード追加時に、フォーム入力データからYAMLファイルを自動生成し、MinIOストレージサービスにアップロードする機能を実装しています。

### 使用方法

#### 1. 新規レコード追加
1. ブラウザで `http://localhost:8000` にアクセス
2. テーブル選択プルダウンから対象テーブルを選択
3. 「新規レコード追加」ボタンをクリック
4. モーダルダイアログで必須項目を入力

#### 2. YAMLファイル生成・アップロード
1. フォーム入力完了後、「保存」ボタンをクリック
2. 成功時：「新規レコード追加成功」メッセージが表示

#### 3. アップロード確認
1. MinIOブラウザコンソールにアクセス：`http://localhost:9001`
2. `vecr-garage-storage` 内でアップロードされたYAMLファイルを確認

## 起動方法

### Dockerコンテナで起動（推奨）
```bash
# プロジェクトルートで実行
make docker-up

# ブラウザでアクセス
http://localhost:8000
```

### ローカル環境で起動
```bash
# member-managerディレクトリに移動
cd member-manager

# 依存パッケージをインストール
pip install -r requirements.txt

# Flaskアプリケーション起動
python app.py

# ブラウザでアクセス
http://localhost:8000
```

## ディレクトリ構造
```
member-manager/
├── app.py                 # Flaskアプリケーション本体
├── requirements.txt       # Python依存パッケージ
├── templates/
│   └── index.html        # メインHTML（将来Jinjaテンプレート化）
├── static/
│   ├── css/
│   │   └── style.css     # スタイルシート
│   └── js/
│       └── main.js       # JavaScript（テーブル操作）
└── README.md             # このファイル
```

## 認証システム

### 現在のモックアップ実装
- 環境変数ベース簡易認証
- Flask-Session によるセッション管理
- ログイン/ログアウト機能

### 本番環境での技術選択肢

#### Option 1: セッションベース認証（推奨・次期実装）
```python
# 技術スタック
auth_stack = [
    "Flask-Login",      # セッション管理・ユーザーローダー
    "Flask-WTF",        # CSRF保護
    "Flask-Limiter",    # レート制限・ブルートフォース対策
    "bcrypt",           # パスワードハッシュ化
    "Redis",            # セッションストア（EKS対応）
    "PostgreSQL"        # ユーザー情報管理
]
```

**メリット**: 
- シンプルな実装
- EKS移行が容易
- 既存コンテナ構成を活用

#### Option 2: JWT + OAuth2.0（高度な要求に対応）
```python
# 技術スタック
jwt_stack = [
    "Flask-JWT-Extended", # JWT管理
    "Authlib",            # OAuth2.0クライアント
    "Redis",              # JWTブラックリスト
    "PostgreSQL"          # ユーザー管理
]
```

#### Option 3: AWS Cognito統合（本番推奨）
```yaml
# AWSサービス統合
aws_auth:
  user_pool: AWS Cognito User Pools
  identity: AWS Cognito Identity Pools
  mfa: SMS/TOTP多要素認証
  social: Google/Facebook/Apple統合
  secrets: AWS Secrets Manager
  
# EKSデプロイメント
deployment:
  container: EKS Fargate
  load_balancer: ALB + SSL termination
  session_store: ElastiCache Redis
  database: RDS PostgreSQL
```

**メリット**:
- 完全マネージド認証サービス
- MFA・ソーシャルログイン標準対応
- AWS IAMとのシームレス統合
- スケーラビリティ・可用性の保証

### セキュリティ実装ロードマップ

#### Phase 1: モックアップ（現在）
```bash
# 環境変数認証（開発専用・.env.exampleから.envにコピーして使用）
ADMIN_USERNAME=vecr_admin
ADMIN_PASSWORD=vecr_secure_2025
```

#### Phase 2: セッション認証（開発・ステージング）
- パスワードハッシュ化（bcrypt）
- CSRF保護実装
- レート制限設定
- セキュリティヘッダー追加

#### Phase 3: 本番環境（AWS統合）
- AWS Cognito導入
- HTTPS強制・SSL証明書管理
- 監査ログ記録
- 侵入検知システム連携

## 将来の実装計画

### Phase 1: 認証システム強化
- [x] モックアップ認証実装
- [ ] Flask-Login + セッション管理
- [ ] AWS Cognito統合検討

### Phase 2: データベース連携
- [ ] PostgreSQL接続の実装
- [ ] SQLAlchemy ORMの導入
- [ ] 実データの読み込み・更新・削除

### Phase 3: テンプレート化
- [ ] Jinjaテンプレートによるサーバーサイドレンダリング
- [ ] 動的なテーブル一覧取得
- [ ] カラム情報の自動取得

### Phase 4: 機能拡張
- [x] **MinIOストレージ連携（YAMLファイルアップロード）**
- [ ] バッチインポート/エクスポート
- [ ] MinIOストレージ連携（プロフィール画像等）
- [ ] リアルタイム更新（WebSocket）
- [ ] 検索・フィルタリング機能
- [ ] ページネーション

### Phase 5: UI/UX改善
- [ ] Vue.js/Reactへの移行検討
- [ ] レスポンシブデザインの強化
- [ ] ダークモード対応
- [ ] 多言語対応

### Phase 6: 本番デプロイメント
- [ ] EKS クラスター設定
- [ ] ALB + SSL証明書設定
- [ ] RDS・ElastiCache統合
- [ ] 監視・ログ収集システム

## API エンドポイント（モック）

### テーブル一覧取得
```
GET /api/tables
```

### テーブルデータ取得
```
GET /api/table/<table_name>
```

### レコード追加
```
POST /api/table/<table_name>/record
Content-Type: application/json

{
  "member_name": "新規メンバー",
  ...
}
```

### レコード更新
```
PUT /api/table/<table_name>/record/<record_id>
Content-Type: application/json

{
  "member_name": "更新後の名前",
  ...
}
```

### レコード削除
```
DELETE /api/table/<table_name>/record/<record_id>
```

## 注意事項

- **このアプリケーションはモックアップです**
- データはメモリ上にのみ保存され、再起動で失われます
- 実際のデータベース操作は行われません
- 本番環境での使用は想定されていません

## 開発者向け情報

### コーディング規約
- Python: PEP 8準拠
- JavaScript: ES6+
- CSS: BEM命名規則（将来的に）

### テスト
```bash
# 将来的に実装予定
pytest tests/
```

### デバッグ
Flaskアプリケーションはデバッグモードで起動します：
```python
app.run(debug=True)
```

## ライセンス

[プロジェクトのライセンスに準拠]

## 貢献

プルリクエストは歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。