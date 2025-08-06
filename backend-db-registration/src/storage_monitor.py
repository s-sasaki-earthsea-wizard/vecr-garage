#!/usr/bin/env python3
"""
ストレージ監視メインスクリプト

このスクリプトは、MinIOストレージの監視をメインロジックとして
FastAPIサーバーを起動し、Webhook機能を提供します。

主な機能:
- MinIOストレージの監視
- Webhook通知の受信と処理
- メンバー登録の自動実行
- ヘルスチェック機能
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 環境変数を読み込み
load_dotenv()

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
    
    def start_monitoring(self):
        """ストレージ監視を開始"""
        try:
            logger.info("🔍 Starting storage monitoring...")
            
            # FastAPIアプリケーションをインポート
            from src.app import app
            
            # ヘルスチェックエンドポイントを追加
            self._add_health_check_endpoints(app)
            
            # サーバーを起動
            import uvicorn
            uvicorn.run(
                app,
                host=os.getenv("HOST", "0.0.0.0"),
                port=int(os.getenv("PORT", "3000")),
                log_level="info",
                access_log=True
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to start storage monitoring: {e}")
            sys.exit(1)
    
    def _add_health_check_endpoints(self, app):
        """ヘルスチェックエンドポイントを追加"""
        from fastapi import HTTPException
        
        @app.get("/health/storage-monitor")
        async def storage_monitor_health():
            """ストレージ監視サービスの詳細ヘルスチェック"""
            try:
                # Webhook設定の確認（セキュリティのため詳細情報は制限）
                webhook_status = {
                    "enabled": self.webhook_enabled,
                    "configured": True
                }
                
                # ストレージ接続の確認
                from src.storage.storage_client import StorageClient
                storage_client = StorageClient()
                try:
                    storage_client.storage_connection_check()
                    storage_status = {"status": "connected", "storage": "minio"}
                except Exception as e:
                    storage_status = {"status": "error", "error": str(e)}
                
                # データベース接続の確認
                from src.db.database import engine
                try:
                    with engine.connect() as conn:
                        from sqlalchemy import text
                        conn.execute(text("SELECT 1"))
                        conn.commit()
                    db_status = {"status": "connected", "database": "postgresql"}
                except Exception as e:
                    db_status = {"status": "error", "error": str(e)}
                
                return {
                    "status": "healthy",
                    "service": "storage-monitor",
                    "webhook": webhook_status,
                    "storage": storage_status,
                    "database": db_status
                }
                
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
        
        @app.get("/health/storage-monitor/ready")
        async def storage_monitor_ready():
            """ストレージ監視サービスの準備完了チェック"""
            try:
                # 基本的な接続確認
                from src.storage.storage_client import StorageClient
                from src.db.database import engine
                
                storage_client = StorageClient()
                
                try:
                    storage_ok = storage_client.storage_connection_check()
                except Exception:
                    storage_ok = False
                try:
                    with engine.connect() as conn:
                        from sqlalchemy import text
                        conn.execute(text("SELECT 1"))
                        conn.commit()
                    db_ok = True
                except Exception:
                    db_ok = False
                
                if storage_ok and db_ok:
                    return {"status": "ready", "service": "storage-monitor"}
                else:
                    raise HTTPException(status_code=503, detail="Service not ready")
                    
            except Exception as e:
                logger.error(f"Readiness check failed: {e}")
                raise HTTPException(status_code=503, detail=f"Service not ready: storage_ok={storage_ok}, db_ok={db_ok}, error={str(e)}")


def main():
    """メイン関数"""
    print("🚀 VECR Office Storage Monitor")
    print("=" * 50)
    
    # ストレージ監視を初期化
    monitor = StorageMonitor()
    
    # 監視を開始
    monitor.start_monitoring()


if __name__ == "__main__":
    main() 