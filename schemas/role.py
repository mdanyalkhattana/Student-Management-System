from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RoleBase(BaseModel):
    name: str
    menu_id: Optional[int] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    menu_id: Optional[int] = None


class RoleResponse(RoleBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
