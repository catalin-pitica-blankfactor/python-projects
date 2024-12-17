from fastapi import Depends, HTTPException, BackgroundTasks, APIRouter
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.service.group_service import GroupService
from app.service.user_service import UserService
from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserResponseForGet,
    UserUpdate,
)

router = APIRouter()


@router.post("/user", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    background_task: BackgroundTasks,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(),
    group_service: GroupService = Depends(),
):
    try:
        group_service.get_group_by_id(db, user.user_group)
        return user_service.add_new_user(
            db, user.user_name, user.user_group, background_task
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user", response_model=list[UserResponseForGet])
async def get_all_users(
    db: Session = Depends(get_db), user_service: UserService = Depends()
):
    try:
        return user_service.get_all_users(db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=UserResponseForGet)
async def get_user_by_id(
    user_id: str, db: Session = Depends(get_db), user_service: UserService = Depends()
):
    try:
        return user_service.get_user_by_id(db, user_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/user/{user_id}", response_model=UserResponseForGet)
async def update_user(
    user_id: str,
    user_group: UserUpdate,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(),
):
    try:
        user = user_service.check_user_validation(db, user_id)
        user_service.check_group_in_user(db, user, user_group.group_name)
        return user_service.update_user(db, user_id, user_group.user_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/user/{user_id}")
async def delete_user_by_id(
    user_id: str, db: Session = Depends(get_db), user_service: UserService = Depends()
):
    try:
        return user_service.delete_user_by_id(db, user_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
