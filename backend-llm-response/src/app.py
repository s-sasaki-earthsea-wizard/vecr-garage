#!/usr/bin/env python3
"""
Discord Bot起動スクリプト（メインエントリーポイント）

Discord Botを起動し、@メンションに対してClaude APIで応答します。
"""

import logging
import os
import sys

from services.discord_bot import DiscordBot

from config.discord import DiscordConfigParser

# ロギング設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Discord Bot起動"""
    # デフォルトBot名（環境変数で上書き可能）
    bot_name = os.getenv("DISCORD_BOT_NAME", "🤖🍡華扇")

    # Times Modeテスト設定（環境変数で制御）
    times_test_mode = os.getenv("TIMES_TEST_MODE", "false").lower() == "true"
    times_test_interval = int(os.getenv("TIMES_TEST_INTERVAL", "60"))

    logger.info("=" * 60)
    logger.info(f"🚀 Discord Bot '{bot_name}' を起動します")
    if times_test_mode:
        logger.info(
            f"🧪 Times Mode テストモード有効 (インターバル: {times_test_interval}秒)"
        )
    logger.info("=" * 60)

    try:
        # Bot設定取得（モード別チャンネル取得）
        token, mention_channels, auto_thread_channels, times_channels = (
            DiscordConfigParser.get_bot_config(bot_name)
        )

        logger.info(
            f"📝 Bot設定取得成功: "
            f"Mentionモード {len(mention_channels)}ch, "
            f"AutoThreadモード {len(auto_thread_channels)}ch, "
            f"Timesモード {len(times_channels)}ch"
        )

        # Bot起動
        bot = DiscordBot(
            bot_name,
            token,
            mention_channels,
            auto_thread_channels,
            times_channels,
            times_test_mode=times_test_mode,
            times_test_interval=times_test_interval,
        )
        bot.run()

    except FileNotFoundError as e:
        logger.error(f"❌ 設定ファイルエラー: {e}")
        sys.exit(1)

    except ValueError as e:
        logger.error(f"❌ 設定エラー: {e}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Bot起動エラー: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Discord Botを停止します...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 予期しないエラー: {e}", exc_info=True)
        sys.exit(1)
