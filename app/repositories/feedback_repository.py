"""Este módulo define el repositorio específico para la entidad "Feedback"."""

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.base import BaseRepository

from app.models.feedback_model import Feedback
from app.schemas.feedback_schema import FeedbackCreate

class FeedbackRepository(BaseRepository[Feedback, FeedbackCreate, FeedbackCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Feedback, session=session)
