"""Esquemas de datos para autenticación."""
from pydantic import BaseModel
from app.schemas.user_schema import UserRead
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserRead

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "admin"

class UserResponse(BaseModel):
    id: str
    username: str
    role: str
