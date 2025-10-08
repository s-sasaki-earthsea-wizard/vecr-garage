"""
プロンプトパーサー

システムプロンプトの取得・管理機能の公開API（Facade）を提供します。
"""

import logging
from typing import Optional

from config.prompt.prompt_loader import PromptLoader
from config.prompt.prompt_validator import PromptValidator

logger = logging.getLogger(__name__)


class PromptParser:
    """プロンプトパーサー（公開API - Facade）"""

    @staticmethod
    def get_prompt(bot_name: str, source: str = "file") -> Optional[str]:
        """
        Bot名からシステムプロンプトを取得

        Args:
            bot_name: Bot名
            source: 取得元 ("file" or "db")

        Returns:
            プロンプト文字列。取得失敗またはバリデーションエラーの場合はNone
        """
        # Step 1: ソースから読み込み
        if source == "file":
            prompt = PromptLoader.load_from_file(bot_name)
        elif source == "db":
            prompt = PromptLoader.load_from_db(bot_name)
        else:
            logger.error(f"❌ 不明なプロンプトソース: {source}")
            return None

        # Step 2: バリデーション
        is_valid, error_msg = PromptValidator.validate(prompt)
        if not is_valid:
            logger.error(f"❌ プロンプトバリデーションエラー: {error_msg}")
            return None

        return prompt
