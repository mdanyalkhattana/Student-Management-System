from sqlalchemy.orm import Session
from models.user_model import User
from schemas.auth_schema import UserCreate, UserUpdate
from fastapi import HTTPException, status
from utils import hash_password

def create_user(db: Session, data: UserCreate):
    # Check for duplicate email
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    hashed_password = hash_password(data.password)

    new_user = User(
        name=data.name,
        email=data.email,
        password=hashed_password,
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_all_users(db: Session):
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_user(db: Session, user_id: int, data: UserUpdate):
    user = get_user_by_id(db, user_id)

    if data.email:
        # Avoid duplicate email when updating
        existing = db.query(User).filter(User.email == data.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")
        user.email = data.email

    if data.name:
        user.name = data.name

    if data.password:
        user.password = hash_password(data.password)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    db.delete(user)
    db.commit()
    return True
