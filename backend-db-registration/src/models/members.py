import datetime
import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class HumanMember(Base):
    __tablename__ = "human_members"

    member_id = Column(Integer, primary_key=True)
    member_uuid = Column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4
    )
    member_name = Column(String(50), unique=True, nullable=False)
    yml_file_uri = Column(String(500), unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )

    def __repr__(self):
        return f"<HumanMember(id={self.member_id}, name={self.member_name})>"


class VirtualMember(Base):
    __tablename__ = "virtual_members"

    member_id = Column(Integer, primary_key=True)
    member_uuid = Column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4
    )
    member_name = Column(String(50), unique=True, nullable=False)
    yml_file_uri = Column(String(500), unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )

    def __repr__(self):
        return f"<VirtualMember(id={self.member_id}, name={self.member_name})>"


class HumanMemberProfile(Base):
    __tablename__ = "human_member_profiles"

    profile_id = Column(Integer, primary_key=True)
    profile_uuid = Column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4
    )
    member_id = Column(Integer, ForeignKey("human_members.member_id"), nullable=False)
    member_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("human_members.member_uuid"),
        nullable=False,
        unique=True,
    )
    bio = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )

    # リレーションシップ（foreign_keysを明示的に指定）
    human_member = relationship(
        "HumanMember", backref="profiles", foreign_keys=[member_uuid]
    )

    def __repr__(self):
        return f"<HumanMemberProfile(id={self.profile_id}, member_id={self.member_id})>"


class VirtualMemberProfile(Base):
    __tablename__ = "virtual_member_profiles"

    profile_id = Column(Integer, primary_key=True)
    profile_uuid = Column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4
    )
    member_id = Column(Integer, ForeignKey("virtual_members.member_id"), nullable=False)
    member_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("virtual_members.member_uuid"),
        nullable=False,
        unique=True,
    )
    llm_model = Column(String(50), nullable=False)
    custom_prompt = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )

    # リレーションシップ（foreign_keysを明示的に指定）
    virtual_member = relationship(
        "VirtualMember", backref="profiles", foreign_keys=[member_uuid]
    )

    def __repr__(self):
        return (
            f"<VirtualMemberProfile(id={self.profile_id}, member_id={self.member_id})>"
        )


class MemberRelationship(Base):
    __tablename__ = "member_relationships"

    relationship_id = Column(Integer, primary_key=True)
    from_member_uuid = Column(UUID(as_uuid=True), nullable=False)
    to_member_uuid = Column(UUID(as_uuid=True), nullable=False)
    relationship_type = Column(String(50), nullable=False)
    name_suffix = Column(String(50))
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )

    # ユニーク制約の追加
    __table_args__ = (
        UniqueConstraint(
            "from_member_uuid",
            "to_member_uuid",
            "relationship_type",
            name="unique_relationship",
        ),
    )

    def __repr__(self):
        return f"<MemberRelationship(id={self.relationship_id}, type={self.relationship_type})>"
