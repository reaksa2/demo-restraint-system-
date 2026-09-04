import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_scope
from app.core.permissions import assert_can_manage_brand_content
from app.db.database import get_db
from app.db.models.food import Food
from app.db.models.zone import Zone
from app.db.models.food_price import FoodPrice
from app.schemas.food_price import FoodPriceUpsert, FoodPriceAdminOut

router = APIRouter(prefix="/api/brands/{brand_id}/foods/{food_id}/prices", tags=["prices"])


@router.put("", response_model=FoodPriceAdminOut)
def upsert_price(
    brand_id: uuid.UUID,
    food_id: uuid.UUID,
    payload: FoodPriceUpsert,
    scope: dict = Depends(get_current_user_scope),
    db: Session = Depends(get_db),
):
    """
    Set (create or update) a food's price for one zone.
    Level 1/2/3 only — normal staff never touch prices.
    """
    assert_can_manage_brand_content(db, scope["user"], brand_id)

    food = db.query(Food).filter(Food.id == food_id, Food.brand_id == brand_id).first()
    if food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")

    zone = db.query(Zone).filter(Zone.id == payload.zone_id, Zone.brand_id == brand_id).first()
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found in this brand")

    price = db.query(FoodPrice).filter(FoodPrice.food_id == food_id, FoodPrice.zone_id == payload.zone_id).first()
    if price is None:
        price = FoodPrice(food_id=food_id, zone_id=payload.zone_id)
        db.add(price)

    price.regular_price = payload.regular_price
    price.discount_price = payload.discount_price
    price.discount_active = payload.discount_active

    db.commit()
    db.refresh(price)

    return FoodPriceAdminOut(
        id=price.id,
        zone_id=price.zone_id,
        zone_name_en=zone.name_en,
        zone_name_kh=zone.name_kh,
        regular_price=price.regular_price,
        discount_price=price.discount_price,
        discount_active=price.discount_active,
    )


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_price(
    brand_id: uuid.UUID,
    food_id: uuid.UUID,
    zone_id: uuid.UUID,
    scope: dict = Depends(get_current_user_scope),
    db: Session = Depends(get_db),
):
    assert_can_manage_brand_content(db, scope["user"], brand_id)
    price = (
        db.query(FoodPrice)
        .join(Food, Food.id == FoodPrice.food_id)
        .filter(FoodPrice.food_id == food_id, FoodPrice.zone_id == zone_id, Food.brand_id == brand_id)
        .first()
    )
    if price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
    db.delete(price)
    db.commit()
