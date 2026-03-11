"""Router para la gestión de conversaciones."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas.conversation_schema import ConversationRead, ConversationList
from app.services.conversation_service import ConversationService
from app.core.database import get_session
from app.api.dependencies.dep_auth import get_current_user
from app.models import User

router = APIRouter()

@router.get("/me", response_model=list[ConversationList])
async def get_my_conversations(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Lista las conversaciones del usuario autenticado ordenadas por fecha descendente."""
    service = ConversationService(session)
    return await service.list_by_user(current_user.id)


@router.get("/{conversation_id}", response_model=ConversationRead)
async def get(
    conversation_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Endpoint para obtener una conversación por su ID."""
    service = ConversationService(session)
    return await service.get(conversation_id)
