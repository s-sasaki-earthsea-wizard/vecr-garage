"""
Webhook設定パーサー

環境変数からWebhook設定を読み込み、パース、バリデーションを実行
"""

import os
import json
import logging
from typing import Dict, Optional
from .webhook_validator import WebhookValidator

logger = logging.getLogger(__name__)


class WebhookConfigParser:
    """Webhook設定パーサークラス"""

    DEFAULT_ENV_VAR = "DISCORD_WEBHOOKS"
    DEFAULT_FILE_ENV_VAR = "DISCORD_WEBHOOKS_FILE"

    @staticmethod
    def parse_from_file(file_path: str) -> Dict[str, str]:
        """
        JSONファイルからWebhook設定を読み込む

        Args:
            file_path: JSONファイルのパス

        Returns:
            Webhook設定辞書

        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: JSONパースまたはバリデーションエラー
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Webhook設定ファイルが見つかりません: {file_path}\n"
                f"config/discord_webhooks.example.json をコピーして作成してください"
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"JSONファイルのパースに失敗: {file_path}\n{e}")

        # バリデーション
        is_valid, error_msg = WebhookValidator.validate_webhook_config(config)
        if not is_valid:
            raise ValueError(f"Webhook設定のバリデーションエラー ({file_path}): {error_msg}")

        logger.info(f"Webhook設定ファイル読み込み成功: {file_path} ({len(config)}個)")
        logger.debug(f"登録Webhook: {list(config.keys())}")

        return config

    @staticmethod
    def parse_from_env(env_var: str = DEFAULT_ENV_VAR) -> Dict[str, str]:
        """
        環境変数からWebhook設定をパースして取得

        Args:
            env_var: 環境変数名（デフォルト: DISCORD_WEBHOOKS）

        Returns:
            Webhook設定辞書 {"webhook_name": "webhook_url", ...}

        Raises:
            ValueError: 環境変数が見つからない、パースに失敗、バリデーションエラー
        """
        # 環境変数取得
        config_str = os.getenv(env_var)

        if not config_str:
            raise ValueError(
                f"環境変数 '{env_var}' が設定されていません。\n"
                f'例: {env_var}=\'{{"webhook_name": "https://discord.com/api/webhooks/..."}}\''
            )

        # パース処理
        config = WebhookConfigParser._parse_json_string(config_str)

        # バリデーション
        is_valid, error_msg = WebhookValidator.validate_webhook_config(config)
        if not is_valid:
            raise ValueError(f"Webhook設定のバリデーションエラー: {error_msg}")

        logger.info(f"Webhook設定のパースに成功: {len(config)}個のWebhook登録")
        logger.debug(f"登録Webhook: {list(config.keys())}")

        return config

    @staticmethod
    def parse_from_string(config_str: str) -> Dict[str, str]:
        """
        JSON文字列からWebhook設定をパース

        Args:
            config_str: JSON形式の設定文字列

        Returns:
            Webhook設定辞書

        Raises:
            ValueError: パースまたはバリデーションエラー
        """
        config = WebhookConfigParser._parse_json_string(config_str)

        # バリデーション
        is_valid, error_msg = WebhookValidator.validate_webhook_config(config)
        if not is_valid:
            raise ValueError(f"Webhook設定のバリデーションエラー: {error_msg}")

        return config

    @staticmethod
    def parse_from_dict(config_dict: Dict[str, str]) -> Dict[str, str]:
        """
        辞書からWebhook設定を取得（バリデーションのみ実行）

        Args:
            config_dict: Webhook設定辞書

        Returns:
            検証済みWebhook設定辞書

        Raises:
            ValueError: バリデーションエラー
        """
        # バリデーション
        is_valid, error_msg = WebhookValidator.validate_webhook_config(config_dict)
        if not is_valid:
            raise ValueError(f"Webhook設定のバリデーションエラー: {error_msg}")

        return config_dict

    @staticmethod
    def _parse_json_string(config_str: str) -> Dict[str, str]:
        """
        JSON文字列をパース（内部メソッド）

        Args:
            config_str: JSON文字列

        Returns:
            パース結果の辞書

        Raises:
            ValueError: JSONパースエラー
        """
        # クォート除去（環境変数から取得した場合）
        cleaned_str = config_str.strip("'\"")

        try:
            parsed = json.loads(cleaned_str)

            if not isinstance(parsed, dict):
                raise ValueError(
                    f"Webhook設定は辞書型のJSONである必要があります "
                    f"（現在: {type(parsed).__name__}）"
                )

            return parsed

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Webhook設定のJSONパースに失敗しました: {e}\n" f"入力値: {cleaned_str[:100]}..."
            )

    @staticmethod
    def get_webhook_url(config: Dict[str, str], webhook_name: str) -> str:
        """
        Webhook名からURLを安全に取得

        Args:
            config: Webhook設定辞書
            webhook_name: Webhook名

        Returns:
            Webhook URL

        Raises:
            KeyError: Webhook名が存在しない場合
        """
        is_valid, error_msg = WebhookValidator.validate_webhook_name(config, webhook_name)

        if not is_valid:
            raise KeyError(error_msg)

        return config[webhook_name]
