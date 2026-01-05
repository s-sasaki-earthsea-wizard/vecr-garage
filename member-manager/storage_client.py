#!/usr/bin/env python3
"""
ストレージサービスクライアント
MinIOストレージサービスへのファイルアップロード機能を提供
"""

import logging
import os
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class StorageClient:
    """AWS S3ストレージサービスとの通信を行うクライアントクラス

    YAMLファイルのアップロードとAWS S3との基本的な通信機能を提供します。
    """

    def __init__(self):
        """ストレージクライアントの初期化"""
        # 環境変数からS3設定を取得
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        aws_region = os.getenv("AWS_REGION", "ap-northeast-1")

        if not self.bucket_name:
            raise ValueError("環境変数 S3_BUCKET_NAME が設定されていません")

        # boto3 S3クライアントの初期化
        self.s3_client = self._initialize_s3_client(aws_region)

        logger.info("Storage client initialized for AWS S3")
        logger.info(f"S3 bucket: {self.bucket_name}")
        logger.info(f"AWS region: {aws_region}")

    def _initialize_s3_client(self, aws_region: str):
        """boto3 S3クライアントを初期化

        Args:
            aws_region: AWSリージョン

        Returns:
            boto3.client: S3クライアント
        """
        try:
            # boto3 S3クライアントを作成
            # AWS認証情報は~/.aws/credentialsまたは環境変数から自動取得
            s3_client = boto3.client(
                "s3",
                region_name=aws_region,
            )

            logger.info(f"S3 client initialized for AWS region: {aws_region}")
            return s3_client

        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            raise Exception(f"S3 client initialization failed: {str(e)}") from e

    def _ensure_bucket_exists(self):
        """バケットの存在確認と作成

        Raises:
            Exception: バケット作成に失敗した場合
        """
        try:
            # バケットの存在確認
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' already exists")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]

            if error_code == "404":
                # バケットが存在しない場合は作成
                logger.info(f"Bucket '{self.bucket_name}' not found, creating...")
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Bucket '{self.bucket_name}' created successfully")
                except ClientError as create_error:
                    error_msg = f"Failed to create bucket '{self.bucket_name}': {str(create_error)}"
                    logger.error(error_msg)
                    raise Exception(error_msg) from create_error
            else:
                # その他のエラー（認証エラーなど）
                error_msg = f"Failed to check bucket '{self.bucket_name}': {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg) from e

    def upload_yaml_file(self, yaml_content: str, storage_path: str) -> dict[str, Any]:
        """YAMLファイルをAWS S3ストレージにアップロード

        Args:
            yaml_content (str): アップロードするYAMLの内容
            storage_path (str): ストレージ内のパス

        Returns:
            Dict[str, Any]: アップロード結果

        Raises:
            Exception: アップロードに失敗した場合
        """
        try:
            logger.info(f"Attempting to upload YAML to AWS S3: {storage_path}")

            # バケットの存在確認と作成
            self._ensure_bucket_exists()

            # YAMLコンテンツをバイトに変換
            yaml_bytes = yaml_content.encode("utf-8")

            # AWS S3にファイルをアップロード
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=storage_path,
                Body=yaml_bytes,
                ContentType="application/x-yaml",
                ContentDisposition=f'attachment; filename="{Path(storage_path).name}"',
            )

            result = {
                "success": True,
                "message": "YAML file uploaded successfully to AWS S3",
                "storage_path": storage_path,
                "bucket_name": self.bucket_name,
                "file_size": len(yaml_bytes),
                "upload_timestamp": self._get_current_timestamp(),
            }

            logger.info(f"YAML uploaded successfully to AWS S3: {storage_path}")
            return result

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = f"AWS S3 upload failed ({error_code}): {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
        except NoCredentialsError as e:
            error_msg = f"AWS credentials not found: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to upload YAML to {storage_path}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e

    def test_connection(self) -> bool:
        """AWS S3への接続テスト

        Returns:
            bool: 接続成功の場合True
        """
        try:
            # バケットへのアクセス確認
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info("AWS S3 connection test successful")
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            logger.error(f"AWS S3 connection test failed ({error_code}): {str(e)}")
            return False
        except Exception as e:
            logger.error(f"AWS S3 connection test failed: {str(e)}")
            return False

    def get_storage_info(self) -> dict[str, Any]:
        """ストレージサービスの情報を取得

        Returns:
            Dict[str, Any]: ストレージ情報
        """
        aws_region = os.getenv("AWS_REGION", "ap-northeast-1")
        return {
            "service": "AWS S3",
            "bucket_name": self.bucket_name,
            "region": aws_region,
            "connection_status": self.test_connection(),
        }

    def _get_current_timestamp(self) -> str:
        """現在のタイムスタンプを取得

        Returns:
            str: ISO形式のタイムスタンプ
        """
        from datetime import datetime

        return datetime.now().isoformat()

    def validate_storage_path(self, storage_path: str) -> bool:
        """ストレージパスの妥当性を検証

        Args:
            storage_path (str): 検証するストレージパス

        Returns:
            bool: パスが妥当な場合True
        """
        # 基本的なパス検証
        if not storage_path or not isinstance(storage_path, str):
            return False

        # 危険な文字のチェック
        dangerous_chars = ["..", "~", "$", "`"]
        for char in dangerous_chars:
            if char in storage_path:
                return False

        # パスの長さチェック
        if len(storage_path) > 1000:
            return False

        return True
