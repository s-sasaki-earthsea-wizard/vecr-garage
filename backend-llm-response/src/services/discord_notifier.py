"""
Discord Webhook通知サービス

Discord Webhookを使用してメッセージを送信するサービスクラス
複数のWebhookを辞書形式で管理
"""

import logging
from datetime import datetime
from typing import Any, Optional

import requests

from config.webhook import WebhookConfigParser

# ロガー設定
logger = logging.getLogger(__name__)


class DiscordNotifier:
    """Discord Webhook通知クラス（複数Webhook対応）"""

    def __init__(self, webhooks_config: Optional[str] = None):
        """
        初期化

        Args:
            webhooks_config: Discord Webhooks設定（JSON文字列、辞書、またはNone）
                           - None: 環境変数DISCORD_WEBHOOKSからJSON文字列を取得
                           - str: JSON文字列
                           - dict: 設定辞書

        Raises:
            ValueError: 設定の読み込み、パース、バリデーションに失敗した場合
        """
        # パーサーを使用して設定を取得
        if webhooks_config is None:
            # 環境変数からJSON文字列を取得
            self.webhooks = WebhookConfigParser.parse_from_env()
        elif isinstance(webhooks_config, str):
            # JSON文字列としてパース
            self.webhooks = WebhookConfigParser.parse_from_string(webhooks_config)
        elif isinstance(webhooks_config, dict):
            # 辞書からバリデーション
            self.webhooks = WebhookConfigParser.parse_from_dict(webhooks_config)
        else:
            raise ValueError(
                f"webhooks_configはJSON文字列、辞書、またはNoneである必要があります "
                f"（現在: {type(webhooks_config).__name__}）"
            )

        logger.info(
            f"Discord Notifier初期化完了: {len(self.webhooks)}個のWebhook登録済み"
        )
        logger.debug(f"登録Webhook: {list(self.webhooks.keys())}")

    def get_webhook_url(self, webhook_name: str) -> str:
        """
        Webhook名からURLを取得

        Args:
            webhook_name: Webhook名

        Returns:
            Webhook URL

        Raises:
            KeyError: 指定されたWebhook名が存在しない場合
        """
        return WebhookConfigParser.get_webhook_url(self.webhooks, webhook_name)

    def list_webhooks(self) -> list[str]:
        """
        登録されているWebhook名のリストを取得

        Returns:
            Webhook名のリスト
        """
        return list(self.webhooks.keys())

    def send_message(
        self,
        webhook_name: str,
        content: str,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        指定されたWebhookにメッセージを送信

        Args:
            webhook_name: 送信先Webhook名
            content: 送信するメッセージ内容
            username: 表示するユーザー名（オプション）
            avatar_url: アバター画像URL（オプション）

        Returns:
            送信結果を含む辞書
            - success: 送信成功フラグ
            - webhook_name: 使用したWebhook名
            - status_code: HTTPステータスコード
            - message: 結果メッセージ
        """
        try:
            webhook_url = self.get_webhook_url(webhook_name)
        except KeyError as e:
            logger.error(str(e))
            return {
                "success": False,
                "webhook_name": webhook_name,
                "status_code": 404,
                "message": str(e),
            }

        payload = {"content": content}

        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info(
                f"Discordへのメッセージ送信成功 " f"[{webhook_name}]: {content[:50]}..."
            )

            return {
                "success": True,
                "webhook_name": webhook_name,
                "status_code": response.status_code,
                "message": "メッセージ送信成功",
            }

        except requests.exceptions.Timeout:
            error_msg = f"Discord Webhook送信タイムアウト [{webhook_name}]"
            logger.error(error_msg)
            return {
                "success": False,
                "webhook_name": webhook_name,
                "status_code": 408,
                "message": error_msg,
            }

        except requests.exceptions.HTTPError as e:
            error_msg = (
                f"Discord Webhook HTTPエラー [{webhook_name}]: "
                f"{e.response.status_code}"
            )
            logger.error(f"{error_msg} - {e.response.text}")
            return {
                "success": False,
                "webhook_name": webhook_name,
                "status_code": e.response.status_code,
                "message": error_msg,
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"Discord Webhook送信エラー [{webhook_name}]: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "webhook_name": webhook_name,
                "status_code": 500,
                "message": error_msg,
            }

    def broadcast_message(
        self,
        content: str,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
        webhook_names: Optional[list[str]] = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        複数のWebhookに同時配信

        Args:
            content: 送信するメッセージ内容
            username: 表示するユーザー名（オプション）
            avatar_url: アバター画像URL（オプション）
            webhook_names: 送信先Webhook名のリスト（未指定時は全Webhook）

        Returns:
            送信結果を含む辞書
            - results: 各Webhookの送信結果リスト
        """
        target_webhooks = webhook_names or self.list_webhooks()
        results = []

        for webhook_name in target_webhooks:
            result = self.send_message(
                webhook_name=webhook_name,
                content=content,
                username=username,
                avatar_url=avatar_url,
            )
            results.append(result)

        success_count = sum(1 for r in results if r["success"])
        logger.info(f"ブロードキャスト完了: {success_count}/{len(results)}件成功")

        return {"results": results}

    def send_test_message(self, webhook_name: str) -> dict[str, Any]:
        """
        指定されたWebhookにテストメッセージを送信

        Args:
            webhook_name: 送信先Webhook名

        Returns:
            送信結果を含む辞書
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_message = (
            f"🤖 **VECR Garage システムテスト**\n"
            f"Webhook: `{webhook_name}`\n"
            f"送信時刻: {timestamp}"
        )

        return self.send_message(
            webhook_name=webhook_name, content=test_message, username="VECR Garage Bot"
        )

    def send_member_notification(
        self, webhook_name: str, member_name: str, message: str
    ) -> dict[str, Any]:
        """
        メンバー通知を送信

        Args:
            webhook_name: 送信先Webhook名
            member_name: メンバー名
            message: 通知メッセージ

        Returns:
            送信結果を含む辞書
        """
        notification = f"📢 **{member_name}** からのメッセージ:\n{message}"

        return self.send_message(
            webhook_name=webhook_name, content=notification, username=member_name
        )
