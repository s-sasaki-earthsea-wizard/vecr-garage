from sqlalchemy.orm import Session
from models.members import HumanMember, VirtualMember, HumanMemberProfile, VirtualMemberProfile
import uuid
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import datetime
import os
import logging
import psycopg2

logger = logging.getLogger(__name__)

# データベース接続設定
DATABASE_URL = f"postgresql://{os.getenv('MEMBER_DB_USER')}:{os.getenv('MEMBER_DB_PASSWORD')}@{os.getenv('MEMBER_DB_HOST')}:{os.getenv('MEMBER_DB_PORT')}/{os.getenv('MEMBER_DB_NAME')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseError(Exception):
    """データベース操作時に発生するカスタム例外クラス
    
    データベースの接続エラー、SQL実行エラー、トランザクションエラーなど
    データベース関連のエラーを統一的に扱うために使用されます。
    
    Attributes:
        message (str): エラーメッセージ
        original_error (Exception): 元の例外オブジェクト（デバッグ用）
    """
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

# 人間メンバー操作
def create_human_member(db: Session, name: str, yml_file_uri: str = None):
    """人間メンバーのデータベースオブジェクトを作成する
    
    新しいUUIDを生成し、指定された名前でHumanMemberオブジェクトを作成します。
    この関数はデータベースへの保存は行わず、オブジェクトの作成のみを行います。
    
    Args:
        db (Session): SQLAlchemyのデータベースセッション
        name (str): 人間メンバーの名前
        
    Returns:
        HumanMember: 作成された人間メンバーオブジェクト
        
    Raises:
        DatabaseError: オブジェクト作成時にエラーが発生した場合
        
    Example:
        >>> member = create_human_member(db, "田中太郎")
        >>> print(member.member_name)  # "田中太郎"
        >>> print(member.member_uuid)  # UUID文字列
    """
    try:
        member_uuid = uuid.uuid4()
        db_member = HumanMember(member_name=name, member_uuid=member_uuid, yml_file_uri=yml_file_uri)
        logger.info(f"Human member '{name}' created with UUID: {member_uuid}")
        return db_member
    except Exception as e:
        error_msg = f"Failed to create human member '{name}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def save_human_member(db: Session, name: str, yml_file_uri: str = None):
    """人間メンバーを作成してデータベースに保存する（完全なトランザクション管理）
    
    人間メンバーオブジェクトを作成し、データベースに保存します。
    エラーが発生した場合は自動的にロールバックを行い、
    成功した場合はコミットしてオブジェクトをリフレッシュします。
    
    Args:
        db (Session): SQLAlchemyのデータベースセッション
        name (str): 人間メンバーの名前
        
    Returns:
        HumanMember: 保存された人間メンバーオブジェクト（IDが設定済み）
        
    Raises:
        DatabaseError: 保存時にエラーが発生した場合（ロールバック済み）
        
    Note:
        この関数は完全なトランザクション管理を行います。
        エラー時は自動的にロールバックが実行されます。
    """
    try:
        member = create_human_member(db, name, yml_file_uri)
        db.add(member)
        db.commit()
        db.refresh(member)
        logger.info(f"Human member '{name}' created and saved successfully")
        return member
    except Exception as e:
        db.rollback()
        error_msg = f"Failed to save human member '{name}': {str(e)}. Database transaction has been rolled back."
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def get_human_member_by_name(db: Session, name: str):
    """名前で人間メンバーをデータベースから取得する

    指定された名前の人間メンバーを検索し、見つかった場合は
    そのオブジェクトを返します。見つからない場合はNoneを返します。

    Args:
        db (Session): SQLAlchemyのデータベースセッション
        name (str): 検索する人間メンバーの名前

    Returns:
        HumanMember or None: 見つかった人間メンバーオブジェクト、またはNone

    Raises:
        DatabaseError: データベース検索時にエラーが発生した場合

    Example:
        >>> member = get_human_member_by_name(db, "田中太郎")
        >>> if member:
        ...     print(f"Found: {member.member_name}")
        ... else:
        ...     print("Member not found")
    """
    try:
        return db.query(HumanMember).filter(HumanMember.member_name == name).first()
    except Exception as e:
        error_msg = f"Failed to get human member '{name}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def get_human_member_by_uri(db: Session, yml_file_uri: str):
    """YAMLファイルURIで人間メンバーをデータベースから取得する

    指定されたYAMLファイルURIの人間メンバーを検索し、見つかった場合は
    そのオブジェクトを返します。見つからない場合はNoneを返します。

    Args:
        db (Session): SQLAlchemyのデータベースセッション
        yml_file_uri (str): 検索するYAMLファイルURI

    Returns:
        HumanMember or None: 見つかった人間メンバーオブジェクト、またはNone

    Raises:
        DatabaseError: データベース検索時にエラーが発生した場合
    """
    try:
        return db.query(HumanMember).filter(HumanMember.yml_file_uri == yml_file_uri).first()
    except Exception as e:
        error_msg = f"Failed to get human member by URI '{yml_file_uri}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def upsert_human_member(db: Session, name: str, yml_file_uri: str):
    """人間メンバーをUPSERT（存在すれば更新、存在しなければ挿入）する

    指定されたYAMLファイルURIの人間メンバーが存在する場合は更新し、
    存在しない場合は新規作成します。

    Args:
        db (Session): SQLAlchemyのデータベースセッション
        name (str): 人間メンバーの名前
        yml_file_uri (str): YAMLファイルURI

    Returns:
        HumanMember: UPSERT処理後の人間メンバーオブジェクト

    Raises:
        DatabaseError: UPSERT処理時にエラーが発生した場合
    """
    try:
        # URIで既存メンバーを検索
        existing_member = get_human_member_by_uri(db, yml_file_uri)

        if existing_member:
            # 既存メンバーを更新
            existing_member.member_name = name
            existing_member.updated_at = db.query(func.current_timestamp()).scalar()
            db.commit()
            db.refresh(existing_member)
            logger.info(f"Human member '{name}' updated for URI: {yml_file_uri}")
            return existing_member
        else:
            # 新規メンバーを作成
            member = create_human_member(db, name, yml_file_uri)
            db.add(member)
            db.commit()
            db.refresh(member)
            logger.info(f"Human member '{name}' created for URI: {yml_file_uri}")
            return member

    except Exception as e:
        db.rollback()
        error_msg = f"Failed to upsert human member '{name}' for URI '{yml_file_uri}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

