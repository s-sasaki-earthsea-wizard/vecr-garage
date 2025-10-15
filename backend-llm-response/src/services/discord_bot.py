"""
Discord Bot本体

@メンション検知 → LLM API連携 → Discord返信
複数チャンネル対応
カスタムプロンプト対応
"""

import discord
import logging
from typing import List, Optional
from services.llm_client import LLMClient
from services.times_scheduler import TimesScheduler
from config.prompt import PromptParser

logger = logging.getLogger(__name__)


class DiscordBot:
    """Discord Botクラス（@メンション対応）"""

    def __init__(
        self,
        bot_name: str,
        bot_token: str,
        mention_channels: List[int],
        auto_thread_channels: List[int],
        times_channels: List[int],
    ):
        """
        初期化

        Args:
            bot_name: Bot名
            bot_token: Bot Token
            mention_channels: @メンション対応チャンネルIDのリスト
            auto_thread_channels: 新着投稿自動スレッド作成チャンネルIDのリスト
            times_channels: Times Mode（1日1回自動投稿）チャンネルIDのリスト
        """
        self.bot_name = bot_name
        self.bot_token = bot_token
        self.mention_mode_channels = set(mention_channels)  # 高速検索のためsetに変換
        self.auto_thread_mode_channels = set(auto_thread_channels)
        self.times_mode_channels = set(times_channels)

        # システムプロンプトの読み込み
        self.system_prompt = PromptParser.get_prompt(bot_name, source="file")

        # Intents設定（Message Content Intent必須）
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.messages = True

        self.client = discord.Client(intents=intents)
        self.llm_client = LLMClient()

        # Times Mode スケジューラー初期化
        self.times_scheduler = TimesScheduler(
            bot_name=self.bot_name,
            system_prompt=self.system_prompt,
            discord_client=self.client,
            times_channels=list(times_channels)
        )

        # イベントハンドラー登録
        self._setup_events()

    def _setup_events(self):
        """イベントハンドラーをセットアップ"""

        @self.client.event
        async def on_ready():
            """Bot起動時"""
            logger.info(f"✅ Discord Bot起動完了: {self.client.user} (Bot名: {self.bot_name})")
            logger.info(
                f"📍 Mentionモード対象チャンネル数: {len(self.mention_mode_channels)} "
                f"(IDs: {', '.join(str(ch) for ch in self.mention_mode_channels)})"
            )
            logger.info(
                f"📍 AutoThreadモード対象チャンネル数: {len(self.auto_thread_mode_channels)} "
                f"(IDs: {', '.join(str(ch) for ch in self.auto_thread_mode_channels)})"
            )
            logger.info(
                f"📍 Timesモード対象チャンネル数: {len(self.times_mode_channels)} "
                f"(IDs: {', '.join(str(ch) for ch in self.times_mode_channels)})"
            )

            # Times Mode スケジューラー起動
            self.times_scheduler.start()

        @self.client.event
        async def on_message(message):
            """メッセージ受信時（モード別にルーティング）"""
            # 1. 自分自身のメッセージは無視
            if message.author == self.client.user:
                return

            channel_id = message.channel.id

            # 2. Mentionモード処理
            if channel_id in self.mention_mode_channels:
                await self._handle_mention_mode(message)

            # 3. AutoThreadモード処理
            elif channel_id in self.auto_thread_mode_channels:
                await self._handle_auto_thread_mode(message)

    async def _handle_mention_mode(self, message):
        """
        Mentionモード処理: @メンション検知 → LLM応答

        Args:
            message: Discordメッセージオブジェクト
        """
        # 1. メンションチェック
        if self.client.user not in message.mentions:
            return

        # 2. プロンプト抽出（メンション部分を除去）
        prompt = message.content.replace(f"<@{self.client.user.id}>", "").strip()

        if not prompt:
            await message.channel.send("❓ 質問内容を入力してください。")
            return

        logger.info(
            f"📩 [Mentionモード] メンション検知: {message.author} "
            f"in {message.channel.name} - {prompt[:50]}..."
        )

        # 3. LLM API呼び出し
        try:
            # システムプロンプトを使用してLLM APIを呼び出し
            response = self.llm_client.send_message(
                prompt=prompt, system_prompt=self.system_prompt
            )

            # 4. Discord文字数制限対応（2000文字）
            if len(response) > 2000:
                response = response[:1900] + "\n\n...(応答が長すぎるため省略)"

            # 5. 返信
            await message.channel.send(response)
            logger.info(f"✅ 応答送信完了: {len(response)}文字")

        except Exception as e:
            logger.error(f"❌ LLM API呼び出しエラー: {e}", exc_info=True)
            await message.channel.send(
                "⚠️ エラーが発生しました。後ほど再試行してください。"
            )

    async def _handle_auto_thread_mode(self, message):
        """
        AutoThreadモード処理: 会話履歴を含めて新着投稿に自動返信

        Args:
            message: Discordメッセージオブジェクト
        """
        # 1. Bot自身の投稿は無視（無限ループ防止）
        if message.author == self.client.user:
            return

        logger.info(
            f"📩 [AutoThreadモード] 新着投稿検知: {message.author.display_name} "
            f"in {message.channel.name} - {message.content[:50]}..."
        )

        try:
            # 2. チャンネルの会話履歴を取得（最新メッセージ含めて最大20件）
            conversation_history = await self._get_conversation_history(message)

            # 3. LLM API呼び出し
            response = self.llm_client.send_message(
                prompt=conversation_history,
                system_prompt=self.system_prompt
            )

            # 4. Discord文字数制限対応（2000文字）
            if len(response) > 2000:
                response = response[:1900] + "\n\n...(応答が長すぎるため省略)"

            # 5. 元の投稿者に@メンションして返信
            await message.reply(f"{message.author.mention}\n{response}")
            logger.info(f"✅ [AutoThreadモード] 応答送信完了: {len(response)}文字")

        except Exception as e:
            logger.error(f"❌ [AutoThreadモード] エラー: {e}", exc_info=True)
            await message.reply(
                f"{message.author.mention} ⚠️ エラーが発生しました。後ほど再試行してください。"
            )

    async def _get_conversation_history(self, current_message, limit: int = 20) -> str:
        """
        チャンネルの会話履歴を取得してプロンプト形式に整形

        Args:
            current_message: 現在のメッセージオブジェクト
            limit: 取得する履歴の最大件数（デフォルト: 20件）

        Returns:
            会話履歴のプロンプト文字列
        """
        history_messages = []

        # Discord APIで履歴を取得（最新メッセージの前まで）
        async for msg in current_message.channel.history(limit=limit, before=current_message):
            # システムメッセージやピン留めメッセージは除外
            if msg.type == discord.MessageType.default:
                history_messages.insert(0, msg)  # 古い順に並べる

        # 会話履歴を整形
        conversation_lines = []
        for msg in history_messages:
            author_name = self.bot_name if msg.author == self.client.user else msg.author.display_name
            conversation_lines.append(f"{author_name}: {msg.content}")

        # 最新メッセージを追加
        conversation_lines.append(f"{current_message.author.display_name}: {current_message.content}")

        # 改行で結合
        conversation_context = "\n".join(conversation_lines)

        logger.debug(f"📝 会話履歴取得: {len(history_messages)}件 + 現在のメッセージ")

        return conversation_context

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
