#!/usr/bin/env python3
"""
Lambda関数エントリーポイントのユニットテスト

convert_s3_event_to_webhook_format関数とhandler関数のテストを行います。
"""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestConvertS3EventToWebhookFormat:
    """S3イベント変換関数のテスト"""

    def test_converts_event_name_with_s3_prefix(self):
        """eventNameにs3:プレフィックスが追加されることを確認"""
        from lambda_handler import convert_s3_event_to_webhook_format

        s3_event = {
            "Records": [
                {
                    "eventName": "ObjectCreated:Put",
                    "s3": {
                        "bucket": {"name": "test-bucket"},
                        "object": {"key": "test.yml", "eTag": "abc123", "size": 100},
                    },
                }
            ]
        }

        result = convert_s3_event_to_webhook_format(s3_event)

        assert result["Records"][0]["eventName"] == "s3:ObjectCreated:Put"

    def test_preserves_existing_s3_prefix(self):
        """既にs3:プレフィックスがある場合は変更されないことを確認"""
        from lambda_handler import convert_s3_event_to_webhook_format

        s3_event = {
            "Records": [
                {
                    "eventName": "s3:ObjectCreated:Put",
                    "s3": {
                        "bucket": {"name": "test-bucket"},
                        "object": {"key": "test.yml", "eTag": "abc123", "size": 100},
                    },
                }
            ]
        }

        result = convert_s3_event_to_webhook_format(s3_event)

        assert result["Records"][0]["eventName"] == "s3:ObjectCreated:Put"

    def test_handles_multiple_records(self):
        """複数レコードが正しく変換されることを確認"""
        from lambda_handler import convert_s3_event_to_webhook_format

        s3_event = {
            "Records": [
                {
                    "eventName": "ObjectCreated:Put",
                    "s3": {"bucket": {"name": "b1"}, "object": {"key": "f1.yml"}},
                },
                {
                    "eventName": "ObjectCreated:Copy",
                    "s3": {"bucket": {"name": "b1"}, "object": {"key": "f2.yml"}},
                },
            ]
        }

        result = convert_s3_event_to_webhook_format(s3_event)

        assert result["Records"][0]["eventName"] == "s3:ObjectCreated:Put"
        assert result["Records"][1]["eventName"] == "s3:ObjectCreated:Copy"

    def test_handles_missing_records_field(self):
        """Recordsフィールドがない場合は元のイベントを返すことを確認"""
        from lambda_handler import convert_s3_event_to_webhook_format

        s3_event = {"invalid": "event"}

        result = convert_s3_event_to_webhook_format(s3_event)

        assert result == s3_event

    def test_preserves_other_fields(self):
        """eventName以外のフィールドが保持されることを確認"""
        from lambda_handler import convert_s3_event_to_webhook_format

        s3_event = {
            "Records": [
                {
                    "eventVersion": "2.1",
                    "eventSource": "aws:s3",
                    "awsRegion": "ap-northeast-1",
                    "eventTime": "2024-01-01T00:00:00.000Z",
                    "eventName": "ObjectCreated:Put",
                    "s3": {
                        "bucket": {"name": "test-bucket"},
                        "object": {"key": "test.yml", "eTag": "abc123", "size": 100},
                    },
                }
            ]
        }

        result = convert_s3_event_to_webhook_format(s3_event)

        record = result["Records"][0]
        assert record["eventVersion"] == "2.1"
        assert record["eventSource"] == "aws:s3"
        assert record["awsRegion"] == "ap-northeast-1"
        assert record["s3"]["bucket"]["name"] == "test-bucket"
        assert record["s3"]["object"]["key"] == "test.yml"


class TestLambdaHandler:
    """Lambda handler関数のテスト"""

    @patch("lambda_handler.WebhookFileWatcherService")
    def test_handler_success(self, mock_service_class):
        """正常処理時に200レスポンスを返すことを確認"""
        from lambda_handler import handler

        # モックの設定
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.message = "処理完了"
        mock_result.processed_files = ["test.yml"]
        mock_result.errors = []

        mock_service = MagicMock()
        mock_service.handle_webhook.return_value = mock_result
        mock_service_class.return_value = mock_service

        event = {
            "Records": [
                {
                    "eventName": "ObjectCreated:Put",
                    "s3": {
                        "bucket": {"name": "test-bucket"},
                        "object": {"key": "test.yml", "eTag": "abc123", "size": 100},
                    },
                }
            ]
        }

        response = handler(event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["success"] is True
        assert body["message"] == "処理完了"
        assert body["processed_files"] == ["test.yml"]

    @patch("lambda_handler.WebhookFileWatcherService")
    def test_handler_failure(self, mock_service_class):
        """処理失敗時に400レスポンスを返すことを確認"""
        from lambda_handler import handler

        # モックの設定
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.message = "処理に失敗しました"
        mock_result.processed_files = []
        mock_result.errors = ["エラー詳細"]

        mock_service = MagicMock()
        mock_service.handle_webhook.return_value = mock_result
        mock_service_class.return_value = mock_service

        event = {"Records": [{"eventName": "ObjectCreated:Put", "s3": {}}]}

        response = handler(event, None)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["success"] is False
        assert "エラー詳細" in body["errors"]

    @patch("lambda_handler.WebhookFileWatcherService")
    def test_handler_exception(self, mock_service_class):
        """例外発生時に500レスポンスを返すことを確認"""
        from lambda_handler import handler

        # モックの設定
        mock_service = MagicMock()
        mock_service.handle_webhook.side_effect = Exception("テスト例外")
        mock_service_class.return_value = mock_service

        event = {"Records": [{"eventName": "ObjectCreated:Put", "s3": {}}]}

        response = handler(event, None)

        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert body["success"] is False
        assert "テスト例外" in body["message"]

    @patch("lambda_handler.WebhookFileWatcherService")
    def test_handler_converts_event_format(self, mock_service_class):
        """handlerがイベント形式を変換していることを確認"""
        from lambda_handler import handler

        # モックの設定
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.message = "OK"
        mock_result.processed_files = []
        mock_result.errors = []

        mock_service = MagicMock()
        mock_service.handle_webhook.return_value = mock_result
        mock_service_class.return_value = mock_service

        event = {
            "Records": [
                {
                    "eventName": "ObjectCreated:Put",
                    "s3": {"bucket": {"name": "b"}, "object": {"key": "k"}},
                }
            ]
        }

        handler(event, None)

        # handle_webhookに渡されたペイロードを確認
        call_args = mock_service.handle_webhook.call_args[0][0]
        assert call_args["Records"][0]["eventName"] == "s3:ObjectCreated:Put"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