# 仮想メンバー操作
def create_virtual_member(db: Session, name: str, yml_file_uri: str = None):
    """仮想メンバーのデータベースオブジェクトを作成する
    
    新しいUUIDを生成し、指定された名前でVirtualMemberオブジェクトを作成します。
    この関数はデータベースへの保存は行わず、オブジェクトの作成のみを行います。
    
    Args:
        db (Session): SQLAlchemyのデータベースセッション
        name (str): 仮想メンバーの名前
        
    Returns:
        VirtualMember: 作成された仮想メンバーオブジェクト
        
    Raises:
        DatabaseError: オブジェクト作成時にエラーが発生した場合
        
    Example:
        >>> member = create_virtual_member(db, "AI助手")
        >>> print(member.member_name)  # "AI助手"
        >>> print(member.member_uuid)  # UUID文字列
    """
    try:
        member_uuid = uuid.uuid4()
        db_member = VirtualMember(
            member_name=name,
            member_uuid=member_uuid,
            yml_file_uri=yml_file_uri
        )
        logger.info(f"Virtual member '{name}' created with UUID: {member_uuid}")
        return db_member
    except Exception as e:
        error_msg = f"Failed to create virtual member '{name}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def save_virtual_member(db: Session, name: str, yml_file_uri: str = None):
    """仮想メンバーを作成してデータベースに保存する（完全なトランザクション管理）
    
    仮想メンバーオブジェクトを作成し、データベースに保存します。
    エラーが発生した場合は自動的にロールバックを行い、
    成功した場合はコミットしてオブジェクトをリフレッシュします。
    
    Args:
        db (Session): SQLAlchemyのデータベースセッション
        name (str): 仮想メンバーの名前
        
    Returns:
        VirtualMember: 保存された仮想メンバーオブジェクト（IDが設定済み）
        
    Raises:
        DatabaseError: 保存時にエラーが発生した場合（ロールバック済み）
        
    Note:
        この関数は完全なトランザクション管理を行います。
        エラー時は自動的にロールバックが実行されます。
    """
    try:
        member = create_virtual_member(db, name, yml_file_uri)
        db.add(member)
        db.commit()
        db.refresh(member)
        logger.info(f"Virtual member '{name}' created and saved successfully")
        return member
    except Exception as e:
        db.rollback()
        error_msg = f"Failed to save virtual member '{name}': {str(e)}. Database transaction has been rolled back."
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def get_virtual_member_by_name(db: Session, name: str):
    """名前で仮想メンバーをデータベースから取得する

    指定された名前の仮想メンバーを検索し、見つかった場合は
    そのオブジェクトを返します。見つからない場合はNoneを返します。

    Args:
        db (Session): SQLAlchemyのデータベースセッション
        name (str): 検索する仮想メンバーの名前

    Returns:
        VirtualMember or None: 見つかった仮想メンバーオブジェクト、またはNone

    Raises:
        DatabaseError: データベース検索時にエラーが発生した場合

    Example:
        >>> member = get_virtual_member_by_name(db, "AI助手")
        >>> if member:
        ...     print(f"Found: {member.member_name}")
        ... else:
        ...     print("Member not found")
    """
    try:
        return db.query(VirtualMember).filter(VirtualMember.member_name == name).first()
    except Exception as e:
        error_msg = f"Failed to get virtual member '{name}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def get_virtual_member_by_uri(db: Session, yml_file_uri: str):
    """YAMLファイルURIで仮想メンバーをデータベースから取得する

    指定されたYAMLファイルURIの仮想メンバーを検索し、見つかった場合は
    そのオブジェクトを返します。見つからない場合はNoneを返します。

    Args:
        db (Session): SQLAlchemyのデータベースセッション
        yml_file_uri (str): 検索するYAMLファイルURI

    Returns:
        VirtualMember or None: 見つかった仮想メンバーオブジェクト、またはNone

    Raises:
        DatabaseError: データベース検索時にエラーが発生した場合
    """
    try:
        return db.query(VirtualMember).filter(VirtualMember.yml_file_uri == yml_file_uri).first()
    except Exception as e:
        error_msg = f"Failed to get virtual member by URI '{yml_file_uri}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def upsert_virtual_member(db: Session, name: str, yml_file_uri: str):
    """仮想メンバーをUPSERT（存在すれば更新、存在しなければ挿入）する

    指定されたYAMLファイルURIの仮想メンバーが存在する場合は更新し、
    存在しない場合は新規作成します。

    Args:
        db (Session): SQLAlchemyのデータベースセッション
        name (str): 仮想メンバーの名前
        yml_file_uri (str): YAMLファイルURI

    Returns:
        VirtualMember: UPSERT処理後の仮想メンバーオブジェクト

    Raises:
        DatabaseError: UPSERT処理時にエラーが発生した場合
    """
    try:
        # URIで既存メンバーを検索
        existing_member = get_virtual_member_by_uri(db, yml_file_uri)

        if existing_member:
            # 既存メンバーを更新
            existing_member.member_name = name
            existing_member.updated_at = db.query(func.current_timestamp()).scalar()
            db.commit()
            db.refresh(existing_member)
            logger.info(f"Virtual member '{name}' updated for URI: {yml_file_uri}")
            return existing_member
        else:
            # 新規メンバーを作成
            member = create_virtual_member(db, name, yml_file_uri)
            db.add(member)
            db.commit()
            db.refresh(member)
            logger.info(f"Virtual member '{name}' created for URI: {yml_file_uri}")
            return member

    except Exception as e:
        db.rollback()
        error_msg = f"Failed to upsert virtual member '{name}' for URI '{yml_file_uri}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

