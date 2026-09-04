import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_scope
from app.core.permissions import assert_can_manage_brand_content, assert_brand_access
from app.db.database import get_db
from app.db.models.zone import Zone
from app.db.models.brand import Brand
from app.schemas.zone import ZoneCreate, ZoneUpdate, ZoneOut

router = APIRouter(prefix="/api/brands/{brand_id}/zones", tags=["zones"])


def _get_brand_or_404(db: Session, brand_id: uuid.UUID) -> Brand:
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    return brand


@router.get("", response_model=list[ZoneOut])
def list_zones(brand_id: uuid.UUID, scope: dict = Depends(get_current_user_scope), db: Session = Depends(get_db)):
    assert_brand_access(db, scope["user"], brand_id, allow_staff=True)
    _get_brand_or_404(db, brand_id)
    return db.query(Zone).filter(Zone.brand_id == brand_id).order_by(Zone.name_en).all()


@router.post("", response_model=ZoneOut, status_code=status.HTTP_201_CREATED)
def create_zone(
    brand_id: uuid.UUID,
    payload: ZoneCreate,
    scope: dict = Depends(get_current_user_scope),
    db: Session = Depends(get_db),
):
    assert_can_manage_brand_content(db, scope["user"], brand_id)
    _get_brand_or_404(db, brand_id)

    if db.query(Zone).filter(Zone.brand_id == brand_id, Zone.name_en == payload.name_en).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Zone name already exists for this brand")

    zone = Zone(brand_id=brand_id, **payload.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.put("/{zone_id}", response_model=ZoneOut)
def update_zone(
    brand_id: uuid.UUID,
    zone_id: uuid.UUID,
    payload: ZoneUpdate,
    scope: dict = Depends(get_current_user_scope),
    db: Session = Depends(get_db),
):
    assert_can_manage_brand_content(db, scope["user"], brand_id)
    zone = db.query(Zone).filter(Zone.id == zone_id, Zone.brand_id == brand_id).first()
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(zone, field, value)

    db.commit()
    db.refresh(zone)
    return zone


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(
    brand_id: uuid.UUID,
    zone_id: uuid.UUID,
    scope: dict = Depends(get_current_user_scope),
    db: Session = Depends(get_db),
):
    assert_can_manage_brand_content(db, scope["user"], brand_id)
    zone = db.query(Zone).filter(Zone.id == zone_id, Zone.brand_id == brand_id).first()
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    db.delete(zone)
    db.commit()
