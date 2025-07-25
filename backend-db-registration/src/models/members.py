from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import datetime
import uuid

from .base import Base

class HumanMember(Base):
    __tablename__ = "human_members"
    
    member_id = Column(Integer, primary_key=True)
    member_uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    member_name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC), onupdate=lambda: datetime.datetime.now(datetime.UTC))

    def __repr__(self):
        return f"<HumanMember(id={self.member_id}, name={self.member_name})>"

class VirtualMember(Base):
    __tablename__ = "virtual_members"
    
    member_id = Column(Integer, primary_key=True)
    member_uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    member_name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC), onupdate=lambda: datetime.datetime.now(datetime.UTC))

    def __repr__(self):
        return f"<VirtualMember(id={self.member_id}, name={self.member_name})>"

class MemberRelationship(Base):
    __tablename__ = "member_relationships"
    
    relationship_id = Column(Integer, primary_key=True)
    from_member_uuid = Column(UUID(as_uuid=True), nullable=False)
    to_member_uuid = Column(UUID(as_uuid=True), nullable=False)
    relationship_type = Column(String(50), nullable=False)
    name_suffix = Column(String(50))
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC), onupdate=lambda: datetime.datetime.now(datetime.UTC))
    
    # ユニーク制約の追加
    __table_args__ = (
        UniqueConstraint('from_member_uuid', 'to_member_uuid', 'relationship_type', name='unique_relationship'),
    )

    def __repr__(self):
        return f"<MemberRelationship(id={self.relationship_id}, type={self.relationship_type})>"