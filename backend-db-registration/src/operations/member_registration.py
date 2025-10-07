from db.database import SessionLocal, save_human_member, save_virtual_member, get_human_member_by_name, get_virtual_member_by_name, get_human_member_by_uri, get_virtual_member_by_uri, upsert_human_member, upsert_virtual_member, DatabaseError, create_human_member, create_virtual_member
from storage.storage_client import StorageClient
from validation.yaml_validator import YAMLValidator, ValidationError
import yaml
from utils.logging_config import setup_logging

logger = setup_logging(__name__)

def register_human_member_from_yaml(yaml_path: str):
    """YAMLファイルから人間メンバーを登録する（バリデーション・ロールバック機能付き）
    
    ストレージから指定されたYAMLファイルを読み込み、バリデーションを実行した後、
    データベースに人間メンバーとして登録します。エラーが発生した場合は
    自動的にロールバックが実行されます。
    
    処理フロー:
    1. ストレージからYAMLファイルを読み込み
    2. YAMLデータのバリデーション実行
    3. 既存メンバーの重複チェック
    4. 新規メンバーの作成とデータベース保存
    
    Args:
        yaml_path (str): ストレージ内のYAMLファイルパス（例: "data/human_members/田中太郎.yml"）
        
    Returns:
        HumanMember: 登録された人間メンバーオブジェクト（既存の場合は既存オブジェクト）
        
    Raises:
        ValidationError: YAMLデータのバリデーションに失敗した場合
        DatabaseError: データベース操作に失敗した場合
        Exception: その他の予期しないエラーが発生した場合
        
    Note:
        - 既存のメンバーが存在する場合は、新規作成せずに既存オブジェクトを返します
        - エラー時は自動的にデータベーストランザクションがロールバックされます
        - ストレージファイルが見つからない場合は専用のエラーメッセージが表示されます
    """
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

        # UPSERT操作でメンバーを登録または更新
        member = upsert_human_member(db, name, yaml_path)
        logger.info(f"Human member {name} upserted successfully from {yaml_path}")
        return member
        
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
    """YAMLファイルから仮想メンバーを登録する（バリデーション・ロールバック機能付き）
    
    ストレージから指定されたYAMLファイルを読み込み、バリデーションを実行した後、
    データベースに仮想メンバーとして登録します。エラーが発生した場合は
    自動的にロールバックが実行されます。
    
    処理フロー:
    1. ストレージからYAMLファイルを読み込み
    2. YAMLデータのバリデーション実行（name, llm_model必須）
    3. 既存メンバーの重複チェック
    4. 新規メンバーの作成とデータベース保存
    
    Args:
        yaml_path (str): ストレージ内のYAMLファイルパス（例: "data/virtual_members/AI助手.yml"）
        
    Returns:
        VirtualMember: 登録された仮想メンバーオブジェクト（既存の場合は既存オブジェクト）
        
    Raises:
        ValidationError: YAMLデータのバリデーションに失敗した場合
        DatabaseError: データベース操作に失敗した場合
        Exception: その他の予期しないエラーが発生した場合
        
    Note:
        - 既存のメンバーが存在する場合は、新規作成せずに既存オブジェクトを返します
        - エラー時は自動的にデータベーストランザクションがロールバックされます
        - ストレージファイルが見つからない場合は専用のエラーメッセージが表示されます
        - 仮想メンバーは人間メンバーより多くの必須フィールド（llm_model）が必要です
    """
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

        # UPSERT操作でメンバーを登録または更新
        member = upsert_virtual_member(db, name, yaml_path)
        logger.info(f"Virtual member {name} upserted successfully from {yaml_path}")
        return member
        
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
    """複数のYAMLファイルから人間メンバーをバッチ登録する（全成功または全ロールバック）
    
    指定された複数のYAMLファイルから人間メンバーを一括登録します。
    全てのファイルのバリデーションが成功した場合のみデータベースに保存し、
    一つでもエラーが発生した場合は全ての変更をロールバックします。
    
    処理フロー:
    1. 全てのYAMLファイルを事前にバリデーション
    2. バリデーション成功後、全てのメンバーを準備（まだコミットしない）
    3. 全ての処理が成功した場合のみ一括コミット
    4. エラー時は全変更をロールバック
    
    Args:
        yaml_paths (list): ストレージ内のYAMLファイルパスのリスト
        
    Returns:
        list: 登録された人間メンバーオブジェクトのリスト（既存メンバーも含む）
        
    Raises:
        ValidationError: いずれかのYAMLデータのバリデーションに失敗した場合
        DatabaseError: データベース操作に失敗した場合
        Exception: その他の予期しないエラーが発生した場合
        
    Note:
        - 既存のメンバーが存在する場合は、新規作成せずに既存オブジェクトをリストに含めます
        - エラー時は全ての変更がロールバックされます（アトミック操作）
        - バッチ処理のため、個別のファイル処理よりも効率的です
    """
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

            # UPSERT操作でメンバーを登録または更新（まだコミットしない）
            member = upsert_human_member(db, name, yaml_path)
            created_members.append(member)
            logger.info(f"Human member {name} prepared for upsert.")
        
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
    """複数のYAMLファイルから仮想メンバーをバッチ登録する（全成功または全ロールバック）
    
    指定された複数のYAMLファイルから仮想メンバーを一括登録します。
    全てのファイルのバリデーションが成功した場合のみデータベースに保存し、
    一つでもエラーが発生した場合は全ての変更をロールバックします。
    
    処理フロー:
    1. 全てのYAMLファイルを事前にバリデーション（name, llm_model必須）
    2. バリデーション成功後、全てのメンバーを準備（まだコミットしない）
    3. 全ての処理が成功した場合のみ一括コミット
    4. エラー時は全変更をロールバック
    
    Args:
        yaml_paths (list): ストレージ内のYAMLファイルパスのリスト
        
    Returns:
        list: 登録された仮想メンバーオブジェクトのリスト（既存メンバーも含む）
        
    Raises:
        ValidationError: いずれかのYAMLデータのバリデーションに失敗した場合
        DatabaseError: データベース操作に失敗した場合
        Exception: その他の予期しないエラーが発生した場合
        
    Note:
        - 既存のメンバーが存在する場合は、新規作成せずに既存オブジェクトをリストに含めます
        - エラー時は全ての変更がロールバックされます（アトミック操作）
        - バッチ処理のため、個別のファイル処理よりも効率的です
        - 仮想メンバーは人間メンバーより多くの必須フィールド（llm_model）が必要です
    """
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

            # UPSERT操作でメンバーを登録または更新（まだコミットしない）
            member = upsert_virtual_member(db, name, yaml_path)
            created_members.append(member)
            logger.info(f"Virtual member {name} prepared for upsert.")
        
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