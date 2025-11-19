from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
 
from utils.menu import MenuRepository
from schemas.menu import MenuCreate, MenuUpdate, MenuResponse
from schemas.menu import MenuPermissionCreate, MenuPermissionResponse
from utils.menu  import create_menu_permission, get_menu_permission
import json
 
router = APIRouter(prefix="/menus", tags=["Menus"])

@router.post("/create-permission", response_model=MenuPermissionResponse)
def create_menu_permissions(payload: MenuPermissionCreate, db: Session = Depends(get_db)):
    return create_menu_permission(db, payload)

@router.get("/get-permission/{menu_id}", response_model=MenuPermissionResponse)
def fetch_menu_permissions(menu_id: int, db: Session = Depends(get_db)):
    db_obj = get_menu_permission(db, menu_id)
    if db_obj:
        db_obj.permission_objects = json.loads(db_obj.permission_objects)
    return db_obj

@router.post("/create-menu", response_model=MenuResponse)
def create_menu(data: MenuCreate, db: Session = Depends(get_db)):
    return MenuRepository.create(db, data)

@router.get("/get-all-menus", response_model=list[MenuResponse])
def get_menus(db: Session = Depends(get_db)):
    return MenuRepository.get_all(db)

@router.get("get-menu-byId/{menu_id}", response_model=MenuResponse)
def get_menu(menu_id: int, db: Session = Depends(get_db)):
    menu = MenuRepository.get_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu

@router.put("/update-menu/{menu_id}", response_model=MenuResponse)
def update_menu(menu_id: int, data: MenuUpdate, db: Session = Depends(get_db)):
    menu = MenuRepository.update(db, menu_id, data)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu

@router.delete("/delete-menu/{menu_id}")
def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    deleted = MenuRepository.delete(db, menu_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Menu not found")
    return {"message": "Menu deleted successfully"}
