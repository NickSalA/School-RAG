"""Esquemas de datos para autenticación."""
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_role: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "admin"

class UserResponse(BaseModel):
    id: str
    username: str
    role: str