import uuid
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class FoodPriceUpsert(BaseModel):
    """Used by admin (Level 2/3) to set a food's price for one zone."""
    zone_id: uuid.UUID
    regular_price: Decimal
    discount_price: Optional[Decimal] = None
    discount_active: bool = False


class FoodPriceAdminOut(BaseModel):
    """
    Admin-only view: shows every zone's price for a food.
    NEVER reuse this schema for staff or public menu endpoints.
    """
    id: uuid.UUID
    zone_id: uuid.UUID
    zone_name_en: str
    zone_name_kh: str
    regular_price: Decimal
    discount_price: Optional[Decimal] = None
    discount_active: bool

    class Config:
        from_attributes = True


class SinglePriceOut(BaseModel):
    """
    Staff / public menu view: exactly one resolved price for the caller's
    zone. No other zone's price is ever present on this object.
    """
    price: Decimal
    is_discounted: bool
