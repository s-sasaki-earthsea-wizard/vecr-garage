"""
AWS Secrets Manager共有モジュール

AWS Secrets Managerからの機密情報取得機能を提供します。
各サービスで共通利用される関数群を定義しています。
"""

import json
import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def get_secret_from_aws(aws_secret_id: str, key: str) -> Optional[str]:
    """
    AWS Secrets Managerから指定されたキーの値を取得する

    Args:
        aws_secret_id: AWS Secrets ManagerのシークレットID
        key: 取得したい設定値のキー

    Returns:
        設定値（文字列）、取得に失敗した場合はNone

    Raises:
        なし（例外は内部でキャッチしてNoneを返す）
    """
    try:
        # AWS設定は.awsディレクトリからboto3が自動的に読み込み
        client = boto3.client("secretsmanager")

        response = client.get_secret_value(SecretId=aws_secret_id)
        secret_dict = json.loads(response["SecretString"])
        return secret_dict.get(key)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ResourceNotFoundException":
            logger.warning(
                f"Secrets Manager ID '{aws_secret_id}' が見つかりません。"
                f"AWS環境で適切にシークレットが作成されているか確認してください。"
            )
        elif error_code == "AccessDeniedException":
            logger.error(
                f"Secrets Manager '{aws_secret_id}' へのアクセスが拒否されました。"
                f"IAM権限を確認してください。"
            )
        elif error_code == "InvalidParameterException":
            logger.error(
                f"Secrets Manager ID '{aws_secret_id}' のパラメータが不正です。"
            )
        elif error_code == "InvalidRequestException":
            logger.error(
                f"Secrets Manager '{aws_secret_id}' への無効なリクエストです。"
                f"シークレットのフォーマットを確認してください。"
            )
        else:
            logger.error(
                f"AWS Secrets Manager APIエラー: {error_code} - {e.response['Error']['Message']}"
            )
        return None
    except json.JSONDecodeError as e:
        logger.error(
            f"Secrets Manager '{aws_secret_id}' の値をJSONとして解析できませんでした: {e}"
        )
        return None
    except Exception as e:
        logger.error(f"AWS Secrets Manager取得時の予期しないエラー: {type(e).__name__}: {e}")
        return None


def get_config_value(key: str, aws_secret_id: str = "vecr-garage-dev-app-secrets") -> str:
    """
    AWS Secrets Managerから設定値を取得する

    取得に失敗した場合は明確にエラーを発生させることで、
    インフラ側の問題を早期発見できるようにしています。

    Args:
        key: 取得したい設定値のキー
        aws_secret_id: AWS Secrets ManagerのシークレットID

    Returns:
        設定値（文字列）

    Raises:
        ValueError: 設定値の取得に失敗した場合
    """
    secret_value = get_secret_from_aws(aws_secret_id, key)
    if not secret_value:
        raise ValueError(
            f"設定値'{key}'がSecrets Manager '{aws_secret_id}'から取得できませんでした"
        )
    return secret_value
