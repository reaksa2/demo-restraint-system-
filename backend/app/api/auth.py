from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_scope
from app.core.security import verify_password, create_access_token
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, CurrentUserInfo

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=CurrentUserInfo)
def get_me(scope: dict = Depends(get_current_user_scope)):
    user: User = scope["user"]
    return CurrentUserInfo(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        group_id=scope["group_id"],
        brand_id=scope["brand_id"],
        zone_id=scope["zone_id"],
    )
