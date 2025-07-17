from db.database import SessionLocal, save_human_member, save_virtual_member, get_human_member_by_name, get_virtual_member_by_name, DatabaseError
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
        # ストレージからYAMLを読み込む（既にパース済みの辞書オブジェクト）
        storage_client = StorageClient()
        yaml_data = storage_client.read_yaml_from_minio(yaml_path)
        
        # YAMLからデータを取得
        name = yaml_data.get('name')
        
        # DBセッションを開始
        db = SessionLocal()
        
        # 人間メンバーの必須フィールドを検証
        YAMLValidator.validate_human_member_yaml(yaml_data)
        
        # 既存のメンバーをチェック
        existing_member = get_human_member_by_name(db, name)
        if existing_member:
            logger.info(f"Human member {name} already exists.")
            return existing_member
        
        # 新しいメンバーを作成して保存
        new_member = save_human_member(db, name)
        logger.info(f"Human member {name} created and committed successfully.")
        return new_member
        
    except ValidationError as e:
        # バリデーションエラーでもロールバックを実行
        if db:
            db.rollback()
        error_msg = f"Validation error for human member registration from {yaml_path}: {e.message}"
        if e.missing_fields:
            error_msg += f" Missing fields: {', '.join(e.missing_fields)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        raise
    except DatabaseError as e:
        # データベースエラーでもロールバックを実行
        if db:
            db.rollback()
        error_msg = f"Database error for human member registration from {yaml_path}: {e.message}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        if e.original_error:
            print(f"   Original error: {e.original_error}")
        raise
    except Exception as e:
        # その他のエラーでもロールバックを実行
        if db:
            db.rollback()
        if "NoSuchKey" in str(e):
            error_msg = f"Storage error for human member registration from {yaml_path}: File not found in storage"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
        else:
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
        # ストレージからYAMLを読み込む（既にパース済みの辞書オブジェクト）
        storage_client = StorageClient()
        yaml_data = storage_client.read_yaml_from_minio(yaml_path)
        
        # YAMLからデータを取得
        name = yaml_data.get('name')
        
        # DBセッションを開始
        db = SessionLocal()
        
        # 仮想メンバーの必須フィールドを検証
        YAMLValidator.validate_virtual_member_yaml(yaml_data)
        
        # 既存のメンバーをチェック
        existing_member = get_virtual_member_by_name(db, name)
        if existing_member:
            logger.info(f"Virtual member {name} already exists.")
            return existing_member
        
        # 新しいメンバーを作成して保存
        new_member = save_virtual_member(db, name)
        logger.info(f"Virtual member {name} created and committed successfully.")
        return new_member
        
    except ValidationError as e:
        # バリデーションエラーでもロールバックを実行
        if db:
            db.rollback()
        error_msg = f"Validation error for virtual member registration from {yaml_path}: {e.message}"
        if e.missing_fields:
            error_msg += f" Missing fields: {', '.join(e.missing_fields)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        raise
    except DatabaseError as e:
        # データベースエラーでもロールバックを実行
        if db:
            db.rollback()
        error_msg = f"Database error for virtual member registration from {yaml_path}: {e.message}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        if e.original_error:
            print(f"   Original error: {e.original_error}")
        raise
    except Exception as e:
        # その他のエラーでもロールバックを実行
        if db:
            db.rollback()
        if "NoSuchKey" in str(e):
            error_msg = f"Storage error for virtual member registration from {yaml_path}: File not found in storage"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
        else:
            error_msg = f"Unexpected error for virtual member registration from {yaml_path}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
        raise
    finally:
        if db:
            db.close()

def register_human_members_batch(yaml_paths: list):
    """複数のYAMLファイルから人間メンバーをバッチ登録する（全成功または全ロールバック）"""
    db = None
    created_members = []
    
    try:
        # DBセッションを開始
        db = SessionLocal()
        storage_client = StorageClient()
        
        # 全てのファイルを事前にバリデーション
        yaml_data_list = []
        for yaml_path in yaml_paths:
            try:
                yaml_data = storage_client.read_yaml_from_minio(yaml_path)
                # バリデーション
                YAMLValidator.validate_human_member_yaml(yaml_data)
                yaml_data_list.append((yaml_path, yaml_data))
            except Exception as e:
                error_msg = f"Validation error for {yaml_path}: {str(e)}"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                raise
        
        # 全てのバリデーションが成功した場合のみ、データベース操作を実行
        for yaml_path, yaml_data in yaml_data_list:
            name = yaml_data.get('name')
            
            # 既存のメンバーをチェック
            existing_member = get_human_member_by_name(db, name)
            if existing_member:
                logger.info(f"Human member {name} already exists.")
                created_members.append(existing_member)
                continue
            
            # 新しいメンバーを作成（まだコミットしない）
            new_member = create_human_member(db, name)
            created_members.append(new_member)
            logger.info(f"Human member {name} prepared for creation.")
        
        # 全ての処理が成功した場合のみコミット
        db.commit()
        logger.info(f"Successfully committed {len(created_members)} human members.")
        return created_members
        
    except Exception as e:
        # エラーが発生した場合はロールバック
        if db:
            db.rollback()
        error_msg = f"Batch registration failed: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        print("All changes have been rolled back.")
        raise
    finally:
        if db:
            db.close()

def register_virtual_members_batch(yaml_paths: list):
    """複数のYAMLファイルから仮想メンバーをバッチ登録する（全成功または全ロールバック）"""
    db = None
    created_members = []
    
    try:
        # DBセッションを開始
        db = SessionLocal()
        storage_client = StorageClient()
        
        # 全てのファイルを事前にバリデーション
        yaml_data_list = []
        for yaml_path in yaml_paths:
            try:
                yaml_data = storage_client.read_yaml_from_minio(yaml_path)
                # バリデーション
                YAMLValidator.validate_virtual_member_yaml(yaml_data)
                yaml_data_list.append((yaml_path, yaml_data))
            except Exception as e:
                error_msg = f"Validation error for {yaml_path}: {str(e)}"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                raise
        
        # 全てのバリデーションが成功した場合のみ、データベース操作を実行
        for yaml_path, yaml_data in yaml_data_list:
            name = yaml_data.get('name')
            
            # 既存のメンバーをチェック
            existing_member = get_virtual_member_by_name(db, name)
            if existing_member:
                logger.info(f"Virtual member {name} already exists.")
                created_members.append(existing_member)
                continue
            
            # 新しいメンバーを作成（まだコミットしない）
            new_member = create_virtual_member(db, name)
            created_members.append(new_member)
            logger.info(f"Virtual member {name} prepared for creation.")
        
        # 全ての処理が成功した場合のみコミット
        db.commit()
        logger.info(f"Successfully committed {len(created_members)} virtual members.")
        return created_members
        
    except Exception as e:
        # エラーが発生した場合はロールバック
        if db:
            db.rollback()
        error_msg = f"Batch registration failed: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        print("All changes have been rolled back.")
        raise
    finally:
        if db:
            db.close()