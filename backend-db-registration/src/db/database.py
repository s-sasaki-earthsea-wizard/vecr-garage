from sqlalchemy.orm import Session
from models.members import HumanMember, VirtualMember
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
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
def create_human_member(db: Session, name: str):
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
        db_member = HumanMember(member_name=name, member_uuid=member_uuid)
        logger.info(f"Human member '{name}' created with UUID: {member_uuid}")
        return db_member
    except Exception as e:
        error_msg = f"Failed to create human member '{name}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def save_human_member(db: Session, name: str):
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
        member = create_human_member(db, name)
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

# 仮想メンバー操作
def create_virtual_member(db: Session, name: str):
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
        )
        logger.info(f"Virtual member '{name}' created with UUID: {member_uuid}")
        return db_member
    except Exception as e:
        error_msg = f"Failed to create virtual member '{name}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def save_virtual_member(db: Session, name: str):
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
        member = create_virtual_member(db, name)
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

# 一時的なUPSERT機能（将来的にfile_uriベースの実装に移行予定）
# TODO: 将来的にfile_uriをプライマリーキーとした本格的なUPSERT実装に移行する
# Issue: https://github.com/your-org/vecr-garage/issues/xxx

def save_or_update_human_member(db: Session, name: str):
    """人間メンバーを保存または更新する（一時的なUPSERT実装）

    指定された名前の人間メンバーが既に存在する場合は更新（updated_atフィールド）し、
    存在しない場合は新規作成します。この実装は一時的なもので、将来的には
    file_uriをプライマリーキーとしたより適切なUPSERT実装に移行予定です。

    Args:
        db (Session): SQLAlchemyのデータベースセッション
        name (str): 人間メンバーの名前

    Returns:
        HumanMember: 保存または更新された人間メンバーオブジェクト

    Raises:
        DatabaseError: データベース操作時にエラーが発生した場合

    Note:
        【一時的な実装】この関数は名前ベースの重複チェックを行います。
        将来的には以下の仕様に移行予定:
        - file_uriをプライマリーキーとして使用
        - ON CONFLICT DO UPDATEによる本格的なUPSERT
        - より厳密なファイルベースの管理
    """
    try:
        # 既存のメンバーをチェック
        existing_member = get_human_member_by_name(db, name)

        if existing_member:
            # 更新: updated_atフィールドを現在時刻に更新
            existing_member.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_member)
            logger.info(f"Human member '{name}' updated successfully (updated_at: {existing_member.updated_at})")
            return existing_member
        else:
            # 新規作成
            new_member = save_human_member(db, name)
            logger.info(f"Human member '{name}' created successfully")
            return new_member

    except Exception as e:
        db.rollback()
        error_msg = f"Failed to save or update human member '{name}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

def save_or_update_virtual_member(db: Session, name: str):
    """仮想メンバーを保存または更新する（一時的なUPSERT実装）

    指定された名前の仮想メンバーが既に存在する場合は更新（updated_atフィールド）し、
    存在しない場合は新規作成します。この実装は一時的なもので、将来的には
    file_uriをプライマリーキーとしたより適切なUPSERT実装に移行予定です。

    Args:
        db (Session): SQLAlchemyのデータベースセッション
        name (str): 仮想メンバーの名前

    Returns:
        VirtualMember: 保存または更新された仮想メンバーオブジェクト

    Raises:
        DatabaseError: データベース操作時にエラーが発生した場合

    Note:
        【一時的な実装】この関数は名前ベースの重複チェックを行います。
        将来的には以下の仕様に移行予定:
        - file_uriをプライマリーキーとして使用
        - ON CONFLICT DO UPDATEによる本格的なUPSERT
        - より厳密なファイルベースの管理
    """
    try:
        # 既存のメンバーをチェック
        existing_member = get_virtual_member_by_name(db, name)

        if existing_member:
            # 更新: updated_atフィールドを現在時刻に更新
            existing_member.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_member)
            logger.info(f"Virtual member '{name}' updated successfully (updated_at: {existing_member.updated_at})")
            return existing_member
        else:
            # 新規作成
            new_member = save_virtual_member(db, name)
            logger.info(f"Virtual member '{name}' created successfully")
            return new_member

    except Exception as e:
        db.rollback()
        error_msg = f"Failed to save or update virtual member '{name}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)