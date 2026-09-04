from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_staff
from app.db.database import get_db
from app.db.models.brand import Brand
from app.db.models.category import Category
from app.db.models.food import Food
from app.db.models.food_price import FoodPrice
from app.schemas.category import CategoryOut
from app.schemas.food import FoodMenuOut
from app.schemas.food_price import SinglePriceOut
from app.schemas.menu import MenuResponse, BrandMenuInfo

router = APIRouter(prefix="/api/menu", tags=["menu"])


@router.get("", response_model=MenuResponse)
def get_staff_menu(scope: dict = Depends(require_staff), db: Session = Depends(get_db)):
    """
    The staff/customer-facing menu display.

    Requires a logged-in STAFF user. The response is built from that staff
    member's assigned brand + zone — the frontend never chooses or sends a
    zone, and the response never contains any other zone's price. This is
    what powers the front-of-house display described in the spec: staff log
    in once, and customers only ever see the single applicable price.
    """
    brand_id = scope["brand_id"]
    zone_id = scope["zone_id"]

    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    categories = db.query(Category).filter(Category.brand_id == brand_id).order_by(Category.sort_order).all()

    foods = (
        db.query(Food)
        .options(joinedload(Food.prices))
        .filter(Food.brand_id == brand_id)
        .all()
    )

    food_out: list[FoodMenuOut] = []
    for food in foods:
        price_row = next((p for p in food.prices if p.zone_id == zone_id), None)
        single_price = None
        if price_row is not None:
            single_price = SinglePriceOut(
                price=price_row.effective_price,
                is_discounted=bool(price_row.discount_active and price_row.discount_price is not None),
            )

        food_out.append(
            FoodMenuOut(
                id=food.id,
                name_en=food.name_en,
                name_kh=food.name_kh,
                description_en=food.description_en,
                description_kh=food.description_kh,
                image_url=food.image_url,
                is_available=food.is_available,
                category_id=food.category_id,
                price=single_price,
            )
        )

    return MenuResponse(
        brand=BrandMenuInfo.model_validate(brand),
        categories=[CategoryOut.model_validate(c) for c in categories],
        foods=food_out,
    )
