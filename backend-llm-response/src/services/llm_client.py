"""
LLMクライアントサービス

LLM（Large Language Model）APIを使用してプロンプトを送信し、応答を取得する機能を提供します。
現在はAnthropic Claude APIを実装。将来的にHugging Face等の他プロバイダーにも対応予定。
"""

import os
from typing import Any, Optional

from anthropic import Anthropic


class LLMClient:
    """LLMクライアント（現在はClaude実装、将来的に複数プロバイダー対応予定）"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        LLMClientを初期化（現在はClaude API使用）

        Args:
            api_key: Anthropic APIキー（未指定の場合は環境変数ANTHROPIC_API_KEYを使用）
            model: 使用するモデル（未指定の場合は環境変数ANTHROPIC_MODELを使用）
            max_tokens: 最大トークン数（未指定の場合は環境変数ANTHROPIC_MAX_TOKENSを使用）
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
        self.max_tokens = max_tokens or int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096"))

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEYが設定されていません")

        self.client = Anthropic(api_key=self.api_key)

    def send_message(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 1.0,
    ) -> str:
        """
        プロンプトをLLM APIに送信し、応答を取得

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト（オプション）
            temperature: 生成温度（0.0-1.0）

        Returns:
            LLM APIからの応答文字列

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            # メッセージ構築
            messages = [{"role": "user", "content": prompt}]

            # API呼び出しパラメータ
            params: dict[str, Any] = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": messages,
                "temperature": temperature,
            }

            # システムプロンプトがある場合は追加
            if system_prompt:
                params["system"] = system_prompt

            # API呼び出し
            response = self.client.messages.create(**params)

            # テキスト応答を抽出
            if response.content and len(response.content) > 0:
                return response.content[0].text

            return ""

        except Exception as e:
            raise Exception(f"LLM API呼び出しエラー: {str(e)}")

    def send_test_message(self) -> dict[str, Any]:
        """
        テストメッセージを送信して動作確認

        Returns:
            テスト結果の辞書
        """
        try:
            test_prompt = "こんにちは！簡単な自己紹介をしてください。"
            response = self.send_message(test_prompt)

            return {
                "success": True,
                "model": self.model,
                "prompt": test_prompt,
                "response": response,
                "message": "LLM API接続成功",
            }

        except Exception as e:
            return {
                "success": False,
                "model": self.model,
                "error": str(e),
                "message": "LLM API接続失敗",
            }
