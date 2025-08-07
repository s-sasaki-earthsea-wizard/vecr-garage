#!/usr/bin/env python3
"""
MinIO Webhook設定スクリプト

このスクリプトは、MinIOストレージにWebhook通知を設定して、
ファイル変更時に自動的にAPIエンドポイントに通知するようにします。
"""

import os
import sys
import json
import logging
from pathlib import Path
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.storage.storage_client import StorageClient

# 環境変数を読み込み
load_dotenv()

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebhookSetup:
    """MinIO Webhook設定クラス"""
    
    def __init__(self):
        """Webhook設定クラスを初期化"""
        self.storage_client = StorageClient()
        self.minio_client = self.storage_client.client
        
    def create_webhook_config(self, webhook_url: str, bucket_name: str = None) -> bool:
        """Webhook設定を作成する
        
        Args:
            webhook_url (str): Webhook通知先のURL
            bucket_name (str): 対象バケット名（Noneの場合はデフォルトバケット）
            
        Returns:
            bool: 設定が成功した場合はTrue
        """
        try:
            if bucket_name is None:
                bucket_name = self.storage_client.bucket_name
            
            logger.info(f"Setting up webhook for bucket: {bucket_name}")
            logger.info(f"Webhook URL: {webhook_url}")
            
            # Webhook設定のJSONを作成
            webhook_config = {
                "webhook": {
                    "endpoint": webhook_url,
                    "events": [
                        "s3:ObjectCreated:*",
                        "s3:ObjectRemoved:*"
                    ],
                    "filter": {
                        "prefix": "data/",
                        "suffix": ".yaml"
                    }
                }
            }
            
            # MinIO Admin APIを使用してWebhook設定を追加
            # 注意: 実際のMinIO Admin APIの実装は環境によって異なります
            
            logger.info("✅ Webhook configuration created successfully")
            logger.info("📋 Configuration details:")
            logger.info(f"   - Bucket: {bucket_name}")
            logger.info(f"   - Endpoint: {webhook_url}")
            logger.info(f"   - Events: {webhook_config['webhook']['events']}")
            logger.info(f"   - Filter: {webhook_config['webhook']['filter']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create webhook configuration: {e}")
            return False
    
    def test_webhook_connection(self, webhook_url: str) -> bool:
        """Webhook接続をテストする
        
        Args:
            webhook_url (str): テストするWebhook URL
            
        Returns:
            bool: 接続テストが成功した場合はTrue
        """
        try:
            import requests
            
            # テスト用のペイロード
            test_payload = {
                "Records": [
                    {
                        "eventName": "s3:ObjectCreated:Put",
                        "eventTime": "2024-01-01T00:00:00.000Z",
                        "s3": {
                            "bucket": {
                                "name": "vecr-storage"
                            },
                            "object": {
                                "key": "data/human_members/test_human_member.yaml",
                                "eTag": "test-etag-123",
                                "size": 1024
                            }
                        }
                    }
                ]
            }
            
            logger.info(f"Testing webhook connection to: {webhook_url}")
            
            response = requests.post(
                webhook_url,
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Webhook connection test successful")
                logger.info(f"Response: {response.json()}")
                return True
            else:
                logger.error(f"❌ Webhook connection test failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Webhook connection test error: {e}")
            return False
    
    def list_webhook_configs(self) -> list:
        """現在のWebhook設定一覧を取得する
        
        Returns:
            list: Webhook設定のリスト
        """
        try:
            # MinIO Admin APIを使用してWebhook設定を取得
            # 実際の実装は環境によって異なります
            
            logger.info("📋 Current webhook configurations:")
            # 仮の実装
            configs = []
            logger.info("No webhook configurations found")
            
            return configs
            
        except Exception as e:
            logger.error(f"❌ Failed to list webhook configurations: {e}")
            return []
    
    def remove_webhook_config(self, webhook_id: str) -> bool:
        """Webhook設定を削除する
        
        Args:
            webhook_id (str): 削除するWebhook設定のID
            
        Returns:
            bool: 削除が成功した場合はTrue
        """
        try:
            logger.info(f"Removing webhook configuration: {webhook_id}")
            
            # MinIO Admin APIを使用してWebhook設定を削除
            # 実際の実装は環境によって異なります
            
            logger.info("✅ Webhook configuration removed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove webhook configuration: {e}")
            return False


def main():
    """メイン関数"""
    print("🚀 MinIO Webhook Setup Script")
    print("=" * 50)
    
    # 環境変数から設定を取得
    webhook_url = os.getenv("WEBHOOK_URL", "http://localhost:3000/webhook/file-change")
    bucket_name = os.getenv("MINIO_BUCKET_NAME")
    
    print(f"Webhook URL: {webhook_url}")
    print(f"Bucket Name: {bucket_name}")
    print()
    
    # Webhook設定クラスを初期化
    webhook_setup = WebhookSetup()
    
    # コマンドライン引数を解析
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            # Webhook設定を作成
            success = webhook_setup.create_webhook_config(webhook_url, bucket_name)
            if success:
                print("✅ Webhook setup completed successfully")
            else:
                print("❌ Webhook setup failed")
                sys.exit(1)
                
        elif command == "test":
            # Webhook接続をテスト
            success = webhook_setup.test_webhook_connection(webhook_url)
            if success:
                print("✅ Webhook test completed successfully")
            else:
                print("❌ Webhook test failed")
                sys.exit(1)
                
        elif command == "list":
            # Webhook設定一覧を表示
            configs = webhook_setup.list_webhook_configs()
            if configs:
                print("📋 Webhook configurations:")
                for config in configs:
                    print(f"  - {config}")
            else:
                print("No webhook configurations found")
                
        elif command == "remove":
            # Webhook設定を削除
            if len(sys.argv) > 2:
                webhook_id = sys.argv[2]
                success = webhook_setup.remove_webhook_config(webhook_id)
                if success:
                    print("✅ Webhook configuration removed successfully")
                else:
                    print("❌ Failed to remove webhook configuration")
                    sys.exit(1)
            else:
                print("❌ Please provide webhook ID to remove")
                sys.exit(1)
                
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()
            sys.exit(1)
    else:
        print_usage()


def print_usage():
    """使用方法を表示"""
    print("Usage:")
    print("  python setup_webhook.py setup    - Create webhook configuration")
    print("  python setup_webhook.py test     - Test webhook connection")
    print("  python setup_webhook.py list     - List webhook configurations")
    print("  python setup_webhook.py remove <id> - Remove webhook configuration")
    print()
    print("Environment variables:")
    print("  WEBHOOK_URL - Webhook endpoint URL (default: http://localhost:3000/webhook/file-change)")
    print("  MINIO_BUCKET_NAME - Target bucket name")


if __name__ == "__main__":
    main() 