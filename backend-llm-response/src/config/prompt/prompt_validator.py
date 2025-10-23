"""
プロンプトバリデーター

システムプロンプトの妥当性を検証する機能を提供します。
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PromptValidator:
    """プロンプトバリデーター"""

    # プロンプトの最大文字数（Claude APIの制限を考慮）
    MAX_PROMPT_LENGTH = 100000

    @staticmethod
    def validate(prompt: Optional[str]) -> tuple[bool, str]:
        """
        プロンプトをバリデーション

        Args:
            prompt: プロンプト文字列

        Returns:
            (is_valid, error_message) のタプル
        """
        # Noneは許容（プロンプトなしで起動可能）
        if prompt is None:
            return True, ""

        # 空文字チェック
        if not prompt or not prompt.strip():
            return False, "プロンプトが空です"

        # 文字数チェック
        if len(prompt) > PromptValidator.MAX_PROMPT_LENGTH:
            return (
                False,
                f"プロンプトが長すぎます（{len(prompt)}文字 > {PromptValidator.MAX_PROMPT_LENGTH}文字）",
            )

        # 将来的にインジェクション対策などを追加可能
        # TODO: プロンプトインジェクション対策

        return True, ""
