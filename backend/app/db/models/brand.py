import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)

    # Used in the public menu URL, e.g. /menu/abc
    slug = Column(String(255), unique=True, nullable=False, index=True)

    name_en = Column(String(255), nullable=False)
    name_kh = Column(String(255), nullable=False)
    description_en = Column(String(2000), nullable=True)
    description_kh = Column(String(2000), nullable=True)
    logo_url = Column(String(1000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    group = relationship("Group", back_populates="brands")
    zones = relationship("Zone", back_populates="brand", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="brand", cascade="all, delete-orphan")
    foods = relationship("Food", back_populates="brand", cascade="all, delete-orphan")
    user_links = relationship("UserBrand", back_populates="brand", cascade="all, delete-orphan")
