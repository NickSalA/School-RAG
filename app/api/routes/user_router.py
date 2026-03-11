"""Router para el flujo de usuarios."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import User
from app.schemas.user_schema import UserRead, UserCreate, UserUpdate
from app.core.database import get_session
from app.api.dependencies.dep_auth import get_current_user
from app.services.user_service import UserService

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]

@router.post("/", response_model=UserRead)
async def create(user_in: UserCreate, session: SessionDep, current_user: CurrentUserDep):
    """Endpoint para crear un nuevo usuario."""
    service = UserService(session)
    return await service.create(user_in, current_user.id)

@router.get("/{user_id}", response_model=UserRead)
async def get(user_id: int, session: SessionDep):
    """Endpoint para obtener un usuario por su ID."""

    service = UserService(session)
    return await service.get(user_id)

@router.get("/", response_model=list[UserRead])
async def get_all(session: AsyncSession = Depends(get_session)):
    """Endpoint para listar todos los usuarios."""
    service = UserService(session)
    return await service.list_users()

@router.patch("/{user_id}", response_model=UserRead)
async def update(user_id: int, user_in: UserUpdate, session: SessionDep, current_user: CurrentUserDep):
    """Endpoint para actualizar un usuario existente."""
    service = UserService(session)
    return await service.update(user_id, user_in, current_user.id)

@router.delete("/{user_id}", status_code=204)
async def delete(user_id: int, session: SessionDep, current_user: CurrentUserDep):
    """Endpoint para eliminar un usuario."""
    service = UserService(session)
    await service.delete(user_id, current_user.id)
