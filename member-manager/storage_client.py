#!/usr/bin/env python3
"""
ストレージサービスクライアント
MinIOストレージサービスへのファイルアップロード機能を提供
"""

import logging
import os
from typing import Any
from urllib.parse import urljoin

import boto3
import requests
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class StorageClient:
    """MinIOストレージサービスとの通信を行うクライアントクラス

    YAMLファイルのアップロードとMinIOとの基本的な通信機能を提供します。
    """

    def __init__(self):
        """ストレージクライアントの初期化"""
        self.storage_host = os.getenv("STORAGE_HOST", "storage")
        self.storage_port = os.getenv("STORAGE_PORT", "9000")
        self.base_url = f"http://{self.storage_host}:{self.storage_port}"

        # MinIO認証情報
        self.minio_user = os.getenv("MINIO_ROOT_USER")
        self.minio_password = os.getenv("MINIO_ROOT_PASSWORD")
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME")

        # boto3 S3クライアントの初期化
        self.s3_client = self._initialize_s3_client()

        logger.info(f"Storage client initialized: {self.base_url}")
        logger.info(f"MinIO bucket: {self.bucket_name}")

    def _initialize_s3_client(self):
        """boto3 S3クライアントを初期化

        Returns:
            boto3.client: S3クライアント
        """
        try:
            # MinIOのS3互換エンドポイントを設定
            endpoint_url = f"http://{self.storage_host}:{self.storage_port}"

            # boto3 S3クライアントを作成
            s3_client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=self.minio_user,
                aws_secret_access_key=self.minio_password,
                region_name="us-east-1",  # MinIOでは任意のリージョンでOK
                use_ssl=False,  # ローカル開発環境ではSSL無効
            )

            logger.info(f"S3 client initialized for MinIO: {endpoint_url}")
            return s3_client

        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            raise Exception(f"S3 client initialization failed: {str(e)}")

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
                    raise Exception(error_msg)
            else:
                # その他のエラー（認証エラーなど）
                error_msg = f"Failed to check bucket '{self.bucket_name}': {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)

    def upload_yaml_file(self, yaml_content: str, storage_path: str) -> dict[str, Any]:
        """YAMLファイルをMinIOストレージにアップロード

        Args:
            yaml_content (str): アップロードするYAMLの内容
            storage_path (str): ストレージ内のパス

        Returns:
            Dict[str, Any]: アップロード結果

        Raises:
            Exception: アップロードに失敗した場合
        """
        try:
            logger.info(f"Attempting to upload YAML to MinIO: {storage_path}")

            # バケットの存在確認と作成
            self._ensure_bucket_exists()

            # YAMLコンテンツをバイトに変換
            yaml_bytes = yaml_content.encode("utf-8")

            # MinIOにファイルをアップロード
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=storage_path,
                Body=yaml_bytes,
                ContentType="application/x-yaml",
                ContentDisposition=f'attachment; filename="{os.path.basename(storage_path)}"',
            )

            result = {
                "success": True,
                "message": "YAML file uploaded successfully to MinIO",
                "storage_path": storage_path,
                "bucket_name": self.bucket_name,
                "file_size": len(yaml_bytes),
                "upload_timestamp": self._get_current_timestamp(),
            }

            logger.info(f"YAML uploaded successfully to MinIO: {storage_path}")
            return result

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = f"MinIO upload failed ({error_code}): {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except NoCredentialsError as e:
            error_msg = f"MinIO credentials not found: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Failed to upload YAML to {storage_path}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def test_connection(self) -> bool:
        """ストレージサービスへの接続テスト

        Returns:
            bool: 接続成功の場合True
        """
        try:
            health_url = urljoin(self.base_url, "/minio/health/live")
            response = requests.get(health_url, timeout=10)

            if response.status_code == 200:
                logger.info("Storage service connection test successful")
                return True
            else:
                logger.warning(
                    f"Storage service returned status: {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"Storage service connection test failed: {str(e)}")
            return False

    def get_storage_info(self) -> dict[str, Any]:
        """ストレージサービスの情報を取得

        Returns:
            Dict[str, Any]: ストレージ情報
        """
        return {
            "host": self.storage_host,
            "port": self.storage_port,
            "base_url": self.base_url,
            "auth_configured": bool(self.minio_user and self.minio_password),
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
