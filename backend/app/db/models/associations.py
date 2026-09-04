import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class UserGroup(Base):
    """
    LEVEL2 users are linked to exactly one group through this table.
    (Modeled as many-to-many at the DB level, but the API enforces
    exactly one active row per LEVEL2 user.)
    """
    __tablename__ = "user_groups"
    __table_args__ = (
        UniqueConstraint("user_id", "group_id", name="uq_user_group"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="group_links")
    group = relationship("Group", back_populates="user_links")


class UserBrand(Base):
    """
    LEVEL3 users: one row, zone_id is NULL (they manage the whole brand, not one zone).
    STAFF users: one row, zone_id is REQUIRED (determines which price they/customers see).
    A user should only ever have rows in user_groups OR user_brands, never both —
    enforced in the service/permissions layer, not the DB, to keep this table simple.
    """
    __tablename__ = "user_brands"
    __table_args__ = (
        UniqueConstraint("user_id", "brand_id", name="uq_user_brand"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="brand_links")
    brand = relationship("Brand", back_populates="user_links")
    zone = relationship("Zone", back_populates="staff_links")
