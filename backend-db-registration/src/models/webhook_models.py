from datetime import datetime

from pydantic import BaseModel


class WebhookEvent(BaseModel):
    """Webhookイベントの基本モデル"""

    event_type: str
    timestamp: datetime
    bucket_name: str
    object_name: str
    etag: str | None = None
    size: int | None = None


class MinIOWebhookPayload(BaseModel):
    """MinIO Webhook通知のペイロードモデル"""

    Records: list[dict]


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
    processed_files: list[str] = []
    errors: list[str] = []
