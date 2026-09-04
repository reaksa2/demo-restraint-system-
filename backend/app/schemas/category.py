import uuid
from typing import Optional

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name_en: str
    name_kh: str
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name_en: Optional[str] = None
    name_kh: Optional[str] = None
    sort_order: Optional[int] = None


class CategoryOut(BaseModel):
    id: uuid.UUID
    brand_id: uuid.UUID
    name_en: str
    name_kh: str
    sort_order: int

    class Config:
        from_attributes = True
