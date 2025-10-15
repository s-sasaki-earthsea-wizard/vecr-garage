#!/usr/bin/env python3
"""
Discord Bot起動スクリプト（メインエントリーポイント）

Discord Botを起動し、@メンションに対してClaude APIで応答します。
"""

import sys
import os
import logging
from services.discord_bot import DiscordBot
from config.discord import DiscordConfigParser

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Discord Bot起動"""
    # デフォルトBot名（環境変数で上書き可能）
    bot_name = os.getenv("DISCORD_BOT_NAME", "🤖🍡華扇")

    logger.info("=" * 60)
    logger.info(f"🚀 Discord Bot '{bot_name}' を起動します")
    logger.info("=" * 60)

    try:
        # Bot設定取得（モード別チャンネル取得）
        token, mention_channels, auto_thread_channels = DiscordConfigParser.get_bot_config(bot_name)

        logger.info(
            f"📝 Bot設定取得成功: "
            f"Mentionモード {len(mention_channels)}ch, "
            f"AutoThreadモード {len(auto_thread_channels)}ch"
        )

        # Bot起動
        bot = DiscordBot(bot_name, token, mention_channels, auto_thread_channels)
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
