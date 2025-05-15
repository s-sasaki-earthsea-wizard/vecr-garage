from sqlalchemy.orm import Session
from models.members import HumanMember, VirtualMember
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# データベース接続設定
DATABASE_URL = f"postgresql://{os.getenv('MEMBER_DB_USER')}:{os.getenv('MEMBER_DB_PASSWORD')}@{os.getenv('MEMBER_DB_HOST')}:{os.getenv('MEMBER_DB_PORT')}/{os.getenv('MEMBER_DB_NAME')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 人間メンバー操作
def create_human_member(db: Session, name: str):
    member_uuid = uuid.uuid4()
    db_member = HumanMember(member_name=name, member_uuid=member_uuid)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def get_human_member_by_name(db: Session, name: str):
    return db.query(HumanMember).filter(HumanMember.member_name == name).first()

# 仮想メンバー操作
def create_virtual_member(db: Session, name: str):
    member_uuid = uuid.uuid4()
    db_member = VirtualMember(
        member_name=name,
        member_uuid=member_uuid,
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def get_virtual_member_by_name(db: Session, name: str):
    return db.query(VirtualMember).filter(VirtualMember.member_name == name).first()