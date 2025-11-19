from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from database import Base
from models.menu_model import Menu

class MenuPermission(Base):
    __tablename__ = "menu_permissions"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)

    # Store JSON as Text (same as longtext)
    permission_objects = Column(Text, nullable=False)

    status = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    menu = relationship("Menu", back_populates="permissions")
