"""Este módulo define el repositorio específico para la entidad "Log"."""

from datetime import datetime
from typing import Sequence
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories import BaseRepository

from app.models import Log
from app.schemas import LogCreate
from app.models import ResourceType

class LogRepository(BaseRepository[Log, LogCreate, LogCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Log, session=session)

    async def get_by_resource(self, resource_type: ResourceType) -> Sequence[Log]:
        """Obtiene los logs relacionados con un recurso específico."""
        query = select(self.model).where(
            self.model.resource_type == resource_type).order_by(getattr(self.model,"created_at").desc())
        result = await self.session.exec(query)
        return result.all()

    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> Sequence[Log]:
        """Obtiene los logs registrados dentro de un rango de fechas específico."""
        query = select(self.model).where(
            getattr(self.model,"created_at").between(start_date, end_date)).order_by(getattr(self.model,"created_at").desc())
        result = await self.session.exec(query)
        return result.all()
