import time
import logging
from pathlib import Path
from typing import Dict, Set
from storage.storage_client import StorageClient
from operations.member_registration import register_human_member_from_yaml, register_virtual_member_from_yaml
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileWatcherService:
    """ストレージファイルの更新を監視し、自動的にメンバー登録を実行するサービス
    
    MinIOストレージ内のYAMLファイルを定期的に監視し、新規作成または更新された
    ファイルを検出して自動的にメンバー登録処理を実行します。
    
    主な機能:
    - ファイルのETAG（ハッシュ値）を使用した変更検知
    - 人間メンバーと仮想メンバーの自動判別
    - エラーハンドリングと継続監視
    - バッチ処理および単独処理モードの対応
    
    Attributes:
        storage_client (StorageClient): ストレージクライアント
        polling_interval (int): ポーリング間隔（秒）
        file_etags (Dict[str, str]): ファイルのETag履歴
        processed_files (Set[str]): 処理済みファイルのセット
        running (bool): 監視サービスの実行状態
    """
    
    def __init__(self, polling_interval: int = 30):
        """ファイル監視サービスを初期化する
        
        Args:
            polling_interval (int): ファイル変更をチェックする間隔（秒）
        """
        self.storage_client = StorageClient()
        self.polling_interval = polling_interval
        self.file_etags: Dict[str, str] = {}
        self.processed_files: Set[str] = set()
        self.running = False
        logger.info(f"FileWatcherService initialized with polling interval: {polling_interval}s")
    
    def get_current_files(self) -> Dict[str, str]:
        """現在のストレージファイルとそのETagを取得する
        
        Returns:
            Dict[str, str]: ファイルパスとETagのマッピング
            
        Raises:
            Exception: ストレージアクセスエラーが発生した場合
        """
        current_files = {}
        
        try:
            # 人間メンバーファイルを取得
            human_files = self.storage_client.list_yaml_files("data/human_members/")
            for file_path in human_files:
                try:
                    # MinIOクライアントでファイル情報を取得してETagを確認
                    # ここでは簡易的にファイルの最終更新時刻を使用
                    objects = self.storage_client.client.list_objects(
                        self.storage_client.bucket_name, 
                        prefix=file_path, 
                        recursive=True
                    )
                    for obj in objects:
                        if obj.object_name == file_path:
                            current_files[file_path] = obj.etag
                            break
                except Exception as e:
                    logger.warning(f"Failed to get ETag for {file_path}: {e}")
                    # ETagが取得できない場合はファイルパスをETagとして使用
                    current_files[file_path] = f"unknown_{int(time.time())}"
            
            # 仮想メンバーファイルを取得
            virtual_files = self.storage_client.list_yaml_files("data/virtual_members/")
            for file_path in virtual_files:
                try:
                    objects = self.storage_client.client.list_objects(
                        self.storage_client.bucket_name, 
                        prefix=file_path, 
                        recursive=True
                    )
                    for obj in objects:
                        if obj.object_name == file_path:
                            current_files[file_path] = obj.etag
                            break
                except Exception as e:
                    logger.warning(f"Failed to get ETag for {file_path}: {e}")
                    current_files[file_path] = f"unknown_{int(time.time())}"
                    
        except Exception as e:
            logger.error(f"Failed to get current files: {e}")
            raise
            
        return current_files
    
    def detect_changes(self) -> Dict[str, str]:
        """ファイルの変更を検出する
        
        Returns:
            Dict[str, str]: 変更されたファイルのパスとETagのマッピング
        """
        try:
            current_files = self.get_current_files()
            changed_files = {}
            
            # 新規ファイルまたは更新されたファイルを検出
            for file_path, etag in current_files.items():
                if file_path not in self.file_etags or self.file_etags[file_path] != etag:
                    changed_files[file_path] = etag
                    logger.info(f"Detected change in file: {file_path}")
            
            # ETagを更新
            self.file_etags.update(current_files)
            
            return changed_files
            
        except Exception as e:
            logger.error(f"Failed to detect changes: {e}")
            return {}
    
    def process_changed_file(self, file_path: str) -> bool:
        """変更されたファイルを処理する
        
        Args:
            file_path (str): 処理するファイルのパス
            
        Returns:
            bool: 処理が成功した場合はTrue
        """
        try:
            logger.info(f"Processing changed file: {file_path}")
            
            # ファイルパスに基づいてメンバータイプを判定
            if "human_members" in file_path:
                register_human_member_from_yaml(file_path)
                logger.info(f"✅ Successfully registered human member from: {file_path}")
                
            elif "virtual_members" in file_path:
                register_virtual_member_from_yaml(file_path)
                logger.info(f"✅ Successfully registered virtual member from: {file_path}")
                
            else:
                logger.warning(f"⚠️  Unknown file type, skipping: {file_path}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to process file {file_path}: {e}")
            return False
    
    def initialize_file_tracking(self):
        """ファイル追跡の初期化を行う
        
        既存のファイルのETagを取得して、初回実行時に重複処理を避けるために使用します。
        """
        try:
            logger.info("Initializing file tracking...")
            self.file_etags = self.get_current_files()
            logger.info(f"Initialized tracking for {len(self.file_etags)} files")
            
            # 初期化時に既存ファイルを処理済みとしてマーク（オプション）
            for file_path in self.file_etags.keys():
                self.processed_files.add(file_path)
                
        except Exception as e:
            logger.error(f"Failed to initialize file tracking: {e}")
    
    def watch_files(self, initialize_tracking: bool = True):
        """ファイル監視を開始する（メインループ）
        
        Args:
            initialize_tracking (bool): 初回実行時にファイル追跡を初期化するか
        """
        self.running = True
        logger.info("🚀 Starting file watcher service...")
        
        if initialize_tracking:
            self.initialize_file_tracking()
        
        try:
            while self.running:
                logger.debug(f"Checking for file changes...")
                
                # ファイル変更を検出
                changed_files = self.detect_changes()
                
                if changed_files:
                    logger.info(f"Found {len(changed_files)} changed files")
                    
                    # 変更されたファイルを処理
                    for file_path in changed_files.keys():
                        if self.running:  # 停止要求がないかチェック
                            self.process_changed_file(file_path)
                else:
                    logger.debug("No file changes detected")
                
                # 次のチェックまで待機
                time.sleep(self.polling_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 File watcher service stopped by user")
        except Exception as e:
            logger.error(f"💥 File watcher service error: {e}")
        finally:
            self.running = False
            logger.info("🔚 File watcher service stopped")
    
    def stop(self):
        """ファイル監視を停止する"""
        logger.info("🛑 Stopping file watcher service...")
        self.running = False
    
    def start_in_background(self):
        """バックグラウンドでファイル監視を開始する
        
        Returns:
            threading.Thread: 監視処理を実行するスレッド
        """
        def run_watcher():
            self.watch_files()
        
        thread = threading.Thread(target=run_watcher, daemon=True)
        thread.start()
        logger.info("🚀 File watcher service started in background")
        return thread


class FileWatcherManager:
    """ファイル監視サービスの管理クラス
    
    ファイル監視サービスの開始、停止、状態管理を行います。
    """
    
    def __init__(self):
        self.watcher = None
        self.watcher_thread = None
    
    def start_watcher(self, polling_interval: int = 30) -> bool:
        """ファイル監視を開始する
        
        Args:
            polling_interval (int): ポーリング間隔（秒）
            
        Returns:
            bool: 開始に成功した場合はTrue
        """
        if self.watcher and self.watcher.running:
            logger.warning("File watcher is already running")
            return False
        
        try:
            self.watcher = FileWatcherService(polling_interval)
            self.watcher_thread = self.watcher.start_in_background()
            return True
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
            return False
    
    def stop_watcher(self) -> bool:
        """ファイル監視を停止する
        
        Returns:
            bool: 停止に成功した場合はTrue
        """
        if not self.watcher or not self.watcher.running:
            logger.warning("File watcher is not running")
            return False
        
        try:
            self.watcher.stop()
            if self.watcher_thread:
                self.watcher_thread.join(timeout=5)
            return True
        except Exception as e:
            logger.error(f"Failed to stop file watcher: {e}")
            return False
    
    def get_status(self) -> Dict[str, any]:
        """ファイル監視の状態を取得する
        
        Returns:
            Dict[str, any]: 監視状態の情報
        """
        if not self.watcher:
            return {
                "running": False,
                "files_tracked": 0,
                "polling_interval": 0
            }
        
        return {
            "running": self.watcher.running,
            "files_tracked": len(self.watcher.file_etags),
            "polling_interval": self.watcher.polling_interval,
            "processed_files": len(self.watcher.processed_files)
        }


def main():
    """ファイル監視サービスのテスト実行用メイン関数"""
    print("🚀 Starting File Watcher Service Test")
    
    # ファイル監視サービスを作成
    watcher = FileWatcherService(polling_interval=10)  # 10秒間隔でテスト
    
    try:
        # ファイル監視を開始
        watcher.watch_files()
    except KeyboardInterrupt:
        print("\n🛑 File watcher stopped by user")
    except Exception as e:
        print(f"💥 Error: {e}")


if __name__ == "__main__":
    main()