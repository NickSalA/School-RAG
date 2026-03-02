"Esquema de usuario para la API."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models import Role

class UserBase(BaseModel):
    name: str = Field(..., description="Nombre completo del usuario.")
    email: EmailStr = Field(..., description="Correo electrónico del usuario.")

class UserCreate(UserBase):
    password: str = Field(..., description="Contraseña del usuario.")
    role: Role = Field(default=Role.ADMIN, description="Rol del usuario (admin o superadmin).")

class UserRead(UserBase):
    id: int = Field(..., description="ID único del usuario.")
    role: Role = Field(..., description="Rol del usuario (admin o superadmin).")

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: Role | None = None
