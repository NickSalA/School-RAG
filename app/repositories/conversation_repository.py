"""Este módulo define el repositorio específico para la entidad "Conversation"."""

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.conversation_model import Conversation
from app.schemas.conversation_schema import ConversationCreate
from app.repositories.base import BaseRepository

from app.exceptions.database import NotFoundException

class ConversationRepository(BaseRepository[Conversation, ConversationCreate, ConversationCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Conversation, session=session)

    async def update_messages(self, conversation_id: int, new_messages: list[dict]) -> Conversation | None:
        """Actualiza los mensajes de una conversación existente."""
        db_obj = await self.get(conversation_id)
        if not db_obj:
            raise NotFoundException("La conversación no existe.")

        current_content = list(db_obj.content)
        current_content.extend(new_messages)

        return await self.update(db_obj, {"content": current_content})
