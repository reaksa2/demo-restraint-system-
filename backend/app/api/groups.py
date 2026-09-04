import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_scope
from app.core.permissions import require_level1, assert_group_access
from app.db.database import get_db
from app.db.models.group import Group
from app.db.models.user import UserRole
from app.schemas.group import GroupCreate, GroupUpdate, GroupOut

router = APIRouter(prefix="/api/groups", tags=["groups"])


@router.get("", response_model=list[GroupOut])
def list_groups(scope: dict = Depends(get_current_user_scope), db: Session = Depends(get_db)):
    user = scope["user"]
    if user.role == UserRole.LEVEL1:
        return db.query(Group).order_by(Group.name).all()
    if user.role == UserRole.LEVEL2 and scope["group_id"] is not None:
        return db.query(Group).filter(Group.id == scope["group_id"]).all()
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to groups")


@router.get("/{group_id}", response_model=GroupOut)
def get_group(group_id: uuid.UUID, scope: dict = Depends(get_current_user_scope), db: Session = Depends(get_db)):
    assert_group_access(db, scope["user"], group_id)
    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


@router.post("", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_group(payload: GroupCreate, scope: dict = Depends(get_current_user_scope), db: Session = Depends(get_db)):
    require_level1(scope["user"])
    group = Group(name=payload.name, description=payload.description)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.put("/{group_id}", response_model=GroupOut)
def update_group(
    group_id: uuid.UUID,
    payload: GroupUpdate,
    scope: dict = Depends(get_current_user_scope),
    db: Session = Depends(get_db),
):
    require_level1(scope["user"])
    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    if payload.name is not None:
        group.name = payload.name
    if payload.description is not None:
        group.description = payload.description

    db.commit()
    db.refresh(group)
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: uuid.UUID, scope: dict = Depends(get_current_user_scope), db: Session = Depends(get_db)):
    require_level1(scope["user"])
    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    db.delete(group)
    db.commit()
