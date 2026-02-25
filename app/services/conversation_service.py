"""Servicio para la gestión de conversaciones."""

from sqlmodel.ext.asyncio.session import AsyncSession
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.conversation_schema import ConversationCreate, ConversationRead, ConversationList

from app.exceptions.database import NotFoundException

class ConversationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.conversation = ConversationRepository(session)

    async def create(self, conversation_in: ConversationCreate) -> ConversationRead:
        """Crea una nueva conversación."""
        conversation = await self.conversation.create(conversation_in)
        return ConversationRead.model_validate(conversation)

    async def get(self, conversation_id: int) -> ConversationRead:
        """Obtiene una conversación por su ID."""
        conversation = await self.conversation.get(conversation_id)
        if conversation is None:
            raise NotFoundException(f"Conversación con ID {conversation_id} no encontrada")
        return ConversationRead.model_validate(conversation)

    async def list_conversations(self) -> list[ConversationList]:
        """Lista todas las conversaciones."""
        conversations = await self.conversation.get_all()
        return [ConversationList.model_validate(conv) for conv in conversations]

    async def update_messages(self, conversation_id: int, formatted_messages: list[dict]) -> ConversationRead:
        """Actualiza los mensajes de una conversación existente."""
        updated_conversation = await self.conversation.update_messages(conversation_id, formatted_messages)
        if updated_conversation is None:
            raise NotFoundException(f"Conversación con ID {conversation_id} no encontrada")
        return ConversationRead.model_validate(updated_conversation)
