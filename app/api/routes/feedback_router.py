"""Rutas para la gestión de feedbacks."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies.dep_auth import get_current_user, require_roles
from app.core.database import get_session
from app.models import Role, User
from app.schemas.feedback_schema import FeedbackCreate, FeedbackRead
from app.services.feedback_service import FeedbackService

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
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


@router.post("/", response_model=FeedbackRead, status_code=201)
async def create(
    feedback_in: FeedbackCreate,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """Endpoint para crear un nuevo feedback."""
    service = FeedbackService(session)
    return await service.create(feedback_in)
