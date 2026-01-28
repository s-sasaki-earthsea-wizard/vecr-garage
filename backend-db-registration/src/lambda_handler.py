"""
AWS Lambda関数エントリーポイント

S3イベントトリガーによるメンバー登録処理のLambda関数エントリーポイントです。
S3バケットへのYAMLファイルアップロードを検知し、既存のWebhookFileWatcherServiceを
呼び出してメンバー登録処理を実行します。

使用方法:
    Lambda関数のHandlerに `lambda_handler.handler` を指定してください。
    （または src.lambda_handler.handler、デプロイパッケージの構成による）

環境変数:
    MEMBER_DB_HOST: RDSエンドポイント（Secrets Managerから取得推奨）
    MEMBER_DB_NAME: データベース名（Secrets Managerから取得推奨）
    MEMBER_DB_USER: データベースユーザー（Secrets Managerから取得推奨）
    MEMBER_DB_PASSWORD: データベースパスワード（Secrets Managerから取得推奨）
    S3_BUCKET_NAME: S3バケット名
    AWS_REGION: AWSリージョン
    WEBHOOK_ETAG_CHECK_ENABLED: ETag重複チェックの有効/無効（デフォルト: true）
"""

import json
import logging
from typing import Any

from services.webhook_file_watcher import WebhookFileWatcherService

# ロガー設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def convert_s3_event_to_webhook_format(s3_event: dict[str, Any]) -> dict[str, Any]:
    """AWS S3イベントをWebhookFileWatcherService用の形式に変換する

    AWS S3 Lambdaトリガーのイベント形式とMinIO Webhookの形式には以下の違いがあります：
    - AWS S3: eventName = "ObjectCreated:Put"
    - MinIO:  eventName = "s3:ObjectCreated:Put"

    この関数でeventNameに`s3:`プレフィックスを追加して、
    既存のWebhookFileWatcherServiceで処理できる形式に変換します。

    Args:
        s3_event: AWS S3 Lambdaトリガーから受け取るイベント

    Returns:
        WebhookFileWatcherService用に変換されたイベント

    Example:
        入力（AWS S3形式）:
        {
            "Records": [{
                "eventName": "ObjectCreated:Put",
                "s3": {
                    "bucket": {"name": "my-bucket"},
                    "object": {"key": "path/to/file.yml", "eTag": "abc123", "size": 1024}
                }
            }]
        }

        出力（MinIO互換形式）:
        {
            "Records": [{
                "eventName": "s3:ObjectCreated:Put",  # プレフィックス追加
                "s3": {...}
            }]
        }
    """
    if "Records" not in s3_event:
        logger.warning("S3イベントにRecordsフィールドがありません")
        return s3_event

    converted_records = []
    for record in s3_event["Records"]:
        converted_record = record.copy()

        # eventNameに`s3:`プレフィックスを追加（既に存在する場合はスキップ）
        event_name = record.get("eventName", "")
        if event_name and not event_name.startswith("s3:"):
            converted_record["eventName"] = f"s3:{event_name}"
            logger.debug(f"eventName変換: {event_name} -> s3:{event_name}")

        converted_records.append(converted_record)

    return {"Records": converted_records}


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """AWS Lambda関数のエントリーポイント

    S3イベントトリガーからの通知を受け取り、WebhookFileWatcherServiceを使用して
    メンバー登録処理を実行します。

    Args:
        event: S3イベントトリガーからのイベントデータ
            {
                "Records": [{
                    "eventVersion": "2.1",
                    "eventSource": "aws:s3",
                    "awsRegion": "ap-northeast-1",
                    "eventTime": "2024-01-01T00:00:00.000Z",
                    "eventName": "ObjectCreated:Put",
                    "s3": {
                        "bucket": {"name": "bucket-name"},
                        "object": {
                            "key": "data/samples/human_members/member.yml",
                            "size": 1234,
                            "eTag": "abc123"
                        }
                    }
                }]
            }
        context: Lambda実行コンテキスト（AWS Lambda runtime提供）

    Returns:
        処理結果を含むレスポンス
            {
                "statusCode": 200 or 400 or 500,
                "body": {
                    "success": bool,
                    "message": str,
                    "processed_files": list[str],
                    "errors": list[str]
                }
            }
    """
    logger.info("Lambda関数開始")
    logger.info(f"受信イベント: {json.dumps(event, ensure_ascii=False)}")

    try:
        # S3イベントをWebhook形式に変換
        webhook_payload = convert_s3_event_to_webhook_format(event)
        logger.info(
            f"変換後ペイロード: {json.dumps(webhook_payload, ensure_ascii=False)}"
        )

        # WebhookFileWatcherServiceを初期化して処理実行
        webhook_watcher = WebhookFileWatcherService()
        result = webhook_watcher.handle_webhook(webhook_payload)

        # レスポンス構築
        status_code = 200 if result.success else 400
        response_body = {
            "success": result.success,
            "message": result.message,
            "processed_files": result.processed_files,
            "errors": result.errors,
        }

        logger.info(f"処理完了: success={result.success}, message={result.message}")

        return {
            "statusCode": status_code,
            "body": json.dumps(response_body, ensure_ascii=False),
        }

    except Exception as e:
        logger.error(f"Lambda関数でエラー発生: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "success": False,
                    "message": f"内部エラー: {str(e)}",
                    "processed_files": [],
                    "errors": [str(e)],
                },
                ensure_ascii=False,
            ),
        }
