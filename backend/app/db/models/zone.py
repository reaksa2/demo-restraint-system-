import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Zone(Base):
    """
    Zones belong to a single brand (e.g. Brand A has INSIDE/OUTSIDE).
    Staff and food_prices are always scoped to a zone within one brand.
    """
    __tablename__ = "zones"
    __table_args__ = (
        UniqueConstraint("brand_id", "name_en", name="uq_zone_brand_name"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)

    name_en = Column(String(100), nullable=False)   # e.g. "Inside"
    name_kh = Column(String(100), nullable=False)   # e.g. "ខាងក្នុង"

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    brand = relationship("Brand", back_populates="zones")
    food_prices = relationship("FoodPrice", back_populates="zone", cascade="all, delete-orphan")
    staff_links = relationship("UserBrand", back_populates="zone")
