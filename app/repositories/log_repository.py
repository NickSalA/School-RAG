"""Este módulo define el repositorio específico para la entidad "Log"."""

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.base import BaseRepository

from app.models.log_model import Log
from app.schemas.log_schema import LogCreate

class LogRepository(BaseRepository[Log, LogCreate, LogCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Log, session=session)
