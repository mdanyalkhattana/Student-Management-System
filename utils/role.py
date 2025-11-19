from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.role import Role
from schemas.role import RoleCreate, RoleUpdate
from models.menu_model import Menu


def create_role(db: Session, data: RoleCreate):
    # Unique role name check
    existing = db.query(Role).filter(Role.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role name already exists")

    # Check if menu_id exists
    if data.menu_id is not None:
        menu = db.query(Menu).filter(Menu.id == data.menu_id).first()
        if not menu:
            raise HTTPException(status_code=404, detail="Menu not found")

    new_role = Role(name=data.name, menu_id=data.menu_id)

    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


def get_all_roles(db: Session):
    return db.query(Role).all()


def get_role_by_id(db: Session, role_id: int):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


def update_role(db: Session, role_id: int, data: RoleUpdate):
    role = get_role_by_id(db, role_id)

    if data.name:
        # unique name check
        exists = db.query(Role).filter(Role.name == data.name, Role.id != role_id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Role name already exists")
        role.name = data.name

    if data.menu_id is not None:
        menu = db.query(Menu).filter(Menu.id == data.menu_id).first()
        if not menu:
            raise HTTPException(status_code=404, detail="Menu not found")
        role.menu_id = data.menu_id

    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: int):
    role = get_role_by_id(db, role_id)
    db.delete(role)
    db.commit()
    return True
