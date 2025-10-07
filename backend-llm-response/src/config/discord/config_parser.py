"""
Discord Bot設定パーサー（ファサード）

設定の読み込み・バリデーション・取得を統合した公開APIを提供します。
"""

from typing import Dict, List, Tuple, Optional
import logging
from .config_loader import DiscordConfigLoader
from .config_validator import DiscordConfigValidator

logger = logging.getLogger(__name__)


class DiscordConfigParser:
    """Discord Bot設定パーサー（公開API）"""

    @staticmethod
    def load_and_validate(file_path: Optional[str] = None) -> Dict[str, Dict[str, any]]:
        """
        設定を読み込みバリデーション

        Args:
            file_path: 設定ファイルパス（未指定時はデフォルト）

        Returns:
            Bot設定辞書

        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: バリデーションエラー
        """
        config = DiscordConfigLoader.load_config(file_path)

        is_valid, error_msg = DiscordConfigValidator.validate_config(config)
        if not is_valid:
            raise ValueError(f"Discord Bot設定のバリデーションエラー: {error_msg}")

        return config

    @staticmethod
    def get_bot_token(bot_name: str, config: Optional[Dict] = None) -> str:
        """
        Bot名からTokenを取得

        Args:
            bot_name: Bot名
            config: Bot設定（未指定時はファイルから読み込み）

        Returns:
            Bot Token

        Raises:
            ValueError: Bot名が見つからない
        """
        if config is None:
            config = DiscordConfigParser.load_and_validate()

        if bot_name not in config:
            available_bots = ", ".join(config.keys())
            raise ValueError(
                f"Bot '{bot_name}' が見つかりません。\n"
                f"利用可能なBot: {available_bots}"
            )

        return config[bot_name]["bot_token"]

    @staticmethod
    def get_bot_channels(bot_name: str, config: Optional[Dict] = None) -> List[int]:
        """
        Bot名からチャンネルIDリストを取得

        Args:
            bot_name: Bot名
            config: Bot設定（未指定時はファイルから読み込み）

        Returns:
            チャンネルIDのリスト（int型）

        Raises:
            ValueError: Bot名が見つからない
        """
        if config is None:
            config = DiscordConfigParser.load_and_validate()

        if bot_name not in config:
            available_bots = ", ".join(config.keys())
            raise ValueError(
                f"Bot '{bot_name}' が見つかりません。\n"
                f"利用可能なBot: {available_bots}"
            )

        # 文字列・数値のチャンネルIDをintに変換
        channels = config[bot_name]["channel_ids"]
        return [int(ch) for ch in channels]

    @staticmethod
    def get_bot_config(bot_name: str, config: Optional[Dict] = None) -> Tuple[str, List[int]]:
        """
        Bot名からTokenとチャンネルIDリストを取得

        Args:
            bot_name: Bot名
            config: Bot設定（未指定時はファイルから読み込み）

        Returns:
            (Bot Token, チャンネルIDリスト) のタプル

        Raises:
            ValueError: Bot名が見つからない
        """
        if config is None:
            config = DiscordConfigParser.load_and_validate()

        token = DiscordConfigParser.get_bot_token(bot_name, config)
        channels = DiscordConfigParser.get_bot_channels(bot_name, config)

        return token, channels

    @staticmethod
    def list_bots(config: Optional[Dict] = None) -> List[str]:
        """
        登録されているBot名のリストを取得

        Args:
            config: Bot設定（未指定時はファイルから読み込み）

        Returns:
            Bot名のリスト
        """
        if config is None:
            config = DiscordConfigParser.load_and_validate()

        return list(config.keys())
