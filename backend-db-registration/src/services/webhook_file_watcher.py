import json
import os
import urllib.parse

from models.webhook_models import FileChangeEvent, WebhookResponse
from operations.member_registration import (
    register_human_member_from_yaml,
    register_virtual_member_from_yaml,
)
from storage.storage_client import StorageClient
from utils.logging_config import setup_logging

logger = setup_logging(__name__)


class WebhookFileWatcherService:
    """Webhook通知によるファイル変更監視サービス

    MinIOストレージからのWebhook通知を受け取り、ファイル変更を検出して
    自動的にメンバー登録処理を実行します。

    主な機能:
    - Webhook通知の受信と解析
    - ファイル変更イベントの処理
    - 人間メンバーと仮想メンバーの自動判別
    - エラーハンドリングとログ出力

    Attributes:
        storage_client (StorageClient): ストレージクライアント
        processed_events (Dict[str, str]): 処理済みイベントの追跡
        etag_check_enabled (bool): ETag重複チェック機能の有効/無効
    """

    def __init__(self):
        """Webhookファイル監視サービスを初期化する"""
        self.storage_client = StorageClient()
        self.processed_events: dict[str, str] = {}  # event_id -> etag

        # ETagチェック機能の有効/無効を環境変数から取得
        self.etag_check_enabled = os.getenv("WEBHOOK_ETAG_CHECK_ENABLED", "true").lower() == "true"
        logger.info(
            f"WebhookFileWatcherService initialized (ETag check: {'enabled' if self.etag_check_enabled else 'disabled'})"
        )

    def parse_webhook_payload(self, payload: dict) -> list[FileChangeEvent]:
        """Webhookペイロードを解析してファイル変更イベントを抽出する

        Args:
            payload (dict): Webhook通知のペイロード

        Returns:
            List[FileChangeEvent]: 解析されたファイル変更イベントのリスト
        """
        events = []

        try:
            # MinIO Webhook通知の形式に応じて解析
            if "Records" in payload:
                for record in payload["Records"]:
                    if "s3" in record:
                        s3_data = record["s3"]
                        bucket = s3_data["bucket"]["name"]
                        object_key = s3_data["object"]["key"]
                        event_name = record.get("eventName", "")

                        # ETagとサイズを取得
                        etag = s3_data["object"].get("eTag", "").strip('"')
                        size = s3_data["object"].get("size", 0)
                        event_time = record.get("eventTime", "")

                        event = FileChangeEvent(
                            event_name=event_name,
                            bucket_name=bucket,
                            object_name=object_key,
                            etag=etag,
                            size=size,
                            event_time=event_time,
                        )
                        events.append(event)
                        logger.info(f"Parsed event: {event_name} for {object_key}")

            # カスタムWebhook形式のサポート
            elif "events" in payload:
                for event_data in payload["events"]:
                    event = FileChangeEvent(**event_data)
                    events.append(event)
                    logger.info(f"Parsed custom event for {event.object_name}")

            # 単一イベント形式のサポート
            elif "event_name" in payload:
                event = FileChangeEvent(**payload)
                events.append(event)
                logger.info(f"Parsed single event for {event.object_name}")

        except Exception as e:
            logger.error(f"Failed to parse webhook payload: {e}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

        return events

    def should_process_event(self, event: FileChangeEvent) -> bool:
        """イベントを処理すべきかどうかを判定する

        Args:
            event (FileChangeEvent): 処理対象のイベント

        Returns:
            bool: 処理すべき場合はTrue
        """
        # オブジェクトキーをURLデコード
        try:
            decoded_object_name = urllib.parse.unquote(event.object_name)
            # デバッグログでエンコード前後のパスを記録
            if decoded_object_name != event.object_name:
                logger.debug(
                    f"URL decoded object name: {event.object_name} -> {decoded_object_name}"
                )
        except Exception as e:
            logger.warning(f"Failed to URL decode object name '{event.object_name}': {e}")
            # デコードに失敗した場合は元のパスを使用
            decoded_object_name = event.object_name

        # イベントIDを生成（デコード後のオブジェクト名 + ETag）
        event_id = f"{decoded_object_name}_{event.etag}"

        # ETagチェックが有効な場合のみ重複チェックを実行
        if self.etag_check_enabled:
            if event_id in self.processed_events:
                logger.debug(f"Skipping already processed event: {event_id}")
                return False
        else:
            logger.debug(f"ETag check disabled - processing event: {event_id}")

        # 対象外のイベントをスキップ
        if event.event_name not in [
            "s3:ObjectCreated:Put",
            "s3:ObjectCreated:Post",
            "s3:ObjectCreated:CompleteMultipartUpload",
            "s3:ObjectCreated:Copy",
        ]:
            logger.debug(f"Skipping non-creation event: {event.event_name}")
            return False

        # YAMLファイルのみを処理（デコード後のパスで判定）
        if not decoded_object_name.endswith((".yaml", ".yml")):
            logger.debug(f"Skipping non-YAML file: {decoded_object_name}")
            return False

        # 対象ディレクトリのファイルのみを処理（デコード後のパスで判定）
        # 新しいディレクトリ構造に対応: samples/とtest_cases/両方をサポート
        target_patterns = [
            "data/samples/human_members/",
            "data/samples/virtual_members/",
            "data/test_cases/human_members/",
            "data/test_cases/virtual_members/",
            # 旧形式との互換性のため（段階的移行）
            "data/human_members/",
            "data/virtual_members/",
        ]

        if not any(decoded_object_name.startswith(pattern) for pattern in target_patterns):
            logger.debug(f"Skipping file outside target directories: {decoded_object_name}")
            return False

        return True

    def process_file_event(self, event: FileChangeEvent) -> bool:
        """ファイル変更イベントを処理する

        Args:
            event (FileChangeEvent): 処理するイベント

        Returns:
            bool: 処理が成功した場合はTrue

        Raises:
            ValidationError: YAMLデータのバリデーションに失敗した場合
            DatabaseError: データベース操作に失敗した場合
            Exception: その他の予期しないエラーが発生した場合
        """
        # オブジェクトキーをURLデコード
        try:
            decoded_object_name = urllib.parse.unquote(event.object_name)
            # デバッグログでエンコード前後のパスを記録
            if decoded_object_name != event.object_name:
                logger.debug(
                    f"URL decoded object name: {event.object_name} -> {decoded_object_name}"
                )
        except Exception as e:
            logger.warning(f"Failed to URL decode object name '{event.object_name}': {e}")
            # デコードに失敗した場合は元のパスを使用
            decoded_object_name = event.object_name

        logger.info(f"Processing file event: {event.event_name} for {decoded_object_name}")

        # ファイルパスに基づいてメンバータイプを判定（デコード後のパスで判定）
        if "human_members" in decoded_object_name:
            register_human_member_from_yaml(decoded_object_name)
            logger.info(f"✅ Successfully registered human member from: {decoded_object_name}")

        elif "virtual_members" in decoded_object_name:
            register_virtual_member_from_yaml(decoded_object_name)
            logger.info(f"✅ Successfully registered virtual member from: {decoded_object_name}")

        else:
            logger.warning(f"⚠️  Unknown file type, skipping: {decoded_object_name}")
            return False

        # ETagチェックが有効な場合のみ処理済みイベントとしてマーク
        if self.etag_check_enabled:
            # 処理済みイベントとしてマーク（デコード後のパスでイベントID生成）
            # TODO: 将来的にfile_uriベースのUPSERT実装でこのETagチェックは不要になる
            # Issue: https://github.com/your-org/vecr-garage/issues/xxx
            # 現在はDB側の一時的なUPSERT処理により同じファイルの更新が正しく処理される
            event_id = f"{decoded_object_name}_{event.etag}"
            self.processed_events[event_id] = event.etag
            logger.debug(f"Marked event as processed: {event_id}")
        else:
            logger.debug(
                f"ETag check disabled - not marking event as processed: {decoded_object_name}"
            )

        return True

    def handle_webhook(self, payload: dict) -> WebhookResponse:
        """Webhook通知を処理する

        Args:
            payload (dict): Webhook通知のペイロード

        Returns:
            WebhookResponse: 処理結果
        """
        logger.info("📥 Received webhook notification")

        processed_files = []
        errors = []

        try:
            # ペイロードを解析
            events = self.parse_webhook_payload(payload)

            if not events:
                logger.warning("No valid events found in webhook payload")
                return WebhookResponse(
                    success=False,
                    message="No valid events found in webhook payload",
                    errors=["No valid events found"],
                )

            logger.info(f"Found {len(events)} events to process")

            # 各イベントを処理
            for event in events:
                if self.should_process_event(event):
                    try:
                        if self.process_file_event(event):
                            processed_files.append(event.object_name)
                        else:
                            errors.append(f"Failed to process {event.object_name}")
                    except Exception as e:
                        # ValidationError, DatabaseError, その他全ての例外をここでキャッチ
                        # エラーは既にregister_*_member_from_yaml関数内でログ出力済み
                        errors.append(f"Failed to process {event.object_name}: {str(e)}")
                        logger.error(
                            f"❌ Failed to process file event {event.object_name}: {str(e)}"
                        )
                else:
                    logger.debug(f"Skipped duplicate event for {event.object_name}")

            # ETagチェックが有効な場合のみクリーンアップを実行
            if self.etag_check_enabled:
                # 処理済みイベントの履歴をクリーンアップ（古いエントリを削除）
                self._cleanup_processed_events()

            # 成功の判定: エラーが0の場合（重複検出による処理スキップは正常な動作）
            success = len(errors) == 0

            # メッセージの構築
            if len(processed_files) > 0:
                message = f"Processed {len(processed_files)} files successfully"
            else:
                message = "No new files to process (duplicate detection working)"

            if errors:
                message += f", {len(errors)} errors occurred"

            return WebhookResponse(
                success=success,
                message=message,
                processed_files=processed_files,
                errors=errors,
            )

        except Exception as e:
            logger.error(f"💥 Error handling webhook: {e}")
            return WebhookResponse(
                success=False,
                message=f"Error handling webhook: {str(e)}",
                errors=[str(e)],
            )

    def _cleanup_processed_events(self, max_events: int = 1000):
        """処理済みイベントの履歴をクリーンアップする

        Args:
            max_events (int): 保持する最大イベント数
        """
        if len(self.processed_events) > max_events:
            # 古いエントリを削除（簡易的な実装）
            items_to_remove = len(self.processed_events) - max_events
            keys_to_remove = list(self.processed_events.keys())[:items_to_remove]

            for key in keys_to_remove:
                del self.processed_events[key]

            logger.debug(f"Cleaned up {items_to_remove} old processed events")

    def get_status(self) -> dict:
        """サービスの状態を取得する

        Returns:
            dict: サービス状態の情報
        """
        return {
            "service_type": "webhook",
            "processed_events_count": len(self.processed_events),
            "storage_client_available": self.storage_client is not None,
        }
