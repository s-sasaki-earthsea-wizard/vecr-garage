import json
import logging
import os

import boto3
from botocore.exceptions import ClientError
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)


def get_secret_from_aws(secret_name, key):
    """AWS Secrets Managerから秘密鍵を取得"""
    try:
        aws_profile = os.getenv("AWS_PROFILE")
        if aws_profile:
            session = boto3.Session(profile_name=aws_profile)
            client = session.client("secretsmanager")
        else:
            client = boto3.client("secretsmanager")

        response = client.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(response["SecretString"])
        return secret_dict.get(key)
    except (ClientError, Exception) as e:
        logger.debug(f"AWS Secrets Manager取得失敗: {e}")
        return None


def get_config_value(key, secret_name="vecr-garage-dev-app-secrets", default=None):
    """設定値を取得: Secrets Manager → 環境変数 → デフォルト値"""
    secret_value = get_secret_from_aws(secret_name, key)
    if secret_value:
        return secret_value

    env_value = os.getenv(key)
    if env_value:
        return env_value

    return default


# Secrets Manager → 環境変数 → デフォルト値の順で接続情報を取得
DB_HOST = get_config_value("MEMBER_DB_HOST", default="localhost")
DB_PORT = get_config_value("MEMBER_DB_PORT", default="5432")
DB_USER = get_config_value("MEMBER_DB_USER", default="testuser")
DB_PASSWORD = get_config_value("MEMBER_DB_PASSWORD", default="password")
DB_NAME = get_config_value("MEMBER_DB_NAME", default="member_db")

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
