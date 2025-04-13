from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 環境変数から接続情報を取得
DB_HOST = os.getenv('MEMBER_DB_HOST')
DB_PORT = os.getenv('MEMBER_DB_PORT')
DB_USER = os.getenv('MEMBER_DB_USER')
DB_PASSWORD = os.getenv('MEMBER_DB_PASSWORD')
DB_NAME = os.getenv('MEMBER_DB_NAME')

# PostgreSQL接続URL
DATABASE_URL = "postgresql://testuser:password@localhost:5432/member_db"

# エンジンの作成
engine = create_engine(DATABASE_URL)

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