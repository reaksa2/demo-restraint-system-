import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Food(Base):
    __tablename__ = "foods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    name_en = Column(String(255), nullable=False)
    name_kh = Column(String(255), nullable=False)
    description_en = Column(String(2000), nullable=True)
    description_kh = Column(String(2000), nullable=True)
    image_url = Column(String(1000), nullable=True)

    is_available = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    brand = relationship("Brand", back_populates="foods")
    category = relationship("Category", back_populates="foods")
    prices = relationship("FoodPrice", back_populates="food", cascade="all, delete-orphan")
