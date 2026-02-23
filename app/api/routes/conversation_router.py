"""Router para la gestión de conversaciones."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas.conversation_schema import ConversationRead, ConversationList
from app.services.conversation import ConversationService
from app.core.database import get_session

router = APIRouter()

@router.get("/{conversation_id}", response_model=ConversationRead)
async def get(conversation_id: int, session: AsyncSession = Depends(get_session)):
    """Endpoint para obtener una conversación por su ID."""
    service = ConversationService(session)
    return await service.get(conversation_id)

@router.get("/", response_model=list[ConversationList])
async def get_all(session: AsyncSession = Depends(get_session)):
    """Endpoint para listar todas las conversaciones."""
    service = ConversationService(session)
    return await service.list_conversations()
