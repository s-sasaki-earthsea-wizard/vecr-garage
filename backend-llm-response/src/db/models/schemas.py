from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """SQLAlchemy Base class"""

    pass


class HumanMember(Base):
    __tablename__ = "human_members"

    member_id = Column(Integer, primary_key=True)
    member_uuid = Column(UUID, nullable=False, unique=True, server_default=func.uuid_generate_v4())
    member_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<HumanMember(id={self.member_id}, name={self.member_name})>"


class VirtualMember(Base):
    __tablename__ = "virtual_members"

    member_id = Column(Integer, primary_key=True)
    member_uuid = Column(UUID, nullable=False, unique=True, server_default=func.uuid_generate_v4())
    member_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<VirtualMember(id={self.member_id}, name={self.member_name})>"


class VirtualMemberProfile(Base):
    __tablename__ = "virtual_member_profiles"

    profile_id = Column(Integer, primary_key=True)
    profile_uuid = Column(UUID, nullable=False, unique=True, server_default=func.uuid_generate_v4())
    member_id = Column(Integer, ForeignKey("virtual_members.member_id"), nullable=False)
    member_uuid = Column(UUID, ForeignKey("virtual_members.member_uuid"), nullable=False, unique=True)
    llm_model = Column(String(50), nullable=False)
    custom_prompt = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # リレーションシップ
    virtual_member = relationship("VirtualMember", backref="profiles", foreign_keys=[member_uuid])

    def __repr__(self):
        return f"<VirtualMemberProfile(id={self.profile_id}, member_id={self.member_id})>"
