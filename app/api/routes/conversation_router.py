"""Router para la gestión de conversaciones."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas.conversation_schema import ConversationRead, ConversationList
from app.services.conversation_service import ConversationService
from app.core.database import get_session
from app.api.dependencies.dep_auth import get_current_user
from app.models import User

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("/me", response_model=list[ConversationList])
async def get_my_conversations(
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """Lista las conversaciones del usuario autenticado ordenadas por fecha descendente."""
    service = ConversationService(session)
    return await service.list_by_user(current_user.id)


@router.get("/{conversation_id}", response_model=ConversationRead)
async def get(
    conversation_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    """Endpoint para obtener una conversación por su ID."""
    service = ConversationService(session)
    return await service.get_for_user(conversation_id, current_user.id)
