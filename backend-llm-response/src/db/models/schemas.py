from sqlalchemy import Column, Integer, String, DateTime, UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class HumanMember(Base):
    __tablename__ = "human_members"

    member_id = Column(Integer, primary_key=True)
    member_uuid = Column(UUID, nullable=False, unique=True, 
                  server_default=func.uuid_generate_v4())
    member_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
