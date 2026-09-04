import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user_scope
from app.core.permissions import assert_can_manage_brand_content, assert_brand_access
from app.db.database import get_db
from app.db.models.brand import Brand
from app.db.models.zone import Zone
from app.db.models.category import Category
from app.db.models.food import Food
from app.db.models.food_price import FoodPrice
from app.schemas.food import FoodCreate, FoodUpdate, FoodAdminOut
from app.schemas.food_price import FoodPriceAdminOut

router = APIRouter(prefix="/api/brands/{brand_id}/foods", tags=["foods"])


def _get_brand_or_404(db: Session, brand_id: uuid.UUID) -> Brand:
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    return brand


def _to_admin_out(food: Food) -> FoodAdminOut:
    return FoodAdminOut(
        id=food.id,
        brand_id=food.brand_id,
        category_id=food.category_id,
        name_en=food.name_en,
        name_kh=food.name_kh,
        description_en=food.description_en,
        description_kh=food.description_kh,
        image_url=food.image_url,
        is_available=food.is_available,
        prices=[
            FoodPriceAdminOut(
                id=p.id,
                zone_id=p.zone_id,
                zone_name_en=p.zone.name_en,
                zone_name_kh=p.zone.name_kh,
                regular_price=p.regular_price,
                discount_price=p.discount_price,
                discount_active=p.discount_active,
            )
            for p in food.prices
        ],
    )


@router.get("", response_model=list[FoodAdminOut])
def list_foods(brand_id: uuid.UUID, scope: dict = Depends(get_current_user_scope), db: Session = Depends(get_db)):
    """Admin view only — includes every zone's price. Staff/public use the menu endpoints instead."""
    assert_can_manage_brand_content(db, scope["user"], brand_id)
    _get_brand_or_404(db, brand_id)
    foods = (
        db.query(Food)
        .options(joinedload(Food.prices).joinedload(FoodPrice.zone))
        .filter(Food.brand_id == brand_id)
        .all()
    )
    return [_to_admin_out(f) for f in foods]


@router.get("/{food_id}", response_model=FoodAdminOut)
def get_food(
    brand_id: uuid.UUID,
    food_id: uuid.UUID,
    scope: dict = Depends(get_current_user_scope),
    db: Session = Depends(get_db),
):
    assert_can_manage_brand_content(db, scope["user"], brand_id)
    food = (
        db.query(Food)
        .options(joinedload(Food.prices).joinedload(FoodPrice.zone))
        .filter(Food.id == food_id, Food.brand_id == brand_id)
        .first()
    )
    if food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")
    return _to_admin_out(food)


@router.post("", response_model=FoodAdminOut, status_code=status.HTTP_201_CREATED)
def create_food(
    brand_id: uuid.UUID,
    payload: FoodCreate,
    scope: dict = Depends(get_current_user_scope),
    db: Session = Depends(get_db),
):
    assert_can_manage_brand_content(db, scope["user"], brand_id)
    _get_brand_or_404(db, brand_id)

    if payload.category_id is not None:
        cat = db.query(Category).filter(Category.id == payload.category_id, Category.brand_id == brand_id).first()
        if cat is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found in this brand")

    food = Food(brand_id=brand_id, **payload.model_dump())
    db.add(food)
    db.commit()
    db.refresh(food)
    return _to_admin_out(food)


@router.put("/{food_id}", response_model=FoodAdminOut)
def update_food(
    brand_id: uuid.UUID,
    food_id: uuid.UUID,
    payload: FoodUpdate,
    scope: dict = Depends(get_current_user_scope),
    db: Session = Depends(get_db),
):
    assert_can_manage_brand_content(db, scope["user"], brand_id)
    food = db.query(Food).filter(Food.id == food_id, Food.brand_id == brand_id).first()
    if food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")

    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data and data["category_id"] is not None:
        cat = db.query(Category).filter(Category.id == data["category_id"], Category.brand_id == brand_id).first()
        if cat is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found in this brand")

    for field, value in data.items():
        setattr(food, field, value)

    db.commit()
    db.refresh(food)
    return _to_admin_out(food)


@router.delete("/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food(
    brand_id: uuid.UUID,
    food_id: uuid.UUID,
    scope: dict = Depends(get_current_user_scope),
    db: Session = Depends(get_db),
):
    assert_can_manage_brand_content(db, scope["user"], brand_id)
    food = db.query(Food).filter(Food.id == food_id, Food.brand_id == brand_id).first()
    if food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")
    db.delete(food)
    db.commit()
