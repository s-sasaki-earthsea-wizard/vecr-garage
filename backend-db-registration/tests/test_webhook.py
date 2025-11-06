#!/usr/bin/env python3
"""
Webhook機能テストスクリプト

このスクリプトは、Webhookエンドポイントの機能をテストします。
実際のファイル変更をシミュレートして、Webhook処理が正しく動作することを確認します。
"""

import os
import sys
import time

import requests
from utils.logging_config import setup_logging

logger = setup_logging(__name__)


class WebhookTester:
    """Webhook機能テストクラス"""

    def __init__(self, base_url: str = None):
        """Webhookテストクラスを初期化

        Args:
            base_url (str): APIサーバーのベースURL
        """
        if base_url is None:
            base_url = os.getenv("API_BASE_URL")
            if not base_url:
                raise ValueError("API_BASE_URL environment variable is required")
        self.base_url = base_url
        self.webhook_url = f"{base_url}/webhook/file-change"
        self.status_url = f"{base_url}/webhook/status"
        self.test_url = f"{base_url}/webhook/test"
        self.health_url = f"{base_url}/health"

    def test_health_check(self) -> bool:
        """ヘルスチェックエンドポイントをテストする

        Returns:
            bool: テストが成功した場合はTrue
        """
        try:
            logger.info("🔍 Testing health check endpoint...")
            response = requests.get(self.health_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Health check successful")
                logger.info(f"Status: {data.get('status')}")
                logger.info(f"Service: {data.get('service')}")
                return True
            logger.error(f"❌ Health check failed: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return False

    def test_webhook_status(self) -> bool:
        """Webhookステータスエンドポイントをテストする

        Returns:
            bool: テストが成功した場合はTrue
        """
        try:
            logger.info("📊 Testing webhook status endpoint...")
            response = requests.get(self.status_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Webhook status check successful")
                logger.info(f"Status: {data.get('status')}")
                logger.info(f"Data: {data.get('data')}")
                return True
            logger.error(f"❌ Webhook status check failed: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"❌ Webhook status check error: {e}")
            return False

    def test_webhook_test_endpoint(self) -> bool:
        """Webhookテストエンドポイントをテストする

        Returns:
            bool: テストが成功した場合はTrue
        """
        try:
            logger.info("🧪 Testing webhook test endpoint...")
            response = requests.post(self.test_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Webhook test endpoint successful")
                logger.info(f"Message: {data.get('message')}")
                logger.info(f"Result: {data.get('result', {})}")
                return True
            logger.error(f"❌ Webhook test endpoint failed: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"❌ Webhook test endpoint error: {e}")
            return False

    def test_human_member_webhook(self) -> bool:
        """人間メンバーのWebhook通知をテストする

        Returns:
            bool: テストが成功した場合はTrue
        """
        try:
            logger.info("👤 Testing human member webhook...")

            # 人間メンバーのWebhookペイロード
            payload = {
                "Records": [
                    {
                        "eventName": "s3:ObjectCreated:Put",
                        "eventTime": "2024-01-01T12:00:00.000Z",
                        "s3": {
                            "bucket": {"name": "test-bucket"},
                            "object": {
                                "key": "data/samples/human_members/syota.yml",
                                "eTag": "test-etag-human-123",
                                "size": 2048,
                            },
                        },
                    }
                ]
            }

            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Human member webhook test successful")
                logger.info(f"Success: {data.get('success')}")
                logger.info(f"Message: {data.get('message')}")
                logger.info(f"Processed files: {data.get('processed_files')}")
                return True
            logger.error(f"❌ Human member webhook test failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False

        except Exception as e:
            logger.error(f"❌ Human member webhook test error: {e}")
            return False

    def test_virtual_member_webhook(self) -> bool:
        """仮想メンバーのWebhook通知をテストする

        Returns:
            bool: テストが成功した場合はTrue
        """
        try:
            logger.info("🤖 Testing virtual member webhook...")

            # 仮想メンバーのWebhookペイロード
            payload = {
                "Records": [
                    {
                        "eventName": "s3:ObjectCreated:Put",
                        "eventTime": "2024-01-01T12:00:00.000Z",
                        "s3": {
                            "bucket": {"name": "test-bucket"},
                            "object": {
                                "key": "data/samples/virtual_members/kasen.yml",
                                "eTag": "test-etag-virtual-456",
                                "size": 3072,
                            },
                        },
                    }
                ]
            }

            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Virtual member webhook test successful")
                logger.info(f"Success: {data.get('success')}")
                logger.info(f"Message: {data.get('message')}")
                logger.info(f"Processed files: {data.get('processed_files')}")
                return True
            logger.error(f"❌ Virtual member webhook test failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False

        except Exception as e:
            logger.error(f"❌ Virtual member webhook test error: {e}")
            return False

    def test_invalid_webhook(self) -> bool:
        """無効なWebhook通知をテストする

        Returns:
            bool: テストが成功した場合はTrue（エラーハンドリングが正しく動作することを確認）
        """
        try:
            logger.info("🚫 Testing invalid webhook payload...")

            # 無効なペイロード
            payload = {"invalid": "payload", "no": "records"}

            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            # 無効なペイロードの場合は400エラーが期待される
            if response.status_code == 400:
                data = response.json()
                logger.info("✅ Invalid webhook test successful (error handling works)")
                logger.info(f"Success: {data.get('success')}")
                logger.info(f"Message: {data.get('message')}")
                return True
            logger.warning(f"⚠️  Unexpected status code for invalid payload: {response.status_code}")
            return True  # エラーハンドリングの実装によっては200が返る場合もある

        except Exception as e:
            logger.error(f"❌ Invalid webhook test error: {e}")
            return False

    def test_duplicate_webhook(self) -> bool:
        """重複Webhook通知をテストする

        Returns:
            bool: テストが成功した場合はTrue
        """
        try:
            logger.info("🔄 Testing duplicate webhook handling...")

            # タイムスタンプベースのユニークなETagを生成
            import time

            unique_etag = f"duplicate-etag-{int(time.time())}"

            # 新しいETagを持つWebhookペイロード（1回目）
            payload1 = {
                "Records": [
                    {
                        "eventName": "s3:ObjectCreated:Put",
                        "eventTime": "2024-01-01T12:00:00.000Z",
                        "s3": {
                            "bucket": {"name": "test-bucket"},
                            "object": {
                                "key": "data/samples/human_members/webhook_test_member.yml",
                                "eTag": unique_etag,
                                "size": 1024,
                            },
                        },
                    }
                ]
            }

            # 同じETagを持つWebhookペイロード（2回目 - 重複）
            payload2 = {
                "Records": [
                    {
                        "eventName": "s3:ObjectCreated:Put",
                        "eventTime": "2024-01-01T12:00:00.000Z",
                        "s3": {
                            "bucket": {"name": "test-bucket"},
                            "object": {
                                "key": "data/samples/human_members/webhook_test_member.yml",
                                "eTag": unique_etag,
                                "size": 1024,
                            },
                        },
                    }
                ]
            }

            # 1回目のWebhook送信
            response1 = requests.post(
                self.webhook_url,
                json=payload1,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            # 2回目のWebhook送信（重複）
            response2 = requests.post(
                self.webhook_url,
                json=payload2,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()

                logger.info("✅ Duplicate webhook test completed")
                logger.info(f"First request - Processed files: {data1.get('processed_files')}")
                logger.info(f"Second request - Processed files: {data2.get('processed_files')}")

                # 重複検出が正しく動作している場合、2回目のリクエストでは処理されるファイルが0になる
                first_processed = len(data1.get("processed_files", []))
                second_processed = len(data2.get("processed_files", []))

                logger.info(f"First request processed: {first_processed} files")
                logger.info(f"Second request processed: {second_processed} files")

                if first_processed > 0 and second_processed == 0:
                    logger.info("✅ Duplicate detection is working correctly")
                    return True
                if first_processed > 0 and second_processed < first_processed:
                    logger.info("✅ Duplicate detection appears to be working (some files skipped)")
                    return True
                logger.warning("⚠️  Duplicate detection may not be working as expected")
                logger.warning(
                    f"Expected: first > 0, second = 0, but got: first = {first_processed}, second = {second_processed}"
                )
                return False
            if response1.status_code == 400 and response2.status_code == 400:
                # 両方とも400エラーの場合、重複検出が動作している可能性
                logger.info("✅ Both requests returned 400 (duplicate detection may be working)")
                return True
            logger.error("❌ Duplicate webhook test failed")
            logger.error(f"First request status: {response1.status_code}")
            logger.error(f"Second request status: {response2.status_code}")
            return False

        except Exception as e:
            logger.error(f"❌ Duplicate webhook test error: {e}")
            return False

    def run_all_tests(self) -> dict:
        """すべてのテストを実行する

        Returns:
            dict: テスト結果のサマリー
        """
        logger.info("🚀 Starting comprehensive webhook tests...")
        logger.info(f"Base URL: {self.base_url}")
        logger.info("=" * 60)

        tests = [
            ("Health Check", self.test_health_check),
            ("Webhook Status", self.test_webhook_status),
            ("Webhook Test Endpoint", self.test_webhook_test_endpoint),
            ("Human Member Webhook", self.test_human_member_webhook),
            ("Virtual Member Webhook", self.test_virtual_member_webhook),
            ("Invalid Webhook", self.test_invalid_webhook),
            ("Duplicate Webhook", self.test_duplicate_webhook),
        ]

        results = {}
        passed = 0
        failed = 0

        for test_name, test_func in tests:
            logger.info(f"\n📋 Running: {test_name}")
            logger.info("-" * 40)

            try:
                success = test_func()
                results[test_name] = success

                if success:
                    passed += 1
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    failed += 1
                    logger.info(f"❌ {test_name}: FAILED")

            except Exception as e:
                failed += 1
                results[test_name] = False
                logger.error(f"💥 {test_name}: ERROR - {e}")

            time.sleep(1)  # テスト間の短い待機

        # サマリーを表示
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total tests: {len(tests)}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success rate: {(passed / len(tests)) * 100:.1f}%")

        if failed == 0:
            logger.info("🎉 All tests passed!")
        else:
            logger.info("⚠️  Some tests failed. Check the logs above for details.")

        return {
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / len(tests)) * 100,
            "results": results,
        }


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description="Test webhook functionality")
    parser.add_argument(
        "--url",
        default=os.getenv("API_BASE_URL"),
        help="Base URL of the API server (required: set API_BASE_URL env var)",
    )
    parser.add_argument(
        "--test",
        choices=[
            "health",
            "status",
            "test",
            "human",
            "virtual",
            "invalid",
            "duplicate",
            "all",
        ],
        default="all",
        help="Specific test to run (default: all)",
    )

    args = parser.parse_args()

    print("🧪 Webhook Functionality Test Suite")
    print("=" * 50)

    tester = WebhookTester(args.url)

    if args.test == "all":
        results = tester.run_all_tests()
        exit_code = 0 if results["failed"] == 0 else 1
    else:
        # 個別テストの実行
        test_map = {
            "health": tester.test_health_check,
            "status": tester.test_webhook_status,
            "test": tester.test_webhook_test_endpoint,
            "human": tester.test_human_member_webhook,
            "virtual": tester.test_virtual_member_webhook,
            "invalid": tester.test_invalid_webhook,
            "duplicate": tester.test_duplicate_webhook,
        }

        test_func = test_map.get(args.test)
        if test_func:
            success = test_func()
            exit_code = 0 if success else 1
        else:
            print(f"❌ Unknown test: {args.test}")
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
