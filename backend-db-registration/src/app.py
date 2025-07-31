from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import logging
from services.webhook_file_watcher import WebhookFileWatcherService
from models.webhook_models import WebhookResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Member Registration API",
    description="API for member registration with webhook file monitoring",
    version="1.0.0"
)

# Initialize webhook file watcher service
webhook_watcher = WebhookFileWatcherService()


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
            "webhook_watcher": watcher_status
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
        
        return JSONResponse(
            content=result.model_dump(),
            status_code=status_code
        )
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        error_response = WebhookResponse(
            success=False,
            message=f"Internal server error: {str(e)}",
            errors=[str(e)]
        )
        return JSONResponse(
            content=error_response.model_dump(),
            status_code=500
        )


@app.get("/webhook/status")
async def get_webhook_status():
    """Webhookサービスの状態を取得するエンドポイント"""
    try:
        status = webhook_watcher.get_status()
        return {
            "status": "success",
            "data": status
        }
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
                            "name": "vecr-storage"
                        },
                        "object": {
                            "key": "data/human_members/test_human_member.yaml",
                            "eTag": "test-etag-123",
                            "size": 1024
                        }
                    }
                }
            ]
        }
        
        result = webhook_watcher.handle_webhook(test_payload)
        return {
            "message": "Test webhook processed",
            "result": result.model_dump()
        }
        
    except Exception as e:
        logger.error(f"Test webhook failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info"
    )