import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from models.webhook_models import WebhookResponse
from services.webhook_file_watcher import WebhookFileWatcherService
from utils.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Configure logging
logger = setup_logging(__name__)

# Create FastAPI app
app = FastAPI(
    title="Member Registration API",
    description="API for member registration with webhook file monitoring",
    version="1.0.0",
)

# Initialize webhook file watcher service
webhook_watcher = WebhookFileWatcherService()

# Initialize storage monitor
from storage.storage_monitor import StorageMonitor

storage_monitor = StorageMonitor()


# Add storage monitor health check endpoints
@app.get("/health/storage-monitor")
async def storage_monitor_health():
    """ストレージ監視サービスの詳細ヘルスチェック"""
    try:
        # Webhook設定の確認（セキュリティのため詳細情報は制限）
        webhook_status = {
            "enabled": storage_monitor.webhook_enabled,
            "configured": True,
        }

        # ストレージ接続の確認
        from storage.storage_client import StorageClient

        storage_client = StorageClient()
        try:
            storage_client.storage_connection_check()
            storage_status = {"status": "connected", "storage": "minio"}
        except Exception as e:
            storage_status = {"status": "error", "error": str(e)}

        # データベース接続の確認
        from db.database import engine

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
            "database": db_status,
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/health/storage-monitor/ready")
async def storage_monitor_ready():
    """ストレージ監視サービスの準備完了チェック"""
    try:
        # 基本的な接続確認
        from db.database import engine
        from storage.storage_client import StorageClient

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
        raise HTTPException(status_code=503, detail="Service not ready")

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: storage_ok={storage_ok}, db_ok={db_ok}, error={str(e)}",
        )


@app.get("/")
async def hello():
    """ヘルスチェックエンドポイント"""
    return {"message": "Hello from backend-db-registration!", "status": "healthy"}


@app.get("/health")
async def health_check():
    """詳細なヘルスチェックエンドポイント"""
    try:
        watcher_status = webhook_watcher.get_status()
        return {
            "status": "healthy",
            "service": "backend-db-registration",
            "webhook_watcher": watcher_status,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/webhook/file-change", response_model=WebhookResponse)
async def handle_file_change_webhook(request: Request):
    """ファイル変更Webhookエンドポイント

    MinIOストレージからのファイル変更通知を受け取り、自動的にメンバー登録処理を実行します。

    Args:
        request (Request): FastAPIリクエストオブジェクト

    Returns:
        WebhookResponse: 処理結果
    """
    try:
        # リクエストボディを取得
        payload = await request.json()
        logger.info(f"Received webhook payload: {payload}")

        # Webhook処理を実行
        result = webhook_watcher.handle_webhook(payload)

        # レスポンスステータスコードを決定
        status_code = 200 if result.success else 400

        return JSONResponse(content=result.model_dump(), status_code=status_code)

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        error_response = WebhookResponse(
            success=False, message=f"Internal server error: {str(e)}", errors=[str(e)]
        )
        return JSONResponse(content=error_response.model_dump(), status_code=500)


@app.get("/webhook/status")
async def get_webhook_status():
    """Webhookサービスの状態を取得するエンドポイント"""
    try:
        status = webhook_watcher.get_status()
        return {"status": "success", "data": status}
    except Exception as e:
        logger.error(f"Failed to get webhook status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@app.post("/webhook/test")
async def test_webhook():
    """Webhook機能のテスト用エンドポイント"""
    try:
        # テスト用のペイロード
        test_payload = {
            "Records": [
                {
                    "eventName": "s3:ObjectCreated:Put",
                    "eventTime": "2024-01-01T00:00:00.000Z",
                    "s3": {
                        "bucket": {
                            "name": os.getenv("MINIO_BUCKET_NAME", "vecr-storage")
                        },
                        "object": {
                            "key": "data/samples/human_members/test_human_member.yaml",
                            "eTag": "test-etag-123",
                            "size": 1024,
                        },
                    },
                }
            ]
        }

        result = webhook_watcher.handle_webhook(test_payload)
        return {"message": "Test webhook processed", "result": result.model_dump()}

    except Exception as e:
        logger.error(f"Test webhook failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "3000")),
        reload=True,
        log_level="info",
    )
