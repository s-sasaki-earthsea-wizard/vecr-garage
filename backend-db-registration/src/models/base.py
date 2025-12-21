import json
import logging
import os

import boto3
from botocore.exceptions import ClientError
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)


def get_secret_from_aws(aws_secret_id, key):
    """AWS Secrets Managerから秘密鍵を取得"""
    try:
        aws_profile = os.getenv("AWS_PROFILE")
        if aws_profile:
            session = boto3.Session(profile_name=aws_profile)
            client = session.client("secretsmanager")
        else:
            client = boto3.client("secretsmanager")

        response = client.get_secret_value(SecretId=aws_secret_id)
        secret_dict = json.loads(response["SecretString"])
        return secret_dict.get(key)
    except (ClientError, Exception) as e:
        logger.debug(f"AWS Secrets Manager取得失敗: {e}")
        return None


def get_config_value(key, aws_secret_id="vecr-garage-dev-app-secrets"):
    """AWS Secrets Managerから設定値を取得"""
    secret_value = get_secret_from_aws(aws_secret_id, key)
    if not secret_value:
        raise ValueError(
            f"設定値'{key}'がSecrets Manager '{aws_secret_id}'から取得できませんでした"
        )
    return secret_value


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
