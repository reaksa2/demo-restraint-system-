import uuid
from typing import Optional

from pydantic import BaseModel


class ZoneCreate(BaseModel):
    name_en: str
    name_kh: str


class ZoneUpdate(BaseModel):
    name_en: Optional[str] = None
    name_kh: Optional[str] = None


class ZoneOut(BaseModel):
    id: uuid.UUID
    brand_id: uuid.UUID
    name_en: str
    name_kh: str

    class Config:
        from_attributes = True
