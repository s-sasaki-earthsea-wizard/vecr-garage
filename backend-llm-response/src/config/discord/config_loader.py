"""
Discord Bot設定ファイル読み込み

JSONファイルからBot設定を読み込みます。
"""

import json
import logging
import os

logger = logging.getLogger(__name__)


class DiscordConfigLoader:
    """Discord Bot設定ファイルローダー"""

    DEFAULT_CONFIG_FILE = "config/discord_tokens.json"

    @staticmethod
    def load_config(file_path: str = None) -> dict[str, dict[str, any]]:
        """
        JSONファイルから設定を読み込み

        Args:
            file_path: 設定ファイルパス（未指定時はデフォルト）

        Returns:
            設定辞書
            形式: {
                "bot_name": {
                    "bot_token": "...",
                    "channel_ids": ["id1", "id2"]
                }
            }

        Raises:
            FileNotFoundError: ファイルが存在しない
            json.JSONDecodeError: JSON形式が不正
        """
        if file_path is None:
            file_path = DiscordConfigLoader.DEFAULT_CONFIG_FILE

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Discord Bot設定ファイルが見つかりません: {file_path}\n"
                f"config/discord_tokens.example.json を参考に作成してください"
            )

        try:
            with open(file_path, encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Discord Bot設定ファイルのJSON形式が不正です: {file_path}",
                e.doc,
                e.pos,
            )

        logger.info(f"Discord Bot設定を読み込みました: {len(config)}個のBot")
        return config
