"""
Discord Bot本体

@メンション検知 → Claude API連携 → Discord返信
複数チャンネル対応
"""

import discord
import logging
from typing import List
from services.claude_client import ClaudeClient

logger = logging.getLogger(__name__)


class DiscordBot:
    """Discord Botクラス（@メンション対応）"""

    def __init__(self, bot_name: str, bot_token: str, target_channel_ids: List[int]):
        """
        初期化

        Args:
            bot_name: Bot名
            bot_token: Bot Token
            target_channel_ids: 対象チャンネルIDのリスト
        """
        self.bot_name = bot_name
        self.bot_token = bot_token
        self.target_channel_ids = set(target_channel_ids)  # 高速検索のためsetに変換

        # Intents設定（Message Content Intent必須）
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.messages = True

        self.client = discord.Client(intents=intents)
        self.claude_client = ClaudeClient()

        # イベントハンドラー登録
        self._setup_events()

    def _setup_events(self):
        """イベントハンドラーをセットアップ"""

        @self.client.event
        async def on_ready():
            """Bot起動時"""
            logger.info(f"✅ Discord Bot起動完了: {self.client.user} (Bot名: {self.bot_name})")
            logger.info(
                f"📍 対象チャンネル数: {len(self.target_channel_ids)} "
                f"(IDs: {', '.join(str(ch) for ch in self.target_channel_ids)})"
            )

        @self.client.event
        async def on_message(message):
            """メッセージ受信時"""
            # 1. 自分自身のメッセージは無視
            if message.author == self.client.user:
                return

            # 2. 対象チャンネルのみ処理
            if message.channel.id not in self.target_channel_ids:
                return

            # 3. メンションチェック
            if self.client.user not in message.mentions:
                return

            # 4. プロンプト抽出（メンション部分を除去）
            prompt = message.content.replace(f"<@{self.client.user.id}>", "").strip()

            if not prompt:
                await message.channel.send("❓ 質問内容を入力してください。")
                return

            logger.info(
                f"📩 メンション検知: {message.author} "
                f"in {message.channel.name} - {prompt[:50]}..."
            )

            # 5. Claude API呼び出し
            try:
                response = self.claude_client.send_message(prompt)

                # 6. Discord文字数制限対応（2000文字）
                if len(response) > 2000:
                    response = response[:1900] + "\n\n...(応答が長すぎるため省略)"

                # 7. 返信
                await message.channel.send(response)
                logger.info(f"✅ 応答送信完了: {len(response)}文字")

            except Exception as e:
                logger.error(f"❌ Claude API呼び出しエラー: {e}", exc_info=True)
                await message.channel.send(
                    "⚠️ エラーが発生しました。後ほど再試行してください。"
                )

    def run(self):
        """Bot起動（ブロッキング）"""
        logger.info(f"🤖 Bot '{self.bot_name}' を起動中...")
        try:
            self.client.run(self.bot_token, log_handler=None)  # ロギングは既に設定済み
        except discord.LoginFailure:
            logger.error(f"❌ Bot Tokenが不正です: {self.bot_name}")
            raise
        except Exception as e:
            logger.error(f"❌ Bot起動エラー ({self.bot_name}): {e}", exc_info=True)
            raise
