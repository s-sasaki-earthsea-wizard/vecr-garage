"""
Claude-Discord統合サービス

Claude APIからの応答をDiscord Webhookに投稿する機能を提供します。
"""

from typing import Dict, Any, Optional
from services.claude_client import ClaudeClient
from services.discord_notifier import DiscordNotifier


class ClaudeDiscordBridge:
    """Claude APIとDiscord Webhookを統合するブリッジサービス"""

    def __init__(self):
        """ClaudeDiscordBridgeを初期化"""
        self.claude_client = ClaudeClient()
        self.discord_notifier = DiscordNotifier()

    def send_prompt_to_discord(
        self,
        webhook_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 1.0,
        include_prompt: bool = True,
    ) -> Dict[str, Any]:
        """
        プロンプトをClaude APIに送信し、応答をDiscordに投稿

        Args:
            webhook_name: Discord Webhook名
            prompt: Claude APIに送信するプロンプト
            system_prompt: システムプロンプト（オプション）
            temperature: 生成温度（0.0-1.0）
            include_prompt: Discordメッセージにプロンプトを含めるか

        Returns:
            実行結果の辞書
        """
        try:
            # Step 1: Claude APIにプロンプトを送信
            claude_response = self.claude_client.send_message(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
            )

            # Step 2: Discord投稿用のメッセージを構築
            if include_prompt:
                discord_content = f"**プロンプト:**\n{prompt}\n\n**Claude応答:**\n{claude_response}"
            else:
                discord_content = claude_response

            # メッセージが長すぎる場合は分割（Discord制限: 2000文字）
            if len(discord_content) > 2000:
                discord_content = discord_content[:1900] + "\n\n...(応答が長すぎるため省略)"

            # Step 3: Discordに投稿
            discord_result = self.discord_notifier.send_message(
                webhook_name=webhook_name,
                content=discord_content,
            )

            return {
                "success": True,
                "webhook_name": webhook_name,
                "prompt": prompt,
                "claude_response": claude_response,
                "discord_result": discord_result,
                "message": "Claude応答をDiscordに投稿しました",
            }

        except Exception as e:
            return {
                "success": False,
                "webhook_name": webhook_name,
                "prompt": prompt,
                "error": str(e),
                "message": "Claude-Discord統合処理でエラーが発生しました",
            }
