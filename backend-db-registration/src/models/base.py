import logging

from aws_utils.secrets_manager import get_config_value
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)


# AWS Secrets Managerから接続情報を取得
DB_HOST = get_config_value("MEMBER_DB_HOST")
DB_PORT = get_config_value("MEMBER_DB_PORT")
DB_USER = get_config_value("MEMBER_DB_USER")
DB_PASSWORD = get_config_value("MEMBER_DB_PASSWORD")
DB_NAME = get_config_value("MEMBER_DB_NAME")

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
    """データベースセッションを取得するための関数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
