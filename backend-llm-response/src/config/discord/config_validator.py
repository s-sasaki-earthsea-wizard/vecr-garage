"""
Discord Bot設定バリデーター

Bot設定の構造とフィールドをバリデーションします。
"""

from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class DiscordConfigValidator:
    """Discord Bot設定のバリデーター"""

    @staticmethod
    def validate_config(config: Dict[str, Dict[str, any]]) -> Tuple[bool, str]:
        """
        設定全体をバリデーション

        Args:
            config: Bot設定辞書

        Returns:
            (成功フラグ, エラーメッセージ)
        """
        if not isinstance(config, dict):
            return False, f"設定のルートは辞書である必要があります（現在: {type(config).__name__}）"

        for bot_name, bot_config in config.items():
            is_valid, error_msg = DiscordConfigValidator.validate_bot_config(bot_name, bot_config)
            if not is_valid:
                return False, error_msg

        return True, ""

    @staticmethod
    def validate_bot_config(bot_name: str, bot_config: Dict[str, any]) -> Tuple[bool, str]:
        """
        個別Bot設定をバリデーション

        Args:
            bot_name: Bot名
            bot_config: Bot設定

        Returns:
            (成功フラグ, エラーメッセージ)
        """
        if not isinstance(bot_config, dict):
            return False, f"Bot '{bot_name}' の設定は辞書である必要があります"

        # bot_tokenチェック
        if "bot_token" not in bot_config:
            return False, f"Bot '{bot_name}' に bot_token フィールドが必要です"

        if not isinstance(bot_config["bot_token"], str):
            return False, f"Bot '{bot_name}' の bot_token は文字列である必要があります"

        # channelsチェック
        if "channels" not in bot_config:
            return False, f"Bot '{bot_name}' に channels フィールドが必要です"

        channels = bot_config["channels"]
        if not isinstance(channels, dict):
            return False, f"Bot '{bot_name}' の channels は辞書である必要があります"

        # mention_modeのチェック
        if "mention_mode" in channels:
            if not isinstance(channels["mention_mode"], list):
                return (
                    False,
                    f"Bot '{bot_name}' の channels.mention_mode は配列である必要があります",
                )
            for idx, channel_id in enumerate(channels["mention_mode"]):
                if not isinstance(channel_id, (str, int)):
                    return False, (
                        f"Bot '{bot_name}' の channels.mention_mode[{idx}] は文字列または数値である必要があります"
                    )

        # auto_thread_modeのチェック
        if "auto_thread_mode" in channels:
            if not isinstance(channels["auto_thread_mode"], list):
                return (
                    False,
                    f"Bot '{bot_name}' の channels.auto_thread_mode は配列である必要があります",
                )
            for idx, channel_id in enumerate(channels["auto_thread_mode"]):
                if not isinstance(channel_id, (str, int)):
                    return False, (
                        f"Bot '{bot_name}' の channels.auto_thread_mode[{idx}] は文字列または数値である必要があります"
                    )

        # times_modeのチェック
        if "times_mode" in channels:
            if not isinstance(channels["times_mode"], list):
                return False, f"Bot '{bot_name}' の channels.times_mode は配列である必要があります"
            for idx, channel_id in enumerate(channels["times_mode"]):
                if not isinstance(channel_id, (str, int)):
                    return False, (
                        f"Bot '{bot_name}' の channels.times_mode[{idx}] は文字列または数値である必要があります"
                    )

        return True, ""
