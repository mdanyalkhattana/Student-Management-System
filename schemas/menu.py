from typing import List,Optional,Dict,Union
from pydantic import BaseModel
from datetime import datetime


class PermissionObject(BaseModel):
    object: Optional[Union[str, Dict]] = None
    permission: bool


class MenuPermissionCreate(BaseModel):
    menu_id: int
    permission_objects: List[PermissionObject]


class MenuPermissionResponse(BaseModel):
    id: Optional[int] = None
    menu_id: int
    permission_objects: List[PermissionObject]
    status: Optional[bool] = None

    class Config:
        from_attributes = True


    

class MenuBase(BaseModel):
    name: str
    slug: str
    parent_id: Optional[int] = None
    status: Optional[bool] = True

class MenuCreate(MenuBase):
    pass

class MenuUpdate(BaseModel):
    name: Optional[str]
    slug: Optional[str]
    parent_id: Optional[int]
    status: Optional[bool]

class MenuResponse(MenuBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
