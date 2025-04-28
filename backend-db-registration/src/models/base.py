from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 環境変数から接続情報を取得（デフォルト値付き）
DB_HOST = os.getenv('MEMBER_DB_HOST', 'localhost')
DB_PORT = os.getenv('MEMBER_DB_PORT', '5432')  # デフォルト値を設定
DB_USER = os.getenv('MEMBER_DB_USER', 'testuser')
DB_PASSWORD = os.getenv('MEMBER_DB_PASSWORD', 'password')
DB_NAME = os.getenv('MEMBER_DB_NAME', 'member_db')

# 環境変数を使用した接続URLの構築
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# エラーハンドリングの追加
try:
    engine = create_engine(DATABASE_URL)
    # 接続テスト
    engine.connect()
    print("データベースへの接続に成功しました")
except Exception as e:
    print(f"データベース接続エラー: {e}")
    raise

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデルのベースクラス
Base = declarative_base()

def get_db():
    """
    データベースセッションを取得するための関数
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()