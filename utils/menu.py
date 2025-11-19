import json
from sqlalchemy.orm import Session
from models.menu_permission import MenuPermission
from schemas.menu import MenuPermissionCreate,MenuPermissionResponse
from models.menu_model import Menu
from schemas.menu import MenuCreate, MenuUpdate


def create_menu_permission(db: Session, data: MenuPermissionCreate):
    db_obj = MenuPermission(
        menu_id=data.menu_id,
        permission_objects=json.dumps([p.model_dump() for p in data.permission_objects]),
        status=1
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # Always convert DB string → Python list
    permission_objects = json.loads(db_obj.permission_objects)

    # Build the correct response
    response_data = {
        "id": db_obj.id,
        "menu_id": db_obj.menu_id,
        "permission_objects": permission_objects,   # ← LIST (not string)
        "status": db_obj.status
    }

    # Validate using Pydantic
    return MenuPermissionResponse.model_validate(response_data)


def get_menu_permission(db: Session, menu_id: int):
    return db.query(MenuPermission).filter(MenuPermission.menu_id == menu_id).first()



class MenuRepository:

    @staticmethod
    def create(db: Session, data: MenuCreate):
        new_menu = Menu(**data.dict())
        db.add(new_menu)
        db.commit()
        db.refresh(new_menu)
        return new_menu

    @staticmethod
    def get_all(db: Session):
        return db.query(Menu).all()

    @staticmethod
    def get_by_id(db: Session, menu_id: int):
        return db.query(Menu).filter(Menu.id == menu_id).first()

    @staticmethod
    def update(db: Session, menu_id: int, data: MenuUpdate):
        menu = MenuRepository.get_by_id(db, menu_id)
        if not menu:
            return None
        
        for key, value in data.dict(exclude_unset=True).items():
            setattr(menu, key, value)

        db.commit()
        db.refresh(menu)
        return menu

    @staticmethod
    def delete(db: Session, menu_id: int):
        menu = MenuRepository.get_by_id(db, menu_id)
        if not menu:
            return None
        
        db.delete(menu)
        db.commit()
        return True
