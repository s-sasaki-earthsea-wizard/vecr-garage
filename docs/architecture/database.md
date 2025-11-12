# データベース設計

## PostgreSQLメンバーデータベース

### 接続情報

```bash
# PostgreSQL接続
docker exec -it vecr-garage-db-member psql -U testuser -d member_db

# または
make db-member-psql
```

**接続パラメータ**:

- ホスト: `db-member` (コンテナ内) / `localhost:5432` (ホストから)
- データベース名: `member_db`
- ユーザー: `testuser`
- パスワード: `password` (開発環境のみ)

### テーブル構造

#### human_members（人間メンバー）

```sql
CREATE TABLE human_members (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(255),
    skills TEXT[],
    bio TEXT,
    contact_email VARCHAR(255),
    github_username VARCHAR(255),
    file_uri VARCHAR(512),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**フィールド説明**:

- `id`: 自動採番されるプライマリーキー
- `name`: メンバー名（一意制約）
- `role`: 役割・職種
- `skills`: スキルセット（配列型）
- `bio`: 自己紹介文
- `contact_email`: 連絡先メールアドレス
- `github_username`: GitHubユーザー名
- `file_uri`: MinIOストレージ上のYMLファイルパス
- `created_at`: 作成日時
- `updated_at`: 更新日時

#### virtual_members（仮想メンバー）

```sql
CREATE TABLE virtual_members (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(255),
    llm_model VARCHAR(255) NOT NULL,
    system_prompt TEXT,
    personality_traits TEXT[],
    expertise_areas TEXT[],
    file_uri VARCHAR(512),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**フィールド説明**:

- `id`: 自動採番されるプライマリーキー
- `name`: メンバー名（一意制約）
- `role`: 役割・職種
- `llm_model`: 使用するLLMモデル（必須）
- `system_prompt`: システムプロンプト
- `personality_traits`: 性格特性（配列型）
- `expertise_areas`: 専門分野（配列型）
- `file_uri`: MinIOストレージ上のYMLファイルパス
- `created_at`: 作成日時
- `updated_at`: 更新日時

### データベース操作

#### テーブル確認

```sql
-- テーブル一覧表示
\dt

-- テーブル構造確認
\d human_members
\d virtual_members

-- データ確認
SELECT * FROM human_members;
SELECT * FROM virtual_members;

-- 件数確認
SELECT COUNT(*) FROM human_members;
SELECT COUNT(*) FROM virtual_members;
```

#### UPSERT処理

**現在の実装**: name-based UPSERT（暫定実装）

```python
# backend-db-registration/src/db/database.py

def save_or_update_human_member(session, member_data):
    """人間メンバーの保存または更新（name基準）"""
    existing_member = session.query(HumanMember).filter_by(
        name=member_data.name
    ).first()

    if existing_member:
        # 既存メンバーを更新
        for key, value in member_data.__dict__.items():
            if not key.startswith('_'):
                setattr(existing_member, key, value)
        existing_member.updated_at = datetime.now()
    else:
        # 新規メンバーを作成
        session.add(member_data)

    session.commit()

def save_or_update_virtual_member(session, member_data):
    """仮想メンバーの保存または更新（name基準）"""
    # 同様の実装
```

**将来の実装計画**: file_uri-based UPSERT

- `file_uri`をユニークキーとして使用
- PostgreSQLの`ON CONFLICT DO UPDATE`句活用
- ファイル単位での厳密な重複管理

### データベース運用ルール

#### トランザクション処理

- トランザクション処理を必須とする
- エラー時は必ずロールバック
- SQLAlchemyのセッション管理を適切に行う

**実装例**:

```python
from sqlalchemy.orm import Session

def process_member_data(session: Session, data: dict):
    try:
        # データベース操作
        member = create_member(data)
        session.add(member)
        session.commit()
        return member
    except Exception as e:
        session.rollback()
        logger.error(f"データベースエラー: {e}")
        raise
    finally:
        session.close()
```

#### バックアップとリストア

**開発環境**:

```bash
# バックアップ
docker exec vecr-garage-db-member pg_dump -U testuser member_db > backup.sql

# リストア
docker exec -i vecr-garage-db-member psql -U testuser member_db < backup.sql
```

**本番環境**: AWS RDS自動バックアップを推奨

### ヘルスチェック

```bash
# データベース接続確認
docker ps --format "table {{.Names}}\t{{.Status}}" | grep db-member
# 出力: vecr-garage-db-member   Up X minutes (healthy)

# 手動ヘルスチェック
docker exec vecr-garage-db-member pg_isready -U testuser
```

## DynamoDBチャットログ（将来実装）

### 実装予定

- LocalStack環境での開発
- 会話履歴の永続化
- セッション管理
- Discord Bot会話ログ管理

### テーブル設計案

```python
{
    "TableName": "ChatLogs",
    "KeySchema": [
        {"AttributeName": "session_id", "KeyType": "HASH"},  # Partition key
        {"AttributeName": "timestamp", "KeyType": "RANGE"}   # Sort key
    ],
    "AttributeDefinitions": [
        {"AttributeName": "session_id", "AttributeType": "S"},
        {"AttributeName": "timestamp", "AttributeType": "N"}
    ]
}
```

## 関連ドキュメント

- [サービス構成](services.md)
- [Webhook自動化システム](webhook-automation.md)
- [テスト戦略](../development/testing.md)
