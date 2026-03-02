"""Servicio para gestionar el feedback de los usuarios sobre las respuestas del modelo."""

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories import FeedbackRepository
from app.schemas import FeedbackCreate, FeedbackRead
from app.services import ConversationService

from app.exceptions.database import NotFoundException


class FeedbackService:
    """Servicio para gestionar el feedback de los usuarios sobre las respuestas del modelo."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.feedback_repository = FeedbackRepository(session)
        self.conversation_service = ConversationService(session)

    async def create(self, feedback_in: FeedbackCreate) -> None:
        """Crea un nuevo feedback."""
        conversation = await self.conversation_service.get(feedback_in.conversation_id)
        if conversation is None:
            raise NotFoundException(f"Conversación con ID {feedback_in.conversation_id} no encontrada")
        await self.feedback_repository.create(feedback_in)

    async def get(self, feedback_id: int) -> FeedbackRead:
        """Obtiene un feedback por su ID."""
        feedback = await self.feedback_repository.get(feedback_id)
        if feedback is None:
            raise NotFoundException(f"Feedback con ID {feedback_id} no encontrado")
        return FeedbackRead.model_validate(feedback)

    async def get_all(self) -> list[FeedbackRead]:
        """Obtiene todo el feedback registrado."""
        feedbacks = await self.feedback_repository.get_all()
        return [FeedbackRead.model_validate(feedback) for feedback in feedbacks]
