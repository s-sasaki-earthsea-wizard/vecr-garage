"""
プロンプトローダー

Bot用のシステムプロンプトをファイルから読み込む機能を提供します。
将来的にデータベースからの読み込みにも対応予定。
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptLoader:
    """プロンプトローダー（ファイルベース、将来的にDB対応予定）"""

    PROMPT_DIR = "prompts/bot_characters"

    @staticmethod
    def load_from_file(bot_name: str) -> str | None:
        """
        ファイルからプロンプトを読み込み

        Args:
            bot_name: Bot名

        Returns:
            プロンプト文字列。ファイルが存在しない場合はNone
        """
        prompt_file = Path(f"{PromptLoader.PROMPT_DIR}/{bot_name}.txt")

        if not prompt_file.exists():
            logger.warning(f"⚠️ システムプロンプトファイルが見つかりません: {prompt_file}")
            logger.info(
                f"💡 デフォルトプロンプトなしで起動します。"
                f"カスタマイズする場合は {prompt_file} を作成してください。"
            )
            return None

        try:
            prompt = prompt_file.read_text(encoding="utf-8").strip()

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
    def load_from_db(bot_name: str) -> str | None:
        """
        データベースからプロンプトを読み込み

        Args:
            bot_name: Bot名

        Returns:
            プロンプト文字列。見つからない場合はNone
        """
        from db.connection.connection import DBMemberConnection
        from db.operation.member_queries import get_virtual_member_prompt

        try:
            # データベース接続
            db_connection = DBMemberConnection()
            session = db_connection.db_member_connection_check()

            try:
                # プロンプト取得
                prompt = get_virtual_member_prompt(session, bot_name)

                if prompt:
                    logger.info(f"✅ DB からシステムプロンプト読み込み成功: {bot_name}")
                    logger.debug(f"📝 プロンプト内容 ({len(prompt)}文字): {prompt[:100]}...")
                    return prompt
                else:
                    logger.info(f"💡 DB にプロンプトが見つかりません: {bot_name}")
                    return None

            finally:
                session.close()

        except Exception as e:
            logger.error(f"❌ DB からのプロンプト読み込みエラー: {bot_name} - {e}", exc_info=True)
            return None
