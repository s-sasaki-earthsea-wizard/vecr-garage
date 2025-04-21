from sqlalchemy.orm import Session
from src.models.members import HumanMember, VirtualMember
import uuid

# 人間メンバー操作
def create_human_member(db: Session, name: str, bio: str = None):
    member_uuid = uuid.uuid4()
    db_member = HumanMember(member_name=name, member_uuid=member_uuid, bio=bio)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def get_human_member_by_name(db: Session, name: str):
    return db.query(HumanMember).filter(HumanMember.member_name == name).first()

# 仮想メンバー操作
def create_virtual_member(db: Session, name: str, llm_model: str, custom_prompt: str = None):
    member_uuid = uuid.uuid4()
    db_member = VirtualMember(
        member_name=name,
        member_uuid=member_uuid,
        llm_model=llm_model,
        custom_prompt=custom_prompt
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def get_virtual_member_by_name(db: Session, name: str):
    return db.query(VirtualMember).filter(VirtualMember.member_name == name).first()