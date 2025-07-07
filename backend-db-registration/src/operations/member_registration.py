from db.database import SessionLocal, create_human_member, create_virtual_member, get_human_member_by_name, get_virtual_member_by_name, DatabaseError
from storage.storage_client import StorageClient
from validation.yaml_validator import YAMLValidator, ValidationError
import yaml
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_human_member_from_yaml(yaml_path: str):
    """YAMLファイルから人間メンバーを登録する（バリデーション・ロールバック機能付き）"""
    db = None
    try:
        # ストレージからYAMLを読み込む
        storage_client = StorageClient()
        yaml_content = storage_client.read_yaml_from_minio(yaml_path)
        
        # YAMLの構造を検証
        yaml_data = YAMLValidator.validate_yaml_structure(yaml_content)
        
        # 人間メンバーの必須フィールドを検証
        YAMLValidator.validate_human_member_yaml(yaml_data)
        
        # YAMLからデータを取得
        name = yaml_data.get('name')
        
        # DBセッションを開始
        db = SessionLocal()
        
        # 既存のメンバーをチェック
        existing_member = get_human_member_by_name(db, name)
        if existing_member:
            logger.info(f"Human member {name} already exists.")
            return existing_member
        
        # 新しいメンバーを作成（トランザクション管理付き）
        new_member = create_human_member(db, name)
        logger.info(f"Human member {name} registered successfully.")
        return new_member
        
    except ValidationError as e:
        error_msg = f"Validation error for human member registration from {yaml_path}: {e.message}"
        if e.missing_fields:
            error_msg += f" Missing fields: {', '.join(e.missing_fields)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        raise
    except DatabaseError as e:
        error_msg = f"Database error for human member registration from {yaml_path}: {e.message}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        if e.original_error:
            print(f"   Original error: {e.original_error}")
        raise
    except Exception as e:
        error_msg = f"Unexpected error for human member registration from {yaml_path}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        raise
    finally:
        if db:
            db.close()

def register_virtual_member_from_yaml(yaml_path: str):
    """YAMLファイルから仮想メンバーを登録する（バリデーション・ロールバック機能付き）"""
    db = None
    try:
        # ストレージからYAMLを読み込む
        storage_client = StorageClient()
        yaml_content = storage_client.read_yaml_from_minio(yaml_path)
        
        # YAMLの構造を検証
        yaml_data = YAMLValidator.validate_yaml_structure(yaml_content)
        
        # 仮想メンバーの必須フィールドを検証
        YAMLValidator.validate_virtual_member_yaml(yaml_data)
        
        # YAMLからデータを取得
        name = yaml_data.get('name')
        
        # DBセッションを開始
        db = SessionLocal()
        
        # 既存のメンバーをチェック
        existing_member = get_virtual_member_by_name(db, name)
        if existing_member:
            logger.info(f"Virtual member {name} already exists.")
            return existing_member
        
        # 新しいメンバーを作成（トランザクション管理付き）
        new_member = create_virtual_member(db, name)
        logger.info(f"Virtual member {name} registered successfully.")
        return new_member
        
    except ValidationError as e:
        error_msg = f"Validation error for virtual member registration from {yaml_path}: {e.message}"
        if e.missing_fields:
            error_msg += f" Missing fields: {', '.join(e.missing_fields)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        raise
    except DatabaseError as e:
        error_msg = f"Database error for virtual member registration from {yaml_path}: {e.message}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        if e.original_error:
            print(f"   Original error: {e.original_error}")
        raise
    except Exception as e:
        error_msg = f"Unexpected error for virtual member registration from {yaml_path}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        raise
    finally:
        if db:
            db.close()