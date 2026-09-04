import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class FoodPrice(Base):
    """
    One food has exactly one price row per zone.
    This is the ONLY place a customer/staff-facing price ever comes from,
    and API responses must always resolve to a single row (the caller's zone)
    before serializing — never send a food's full price list to staff/customers.
    """
    __tablename__ = "food_prices"
    __table_args__ = (
        UniqueConstraint("food_id", "zone_id", name="uq_food_zone_price"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    food_id = Column(UUID(as_uuid=True), ForeignKey("foods.id", ondelete="CASCADE"), nullable=False)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False)

    regular_price = Column(Numeric(10, 2), nullable=False)
    discount_price = Column(Numeric(10, 2), nullable=True)
    discount_active = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    food = relationship("Food", back_populates="prices")
    zone = relationship("Zone", back_populates="food_prices")

    @property
    def effective_price(self):
        """The single price that should ever be shown to staff/customers."""
        if self.discount_active and self.discount_price is not None:
            return self.discount_price
        return self.regular_price
