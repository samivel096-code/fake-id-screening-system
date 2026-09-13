from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

class LoginRequest(BaseModel):
    user_id_or_email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserResponse(BaseModel):
    id: str
    email: str
    user_id: str
    full_name: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True

Token.model_rebuild()
