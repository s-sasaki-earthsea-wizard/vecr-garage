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

### 対応テーブル
- `human_members`: 人間メンバー情報
- `human_member_profiles`: 人間メンバープロフィール
- `virtual_members`: AIメンバー情報
- `virtual_member_profiles`: AIメンバープロフィール
- `member_relationships`: メンバー間の関係性

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

## 将来の実装計画

### Phase 1: データベース連携
- [ ] PostgreSQL接続の実装
- [ ] SQLAlchemy ORMの導入
- [ ] 実データの読み込み・更新・削除

### Phase 2: テンプレート化
- [ ] Jinjaテンプレートによるサーバーサイドレンダリング
- [ ] 動的なテーブル一覧取得
- [ ] カラム情報の自動取得

### Phase 3: 機能拡張
- [ ] ユーザー認証・認可
- [ ] バッチインポート/エクスポート
- [ ] MinIOストレージ連携（プロフィール画像等）
- [ ] リアルタイム更新（WebSocket）
- [ ] 検索・フィルタリング機能
- [ ] ページネーション

### Phase 4: UI/UX改善
- [ ] Vue.js/Reactへの移行検討
- [ ] レスポンシブデザインの強化
- [ ] ダークモード対応
- [ ] 多言語対応

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