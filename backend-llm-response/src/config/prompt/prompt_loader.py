"""
プロンプトローダー

Bot用のシステムプロンプトをファイルから読み込む機能を提供します。
将来的にデータベースからの読み込みにも対応予定。
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PromptLoader:
    """プロンプトローダー（ファイルベース、将来的にDB対応予定）"""

    PROMPT_DIR = "prompts/bot_characters"

    @staticmethod
    def load_from_file(bot_name: str) -> Optional[str]:
        """
        ファイルからプロンプトを読み込み

        Args:
            bot_name: Bot名

        Returns:
            プロンプト文字列。ファイルが存在しない場合はNone
        """
        prompt_file = f"{PromptLoader.PROMPT_DIR}/{bot_name}.txt"

        if not os.path.exists(prompt_file):
            logger.warning(
                f"⚠️ システムプロンプトファイルが見つかりません: {prompt_file}"
            )
            logger.info(
                f"💡 デフォルトプロンプトなしで起動します。"
                f"カスタマイズする場合は {prompt_file} を作成してください。"
            )
            return None

        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                prompt = f.read().strip()

            logger.info(f"✅ システムプロンプト読み込み成功: {prompt_file}")
            logger.debug(f"📝 プロンプト内容 ({len(prompt)}文字): {prompt[:100]}...")

            return prompt

        except Exception as e:
            logger.error(
                f"❌ システムプロンプト読み込みエラー: {prompt_file} - {e}",
                exc_info=True,
            )
            return None

    @staticmethod
    def load_from_db(bot_name: str) -> Optional[str]:
        """
        データベースからプロンプトを読み込み（将来実装）

        Args:
            bot_name: Bot名

        Returns:
            プロンプト文字列。見つからない場合はNone
        """
        # TODO: virtual_member_profiles.custom_promptから読み込み
        logger.warning("⚠️ DB連携は未実装です。ファイルベースを使用してください。")
        return None
