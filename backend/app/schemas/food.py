import uuid
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.food_price import FoodPriceAdminOut, SinglePriceOut


class FoodCreate(BaseModel):
    category_id: Optional[uuid.UUID] = None
    name_en: str
    name_kh: str
    description_en: Optional[str] = None
    description_kh: Optional[str] = None
    image_url: Optional[str] = None
    is_available: bool = True


class FoodUpdate(BaseModel):
    category_id: Optional[uuid.UUID] = None
    name_en: Optional[str] = None
    name_kh: Optional[str] = None
    description_en: Optional[str] = None
    description_kh: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None


class FoodAdminOut(BaseModel):
    """
    Admin (Level 2/3) view of a food — includes every zone's price.
    Only ever returned to authenticated admin roles, never to staff/public.
    """
    id: uuid.UUID
    brand_id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    name_en: str
    name_kh: str
    description_en: Optional[str] = None
    description_kh: Optional[str] = None
    image_url: Optional[str] = None
    is_available: bool
    prices: List[FoodPriceAdminOut] = []

    class Config:
        from_attributes = True


class FoodMenuOut(BaseModel):
    """
    Staff / public-facing menu view of a food.
    Contains exactly ONE price (resolved server-side for the caller's zone).
    """
    id: uuid.UUID
    name_en: str
    name_kh: str
    description_en: Optional[str] = None
    description_kh: Optional[str] = None
    image_url: Optional[str] = None
    is_available: bool
    category_id: Optional[uuid.UUID] = None
    price: Optional[SinglePriceOut] = None  # None only if no price configured for this zone yet
