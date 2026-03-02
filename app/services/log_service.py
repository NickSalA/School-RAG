"""Servicio para manejar la lógica de negocio relacionada con los logs de interacción del agente."""

from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import ResourceType
from app.repositories import LogRepository
from app.schemas import LogRead


class LogService:
    def __init__(self, session: AsyncSession):
        self.log_repo = LogRepository(session)

    async def get_all(self) -> list[LogRead]:
        """Obtiene todos los logs registrados."""
        logs = await self.log_repo.get_all()
        return [LogRead.model_validate(log) for log in logs]

    async def get_by_resource(self, resource_type: ResourceType) -> list[LogRead]:
        """Obtiene los logs relacionados con un recurso específico."""
        logs = await self.log_repo.get_by_resource(resource_type)
        return [LogRead.model_validate(log) for log in logs]

    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> list[LogRead]:
        """Obtiene los logs registrados dentro de un rango de fechas específico."""
        logs = await self.log_repo.get_by_date_range(start_date, end_date)
        return [LogRead.model_validate(log) for log in logs]
