from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class WebhookEvent(BaseModel):
    """Webhookイベントの基本モデル"""
    event_type: str
    timestamp: datetime
    bucket_name: str
    object_name: str
    etag: Optional[str] = None
    size: Optional[int] = None


class MinIOWebhookPayload(BaseModel):
    """MinIO Webhook通知のペイロードモデル"""
    Records: List[dict]


class FileChangeEvent(BaseModel):
    """ファイル変更イベントのモデル"""
    event_name: str
    bucket_name: str
    object_name: str
    etag: str
    size: int
    event_time: str


class WebhookResponse(BaseModel):
    """Webhook処理結果のレスポンスモデル"""
    success: bool
    message: str
    processed_files: List[str] = []
    errors: List[str] = [] 