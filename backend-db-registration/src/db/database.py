import logging
import os
import uuid

from models.members import (
    HumanMember,
    HumanMemberProfile,
    VirtualMember,
    VirtualMemberProfile,
)
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

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
        db_member = HumanMember(
            member_name=name, member_uuid=member_uuid, yml_file_uri=yml_file_uri
        )
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
    """人間メンバーをUPSERT（ON CONFLICT DO UPDATE使用）

    PostgreSQLのON CONFLICT DO UPDATE機能を使用して、
    単一のSQL文でINSERT/UPDATEを統一処理します。

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
        from sqlalchemy import text

        # ON CONFLICT DO UPDATEでINSERT/UPDATEを一元化
        sql = text(
            """
            INSERT INTO human_members (member_name, yml_file_uri, member_uuid, created_at, updated_at)
            VALUES (:name, :yml_file_uri, gen_random_uuid(), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (yml_file_uri)
            DO UPDATE SET
                member_name = EXCLUDED.member_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING member_id, member_uuid, member_name, yml_file_uri, created_at, updated_at
        """
        )

        result = db.execute(sql, {"name": name, "yml_file_uri": yml_file_uri})
        row = result.fetchone()

        # 結果からHumanMemberオブジェクトを構築
        member = HumanMember(
            member_id=row.member_id,
            member_uuid=row.member_uuid,
            member_name=row.member_name,
            yml_file_uri=row.yml_file_uri,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

        logger.info(f"Human member '{name}' upserted for URI: {yml_file_uri}")
        return member

    except Exception as e:
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
            member_name=name, member_uuid=member_uuid, yml_file_uri=yml_file_uri
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
    """仮想メンバーをUPSERT（ON CONFLICT DO UPDATE使用）

    PostgreSQLのON CONFLICT DO UPDATE機能を使用して、
    単一のSQL文でINSERT/UPDATEを統一処理します。

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
        from sqlalchemy import text

        # ON CONFLICT DO UPDATEでINSERT/UPDATEを一元化
        sql = text(
            """
            INSERT INTO virtual_members (member_name, yml_file_uri, member_uuid, created_at, updated_at)
            VALUES (:name, :yml_file_uri, gen_random_uuid(), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (yml_file_uri)
            DO UPDATE SET
                member_name = EXCLUDED.member_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING member_id, member_uuid, member_name, yml_file_uri, created_at, updated_at
        """
        )

        result = db.execute(sql, {"name": name, "yml_file_uri": yml_file_uri})
        row = result.fetchone()

        # 結果からVirtualMemberオブジェクトを構築
        member = VirtualMember(
            member_id=row.member_id,
            member_uuid=row.member_uuid,
            member_name=row.member_name,
            yml_file_uri=row.yml_file_uri,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

        logger.info(f"Virtual member '{name}' upserted for URI: {yml_file_uri}")
        return member

    except Exception as e:
        error_msg = f"Failed to upsert virtual member '{name}' for URI '{yml_file_uri}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)


# プロフィール操作
def upsert_human_member_profile(db: Session, member_id: int, member_uuid: str, bio: str = None):
    """人間メンバープロフィールのUPSERT処理（ON CONFLICT DO UPDATE使用）"""
    try:
        sql = text(
            """
            INSERT INTO human_member_profiles (member_id, member_uuid, bio, profile_uuid, created_at, updated_at)
            VALUES (:member_id, :member_uuid, :bio, gen_random_uuid(), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (member_uuid)
            DO UPDATE SET
                member_id = EXCLUDED.member_id,
                bio = EXCLUDED.bio,
                updated_at = CURRENT_TIMESTAMP
            RETURNING profile_id, member_id, member_uuid, bio, profile_uuid, created_at, updated_at
        """
        )

        result = db.execute(sql, {"member_id": member_id, "member_uuid": member_uuid, "bio": bio})
        row = result.fetchone()

        # 結果からHumanMemberProfileオブジェクトを構築
        profile = HumanMemberProfile(
            profile_id=row.profile_id,
            profile_uuid=row.profile_uuid,
            member_id=row.member_id,
            member_uuid=row.member_uuid,
            bio=row.bio,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

        logger.info(f"Human member profile upserted for member {member_uuid}")
        return profile

    except Exception as e:
        # NOTE: ロールバックは呼び出し元で実行
        error_msg = f"Failed to upsert human member profile for member {member_uuid}: {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)


def upsert_virtual_member_profile(
    db: Session,
    member_id: int,
    member_uuid: str,
    llm_model: str,
    custom_prompt: str = None,
):
    """仮想メンバープロフィールのUPSERT処理（ON CONFLICT DO UPDATE使用）"""
    try:
        sql = text(
            """
            INSERT INTO virtual_member_profiles (member_id, member_uuid, llm_model, custom_prompt, profile_uuid, created_at, updated_at)
            VALUES (:member_id, :member_uuid, :llm_model, :custom_prompt, gen_random_uuid(), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (member_uuid)
            DO UPDATE SET
                member_id = EXCLUDED.member_id,
                llm_model = EXCLUDED.llm_model,
                custom_prompt = EXCLUDED.custom_prompt,
                updated_at = CURRENT_TIMESTAMP
            RETURNING profile_id, member_id, member_uuid, llm_model, custom_prompt, profile_uuid, created_at, updated_at
        """
        )

        result = db.execute(
            sql,
            {
                "member_id": member_id,
                "member_uuid": member_uuid,
                "llm_model": llm_model,
                "custom_prompt": custom_prompt,
            },
        )
        row = result.fetchone()

        # 結果からVirtualMemberProfileオブジェクトを構築
        profile = VirtualMemberProfile(
            profile_id=row.profile_id,
            profile_uuid=row.profile_uuid,
            member_id=row.member_id,
            member_uuid=row.member_uuid,
            llm_model=row.llm_model,
            custom_prompt=row.custom_prompt,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

        logger.info(f"Virtual member profile upserted for member {member_uuid}")
        return profile

    except Exception as e:
        # NOTE: ロールバックは呼び出し元で実行
        error_msg = f"Failed to upsert virtual member profile for member {member_uuid}: {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)
