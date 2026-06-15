"""Rutas para la gestión de feedbacks."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies.dep_auth import require_roles
from app.core.database import get_session
from app.models import Role, User
from app.schemas.feedback_schema import FeedbackRead
from app.services.feedback_service import FeedbackService

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]
AdminUserDep = Annotated[User, Depends(require_roles(Role.ADMIN, Role.SUPERADMIN))]


@router.get("/{feedback_id}", response_model=FeedbackRead)
async def get(
    feedback_id: int,
    session: SessionDep,
    current_user: AdminUserDep,
):
    """Endpoint para obtener un feedback por su ID."""
    service = FeedbackService(session)
    return await service.get(feedback_id)


@router.get("/", response_model=list[FeedbackRead])
async def get_all(session: SessionDep, current_user: AdminUserDep):
    """Endpoint para listar todos los feedbacks."""
    service = FeedbackService(session)
    return await service.get_all()
