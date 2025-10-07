"""
Webhook設定バリデーター

Webhook URLとデータ構造の妥当性を検証
"""
import re
from typing import Dict, Tuple
from urllib.parse import urlparse


class WebhookValidator:
    """Webhook設定バリデーションクラス"""

    # Discord Webhook URLの正規表現パターン
    DISCORD_WEBHOOK_PATTERN = re.compile(
        r'^https://discord\.com/api/webhooks/\d+/[\w-]+$'
    )

    @staticmethod
    def validate_discord_url(url: str) -> bool:
        """
        Discord Webhook URLの形式を検証

        Args:
            url: 検証するURL

        Returns:
            有効な場合True、無効な場合False
        """
        if not url or not isinstance(url, str):
            return False

        # 基本的なURL形式チェック
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return False
        except Exception:
            return False

        # Discord固有のパターンマッチ
        return bool(WebhookValidator.DISCORD_WEBHOOK_PATTERN.match(url))

    @staticmethod
    def validate_webhook_config(config: Dict[str, str]) -> Tuple[bool, str]:
        """
        Webhook設定辞書全体を検証

        Args:
            config: Webhook設定辞書 {"name": "url", ...}

        Returns:
            (検証結果, エラーメッセージ) のタプル
            検証成功時は (True, "")
        """
        # 辞書型チェック
        if not isinstance(config, dict):
            return False, f"設定は辞書型である必要があります（現在: {type(config).__name__}）"

        # 空チェック
        if not config:
            return False, "少なくとも1つのWebhookを設定する必要があります"

        # 各エントリーの検証
        for name, url in config.items():
            # キーの検証
            if not isinstance(name, str) or not name.strip():
                return False, f"Webhook名は空でない文字列である必要があります: {name}"

            # URLの検証
            if not isinstance(url, str):
                return False, f"Webhook URL '{name}' は文字列である必要があります"

            if not WebhookValidator.validate_discord_url(url):
                return False, (
                    f"無効なDiscord Webhook URL '{name}': {url}\n"
                    f"期待される形式: https://discord.com/api/webhooks/{{id}}/{{token}}"
                )

        return True, ""

    @staticmethod
    def validate_webhook_name(config: Dict[str, str], webhook_name: str) -> Tuple[bool, str]:
        """
        指定されたWebhook名の存在を検証

        Args:
            config: Webhook設定辞書
            webhook_name: 検証するWebhook名

        Returns:
            (検証結果, エラーメッセージ) のタプル
        """
        if webhook_name not in config:
            available = ", ".join(config.keys())
            return False, (
                f"Webhook '{webhook_name}' が見つかりません。\n"
                f"利用可能なWebhook: {available}"
            )

        return True, ""
