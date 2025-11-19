from sqlalchemy import Column, Integer, String, Boolean, DateTime, func,ForeignKey 
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=True)  # Allow null for OAuth users
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # for linked the role table 
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)   

    role = relationship("Role", back_populates="users")