import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_scope
from app.core.permissions import assert_can_manage_brand_content, assert_brand_access
from app.db.database import get_db
from app.db.models.category import Category
from app.db.models.brand import Brand
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter(prefix="/api/brands/{brand_id}/categories", tags=["categories"])


def _get_brand_or_404(db: Session, brand_id: uuid.UUID) -> Brand:
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    return brand


@router.get("", response_model=list[CategoryOut])
def list_categories(brand_id: uuid.UUID, scope: dict = Depends(get_current_user_scope), db: Session = Depends(get_db)):
    assert_brand_access(db, scope["user"], brand_id, allow_staff=True)
    _get_brand_or_404(db, brand_id)
    return db.query(Category).filter(Category.brand_id == brand_id).order_by(Category.sort_order).all()


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    brand_id: uuid.UUID,
    payload: CategoryCreate,
    scope: dict = Depends(get_current_user_scope),
    db: Session = Depends(get_db),
):
    assert_can_manage_brand_content(db, scope["user"], brand_id)
    _get_brand_or_404(db, brand_id)

    category = Category(brand_id=brand_id, **payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    brand_id: uuid.UUID,
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    scope: dict = Depends(get_current_user_scope),
    db: Session = Depends(get_db),
):
    assert_can_manage_brand_content(db, scope["user"], brand_id)
    category = db.query(Category).filter(Category.id == category_id, Category.brand_id == brand_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    brand_id: uuid.UUID,
    category_id: uuid.UUID,
    scope: dict = Depends(get_current_user_scope),
    db: Session = Depends(get_db),
):
    assert_can_manage_brand_content(db, scope["user"], brand_id)
    category = db.query(Category).filter(Category.id == category_id, Category.brand_id == brand_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    db.delete(category)
    db.commit()
