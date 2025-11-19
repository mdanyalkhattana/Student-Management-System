from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.role import RoleCreate, RoleUpdate, RoleResponse
from utils.role import (
    create_role, get_all_roles, get_role_by_id, update_role, delete_role
)

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


@router.post("/create-Role", response_model=RoleResponse)
def create_new_role(data: RoleCreate, db: Session = Depends(get_db)):
    return create_role(db, data)


@router.get("/Get-all-role", response_model=list[RoleResponse])
def list_roles(db: Session = Depends(get_db)):
    return get_all_roles(db)


@router.get("/Get-role-byId/{role_id}", response_model=RoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    return get_role_by_id(db, role_id)


@router.put("/Update-role/{role_id}", response_model=RoleResponse)
def update_existing_role(role_id: int, data: RoleUpdate, db: Session = Depends(get_db)):
    return update_role(db, role_id, data)


@router.delete("/delete-role/{role_id}")
def remove_role(role_id: int, db: Session = Depends(get_db)):
    delete_role(db, role_id)
    return {"message": "Role deleted successfully"}
