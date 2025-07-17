from sqlalchemy.orm import Session
from models.members import HumanMember, VirtualMember
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import os
import logging
import psycopg2

logger = logging.getLogger(__name__)

# データベース接続設定
DATABASE_URL = f"postgresql://{os.getenv('MEMBER_DB_USER')}:{os.getenv('MEMBER_DB_PASSWORD')}@{os.getenv('MEMBER_DB_HOST')}:{os.getenv('MEMBER_DB_PORT')}/{os.getenv('MEMBER_DB_NAME')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseError(Exception):
    """データベース操作エラーのカスタム例外"""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

# 人間メンバー操作
def create_human_member(db: Session, name: str):
    """人間メンバーを作成する"""
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
    """人間メンバーを作成してデータベースに保存する（完全なトランザクション管理）"""
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
    """名前で人間メンバーを取得する"""
    try:
        return db.query(HumanMember).filter(HumanMember.member_name == name).first()
    except Exception as e:
        error_msg = f"Failed to get human member '{name}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)

# 仮想メンバー操作
def create_virtual_member(db: Session, name: str):
    """仮想メンバーを作成する"""
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
    """仮想メンバーを作成してデータベースに保存する（完全なトランザクション管理）"""
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
    """名前で仮想メンバーを取得する"""
    try:
        return db.query(VirtualMember).filter(VirtualMember.member_name == name).first()
    except Exception as e:
        error_msg = f"Failed to get virtual member '{name}': {str(e)}"
        logger.error(error_msg)
        raise DatabaseError(error_msg, e)