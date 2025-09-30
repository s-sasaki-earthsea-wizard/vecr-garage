#!/usr/bin/env python3
"""
ストレージ監視設定とヘルスチェック機能

このモジュールは、MinIOストレージの監視設定と
ヘルスチェック機能を提供します。

主な機能:
- MinIOストレージの監視設定
- Webhook設定の管理
- ヘルスチェック機能
"""

import os
from utils.logging_config import setup_logging

# ログ設定
logger = setup_logging(__name__)


class StorageMonitor:
    """ストレージ監視クラス"""
    
    def __init__(self):
        """ストレージ監視を初期化"""
        self.webhook_enabled = os.getenv('WEBHOOK_ENABLED', 'true').lower() == 'true'
        self.webhook_endpoint = os.getenv('WEBHOOK_ENDPOINT', '/webhook/file-change')
        self.webhook_events = os.getenv('WEBHOOK_EVENTS', 's3:ObjectCreated:*,s3:ObjectRemoved:*')
        self.webhook_filter_prefix = os.getenv('WEBHOOK_FILTER_PREFIX', 'data/')
        self.webhook_filter_suffix = os.getenv('WEBHOOK_FILTER_SUFFIX', '.yaml,.yml')
        
        logger.info("🚀 Storage Monitor initialized")
        logger.info(f"📋 Configuration:")
        logger.info(f"   - Webhook enabled: {self.webhook_enabled}")
        # セキュリティのため詳細設定はログに出力しない
    
    def get_config(self):
        """現在の設定を取得"""
        return {
            "webhook_enabled": self.webhook_enabled,
            "webhook_endpoint": self.webhook_endpoint,
            "webhook_events": self.webhook_events,
            "webhook_filter_prefix": self.webhook_filter_prefix,
            "webhook_filter_suffix": self.webhook_filter_suffix
        }
    
    def update_config(self, **kwargs):
        """設定を更新"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.info(f"Updated {key}: {value}")
        
        return self.get_config()


# メイン関数は削除（app.pyから呼び出されるため） 