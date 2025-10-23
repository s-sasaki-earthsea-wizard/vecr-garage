# 認証システム

## 認証戦略ロードマップ

VECR Garageプロジェクトでは、開発段階に応じた3段階の認証システムを計画しています。

### Phase 1: モックアップ認証（✅ 実装済み）

**目的**: UI/UX検証・プロトタイピング

#### 実装内容

**技術スタック**:
- 環境変数ベースの簡易認証
- Flask-Session によるセッション管理
- ログイン/ログアウト機能
- パスワード表示切り替えボタン（👁️/🙈）

**環境変数設定**:
```bash
# .env.exampleから.envにコピーして使用
ADMIN_USERNAME=Admin
ADMIN_PASSWORD=SamplePassword
SECRET_KEY=vecr-garage-secret-key-development-only-2025
```

#### 実装済み機能

**ログインページデザイン**:
- 美しいUIデザイン
- パスワード表示切り替えボタン
- エラーメッセージ表示

**セッション管理**:
- Flask-Sessionによるサーバーサイドセッション
- セッションタイムアウト（30分）
- ログアウト機能

**API保護**:
- `@login_required`デコレータ
- 全APIエンドポイントの保護
- 未認証時のリダイレクト

**実装ファイル**:
- `member-manager/app.py`: 認証ロジック実装
- `member-manager/templates/login.html`: ログインページ

#### セキュリティ考慮事項

⚠️ **現在のモックアップ段階の制限**:
- 平文パスワード（開発専用）
- 簡易セッション管理
- HTTPS非対応（ローカル環境）
- 単一ユーザーのみ（Admin）

✅ **本番環境では使用不可** - Phase 2以降の実装が必須

### Phase 2: セッションベース認証（次期実装）

**目的**: 開発・ステージング環境での実用化

#### 計画内容

**技術スタック**:
```python
auth_stack = [
    "Flask-Login",      # セッション管理
    "Flask-WTF",        # CSRF保護
    "Flask-Limiter",    # レート制限
    "bcrypt",           # パスワードハッシュ化
    "Redis"             # セッションストア
]
```

**実装予定機能**:
- パスワードハッシュ化（bcrypt）
- CSRF保護（Flask-WTF）
- レート制限（Flask-Limiter）
- Redis セッションストア
- セッション有効期限管理
- ログイン試行回数制限
- 多要素認証（MFA）の準備

**セキュリティヘッダー**:
```python
# Content Security Policy
Content-Security-Policy: default-src 'self'

# X-Frame-Options
X-Frame-Options: DENY

# X-Content-Type-Options
X-Content-Type-Options: nosniff

# Strict-Transport-Security (HTTPS必須)
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### Phase 3: 本番環境認証（将来実装）

**目的**: 本格運用・AWS統合

#### 計画内容

**AWS統合サービス**:
```yaml
aws_services:
  authentication: AWS Cognito
  secrets: AWS Secrets Manager
  certificates: AWS Certificate Manager
  deployment: EKS + ALB
```

**実装予定機能**:
- AWS Cognito統合
- MFA（多要素認証）対応
- ソーシャルログイン連携（Google, GitHub等）
- JWT認証 + API Gateway
- SAML/OAuth 2.0対応
- 監査ログ（CloudWatch Logs）
- セキュリティアラート（CloudWatch Alarms）

**アーキテクチャ図**:
```
[ユーザー]
  ↓ HTTPS
[ALB (SSL/TLS Termination)]
  ↓
[API Gateway (JWT検証)]
  ↓
[EKS (Kubernetes)]
  ├─ member-manager Pod
  ├─ backend-db-registration Pod
  └─ backend-llm-response Pod
  ↓
[AWS Cognito (認証)]
[AWS Secrets Manager (認証情報)]
[RDS (PostgreSQL)]
```

## 現在の実装詳細（Phase 1）

### アクセス方法

**ローカル環境**:
```bash
# ブラウザでアクセス
http://localhost:8000/

# ログインページに自動リダイレクト
http://localhost:8000/login
```

**認証情報**:
- ユーザー名: `Admin` （`.env`の`ADMIN_USERNAME`）
- パスワード: `SamplePassword` （`.env`の`ADMIN_PASSWORD`）

### 実装コード例

#### ログインエンドポイント

```python
# member-manager/app.py

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 環境変数と照合
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            flash('ログインしました', 'success')
            return redirect(url_for('index'))
        else:
            flash('ユーザー名またはパスワードが正しくありません', 'error')

    return render_template('login.html')
```

#### ログアウトエンドポイント

```python
@app.route('/logout')
def logout():
    session.clear()
    flash('ログアウトしました', 'info')
    return redirect(url_for('login'))
```

#### ログイン必須デコレータ

```python
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('ログインが必要です', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 使用例
@app.route('/api/members')
@login_required
def get_members():
    # API実装
```

### セッション設定

```python
# member-manager/app.py

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'vecr-garage-secret-key-development-only-2025')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
```

## セキュリティベストプラクティス

### 開発環境（Phase 1）

✅ **実施済み**:
- セッション管理
- ログイン/ログアウト機能
- 未認証時のリダイレクト
- `.env`ファイルの`.gitignore`保護

⚠️ **実施推奨**:
- HTTPSの使用（ローカル開発でも）
- セッションタイムアウトの適切な設定
- 定期的なシークレットキー更新

### 本番環境（Phase 3）

✅ **必須要件**:
- パスワードハッシュ化必須
- HTTPS通信強制
- セキュリティヘッダー設定
- 監査ログ記録
- レート制限
- CSRF保護
- XSS対策
- SQL injection対策
- セキュリティパッチの定期適用

## トラブルシューティング

### ログインできない

**症状**: ユーザー名・パスワードを入力してもログインできない

**解決策**:
```bash
# 1. 環境変数確認
docker exec vecr-garage-member-manager env | grep ADMIN

# 2. .envファイル確認
cat .env | grep ADMIN

# 3. コンテナ再起動
make docker-restart
```

### セッションが切れる

**症状**: ログイン後すぐにセッションが切れる

**解決策**:
```python
# app.py でセッションタイムアウト時間を延長
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
```

### ログインページにリダイレクトされ続ける

**症状**: 無限リダイレクトループ

**解決策**:
```bash
# 1. ブラウザのクッキー削除
# 2. シークレットキー確認
cat .env | grep SECRET_KEY

# 3. セッションファイル削除
docker exec vecr-garage-member-manager rm -rf /app/flask_session/*
```

## 関連ドキュメント

- [サービス構成](../architecture/services.md)
- [よく使うコマンド](../development/commands.md)
- [トラブルシューティング](../development/troubleshooting.md)
