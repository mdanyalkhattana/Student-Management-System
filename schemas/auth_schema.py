# schemas/auth_schema.py
from pydantic import BaseModel, EmailStr,constr
from typing_extensions import Annotated
from typing import Optional


# User login request
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# JWT Token response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# schemas/password_schema.py 

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    id: int
    email: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class UserCreate(BaseModel):     
    name: str
    email: EmailStr
    password: Annotated[str, constr(min_length=6)]
    role_id: Optional[int] = None

# Response schema (hide password)
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_verified: bool
    role_id: Optional[int] = None

    class Config:
        orm_mode = True

class VerifyEmailRequest(BaseModel):
    token: str
#  for the CRUD api schmemasclass UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