# プロフィール操作
def save_human_member_profile(db: Session, member_id: int, member_uuid: str, bio: str = None):
    """人間メンバープロフィールを新規作成する"""
    try:
        profile = HumanMemberProfile(
            member_id=member_id,
            member_uuid=member_uuid,
            bio=bio
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    except Exception as e:
        db.rollback()
        error_msg = f"Failed to create human member profile for member {member_uuid}: {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def upsert_human_member_profile(db: Session, member_id: int, member_uuid: str, bio: str = None):
    """人間メンバープロフィールのUPSERT処理"""
    try:
        existing_profile = db.query(HumanMemberProfile).filter(
            HumanMemberProfile.member_uuid == member_uuid
        ).first()

        if existing_profile:
            # 更新処理
            if bio is not None:
                existing_profile.bio = bio
            existing_profile.updated_at = datetime.datetime.now(datetime.UTC)
            db.commit()
            db.refresh(existing_profile)
            return existing_profile
        else:
            # 新規作成
            return save_human_member_profile(db, member_id, member_uuid, bio)
    except Exception as e:
        db.rollback()
        error_msg = f"Failed to upsert human member profile for member {member_uuid}: {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def save_virtual_member_profile(db: Session, member_id: int, member_uuid: str, llm_model: str, custom_prompt: str = None):
    """仮想メンバープロフィールを新規作成する"""
    try:
        profile = VirtualMemberProfile(
            member_id=member_id,
            member_uuid=member_uuid,
            llm_model=llm_model,
            custom_prompt=custom_prompt
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    except Exception as e:
        db.rollback()
        error_msg = f"Failed to create virtual member profile for member {member_uuid}: {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def upsert_virtual_member_profile(db: Session, member_id: int, member_uuid: str, llm_model: str, custom_prompt: str = None):
    """仮想メンバープロフィールのUPSERT処理"""
    try:
        existing_profile = db.query(VirtualMemberProfile).filter(
            VirtualMemberProfile.member_uuid == member_uuid
        ).first()

        if existing_profile:
            # 更新処理
            if llm_model is not None:
                existing_profile.llm_model = llm_model
            if custom_prompt is not None:
                existing_profile.custom_prompt = custom_prompt
            existing_profile.updated_at = datetime.datetime.now(datetime.UTC)
            db.commit()
            db.refresh(existing_profile)
            return existing_profile
        else:
            # 新規作成
            return save_virtual_member_profile(db, member_id, member_uuid, llm_model, custom_prompt)
    except Exception as e:
        db.rollback()
        error_msg = f"Failed to upsert virtual member profile for member {member_uuid}: {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)