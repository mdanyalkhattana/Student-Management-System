from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.auth_schema import UserCreate, UserUpdate, UserResponse
from utils.user_repo import (
    create_user, get_all_users, get_user_by_id,
    update_user, delete_user
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/create-user", response_model=UserResponse)
def create_new_user(data: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, data)


@router.get("/get-all-user", response_model=list[UserResponse])
def list_all_users(db: Session = Depends(get_db)):
    return get_all_users(db)


@router.get("/get-user-byID/{user_id}", response_model=UserResponse)
def get_single_user(user_id: int, db: Session = Depends(get_db)):
    return get_user_by_id(db, user_id)


@router.put("/update-user-byId/{user_id}", response_model=UserResponse)
def update_existing_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    return update_user(db, user_id, data)


@router.delete("/delete-user/{user_id}")
def remove_user(user_id: int, db: Session = Depends(get_db)):
    delete_user(db, user_id)
    return {"message": "User deleted successfully"}
