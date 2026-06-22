"""Este módulo define el repositorio específico para la entidad "Feedback"."""

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.repositories.base import BaseRepository

from app.models import Feedback
from app.schemas import FeedbackCreate


class FeedbackRepository(BaseRepository[Feedback, FeedbackCreate, FeedbackCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Feedback, session=session)

    async def get_by_conversation(self, conversation_id: int) -> Feedback | None:
        """Obtiene un feedback por ID de conversación."""
        query = select(self.model).where(
            self.model.conversation_id == conversation_id
        )
        result = await self.session.exec(query)
        return result.first()
