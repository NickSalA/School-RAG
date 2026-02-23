"""Router para el flujo de usuarios."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.user_schema import UserRead, UserCreate, UserUpdate
from app.core.database import get_session

from app.services.user import UserService

router = APIRouter()

@router.post("/", response_model=UserRead)
async def create(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    """Endpoint para crear un nuevo usuario."""
    service = UserService(session)
    return await service.create(user_in)

@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    """Endpoint para obtener un usuario por su ID."""
    service = UserService(session)
    return await service.get(user_id)

@router.get("/", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_session)):
    """Endpoint para listar todos los usuarios."""
    service = UserService(session)
    return await service.list_users()

@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, user_in: UserUpdate, session: AsyncSession = Depends(get_session)):
    """Endpoint para actualizar un usuario existente."""
    service = UserService(session)
    return await service.update(user_id, user_in)

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    """Endpoint para eliminar un usuario."""
    service = UserService(session)
    await service.delete(user_id)
