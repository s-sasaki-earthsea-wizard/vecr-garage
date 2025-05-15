from db.database import SessionLocal, create_human_member, create_virtual_member, get_human_member_by_name, get_virtual_member_by_name
from storage.storage_client import StorageClient
import yaml
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_human_member_from_yaml(yaml_path: str):
    """YAMLファイルから人間メンバーを登録する"""
    try:
        # ストレージからYAMLを読み込む
        storage_client = StorageClient()
        yaml_data = storage_client.read_yaml_from_minio(yaml_path)
        
        # YAMLからデータを取得
        name = yaml_data.get('name')
        
        # DBセッションを開始
        db = SessionLocal()
        try:
            # 既存のメンバーをチェック
            existing_member = get_human_member_by_name(db, name)
            if existing_member:
                logger.info(f"Human member {name} already exists.")
                return existing_member
            
            # 新しいメンバーを作成
            new_member = create_human_member(db, name)
            logger.info(f"Human member {name} registered successfully.")
            return new_member
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error registering human member: {e}")
        raise

def register_virtual_member_from_yaml(yaml_path: str):
    """YAMLファイルから仮想メンバーを登録する"""
    try:
        # ストレージからYAMLを読み込む
        storage_client = StorageClient()
        yaml_data = storage_client.read_yaml_from_minio(yaml_path)
        
        # YAMLからデータを取得
        name = yaml_data.get('name')
        
        # DBセッションを開始
        db = SessionLocal()
        try:
            # 既存のメンバーをチェック
            existing_member = get_virtual_member_by_name(db, name)
            if existing_member:
                logger.info(f"Virtual member {name} already exists.")
                return existing_member
            
            # 新しいメンバーを作成
            new_member = create_virtual_member(db, name)
            logger.info(f"Virtual member {name} registered successfully.")
            return new_member
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error registering virtual member: {e}")
        raise