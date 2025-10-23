"""
Discord Bot Times Mode スケジューラー

平日（月〜金）のJST 9:00-18:00の間に1日1回、ランダムな話題で投稿する機能
"""

import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Optional

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class TimesScheduler:
    """Times Mode スケジューラー（1日1回ランダム投稿）"""

    def __init__(
        self,
        bot_name: str,
        system_prompt: str,
        discord_client,
        times_channels: list[int],
        test_mode: bool = False,
        test_interval_seconds: int = 60,
    ):
        """
        初期化

        Args:
            bot_name: Bot名
            system_prompt: システムプロンプト
            discord_client: discord.Clientインスタンス
            times_channels: Times Mode対象チャンネルIDリスト
            test_mode: テストモード（True: 即座実行＋短いインターバル、False: 本番モード）
            test_interval_seconds: テストモード時のインターバル秒数（デフォルト: 60秒）
        """
        self.bot_name = bot_name
        self.system_prompt = system_prompt
        self.discord_client = discord_client
        self.times_channels = times_channels
        self.llm_client = LLMClient()

        # テストモード設定
        self.test_mode = test_mode
        self.test_interval_seconds = test_interval_seconds

        # JST設定
        self.jst = pytz.timezone("Asia/Tokyo")

        # スケジューラー初期化（非同期対応）
        self.scheduler = AsyncIOScheduler(timezone=self.jst)

        # 1日1回投稿済みフラグ（日付ベース管理）
        self.last_posted_date: Optional[str] = None

        # 話題リスト読み込み
        self.topics = self._load_topics()

        mode_str = "テストモード" if test_mode else "本番モード"
        logger.info(
            f"📅 TimesScheduler初期化完了 ({mode_str}): Bot '{self.bot_name}', "
            f"対象チャンネル数: {len(self.times_channels)}, "
            f"話題数: {len(self.topics)}"
        )

    def _load_topics(self) -> list[str]:
        """
        話題リストをJSONファイルから読み込み

        Returns:
            話題リスト

        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: JSON形式が不正
        """
        topics_file = (
            Path(__file__).parent.parent.parent / "prompts" / "times_topics.json"
        )

        if not topics_file.exists():
            raise FileNotFoundError(
                f"話題リストファイルが見つかりません: {topics_file}"
            )

        try:
            with open(topics_file, encoding="utf-8") as f:
                data = json.load(f)
                topics = data.get("topics", [])

                if not topics:
                    raise ValueError("話題リストが空です")

                logger.info(f"✅ 話題リスト読み込み成功: {len(topics)}件")
                return topics

        except json.JSONDecodeError as e:
            raise ValueError(f"JSON形式が不正です: {e}")

    def start(self):
        """スケジューラー起動"""
        if not self.times_channels:
            logger.warning(
                "⚠️ Times Mode対象チャンネルが0件のためスケジューラーを起動しません"
            )
            return

        # トリガー設定（本番モード or テストモード）
        if not self.test_mode:
            # 本番モード: 平日9:00に実行、jitterで0-32400秒（9時間）のランダム遅延
            trigger = self._create_production_trigger()
            job_name = "Times Mode 1日1回投稿（平日のみ）"
            log_msg = "平日（月〜金）JST 9:00-18:00の間にランダム投稿"
        else:
            # テストモード: 短いインターバルで繰り返し実行
            trigger = self._create_test_trigger()
            job_name = f"Times Mode テスト投稿 ({self.test_interval_seconds}秒間隔)"
            log_msg = f"{self.test_interval_seconds}秒ごとに投稿 (1日1回制御は無効)"
            logger.info(f"🧪 テストモード有効: {log_msg}")

        self.scheduler.add_job(
            self._post_random_topic,
            trigger=trigger,
            id="times_mode_daily_post",
            name=job_name,
        )

        self.scheduler.start()
        logger.info(f"🚀 TimesSchedulerスケジューラー起動完了: {log_msg}")

    def _create_production_trigger(self):
        """本番モード用のトリガーを作成（平日のみ9:00、jitter 9時間）"""
        return CronTrigger(
            day_of_week="mon-fri",  # 月曜日〜金曜日のみ実行
            hour=9,
            minute=0,
            second=0,
            timezone=self.jst,
            jitter=32400,  # 9時間 = 9 * 60 * 60 = 32400秒
        )

    def _create_test_trigger(self):
        """テストモード用のトリガーを作成（短いインターバル）"""
        from apscheduler.triggers.interval import IntervalTrigger

        return IntervalTrigger(seconds=self.test_interval_seconds, timezone=self.jst)

    async def _post_random_topic(self):
        """
        ランダムな話題で投稿（1日1回制御）
        """
        # 今日の日付取得（JST）
        today = datetime.now(self.jst).strftime("%Y-%m-%d")

        # 本番モードのみ1日1回制御を実施
        if not self.test_mode:
            # 今日既に投稿済みならスキップ
            if self.last_posted_date == today:
                logger.info(f"⏭️ 本日({today})は既に投稿済みのためスキップ")
                return

        logger.info(f"📝 Times Mode投稿開始: {today}")

        # ランダムに話題を選択
        topic = random.choice(self.topics)
        logger.info(f"🎲 選択された話題: {topic[:50]}...")

        # LLM API呼び出し
        try:
            response = self.llm_client.send_message(
                prompt=topic, system_prompt=self.system_prompt
            )

            # Discord文字数制限対応（2000文字）
            if len(response) > 2000:
                response = response[:1900] + "\n\n...(応答が長すぎるため省略)"

            # 全対象チャンネルに投稿
            for channel_id in self.times_channels:
                try:
                    channel = self.discord_client.get_channel(channel_id)
                    if channel is None:
                        logger.warning(f"⚠️ チャンネルID {channel_id} が見つかりません")
                        continue

                    await channel.send(response)
                    logger.info(
                        f"✅ Times Mode投稿完了: チャンネル {channel.name} ({channel_id}), "
                        f"{len(response)}文字"
                    )

                except Exception as e:
                    logger.error(
                        f"❌ Times Mode投稿エラー (チャンネルID: {channel_id}): {e}",
                        exc_info=True,
                    )

            # 投稿済みフラグ更新
            self.last_posted_date = today
            logger.info(f"🎉 本日({today})のTimes Mode投稿完了")

        except Exception as e:
            logger.error(f"❌ LLM API呼び出しエラー: {e}", exc_info=True)

    def stop(self):
        """スケジューラー停止"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 TimesSchedulerスケジューラー停止")
