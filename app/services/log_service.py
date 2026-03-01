"""Servicio para manejar la lógica de negocio relacionada con los logs de interacción del agente."""

from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.log_model import Log, ResourceType
from app.repositories.log_repository import LogRepository
from app.schemas.log_schema import LogRead


def _log_to_read(db_log: Log) -> LogRead:
    """Convierte un objeto Log de SQLAlchemy a LogRead de Pydantic."""
    return LogRead(
        id=db_log.id,
        user_id=db_log.user_id,
        action=db_log.action,
        resource_type=db_log.resource_type,
        resource_id=db_log.resource_id,
        details=db_log.details,  # type: ignore  # Inconsistencia de tipos en modelo vs schema
        created_at=db_log.created_at
    )


class LogService:
    def __init__(self, session: AsyncSession):
        self.log_repo = LogRepository(session)

    async def get_all(self) -> list[LogRead]:
        """Obtiene todos los logs registrados."""
        logs = await self.log_repo.get_all()
        return [_log_to_read(log) for log in logs]

    async def get_by_resource(self, resource_type: ResourceType) -> list[LogRead]:
        """Obtiene los logs relacionados con un recurso específico."""
        logs = await self.log_repo.get_by_resource(resource_type)
        return [_log_to_read(log) for log in logs]

    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> list[LogRead]:
        """Obtiene los logs registrados dentro de un rango de fechas específico."""
        logs = await self.log_repo.get_by_date_range(start_date, end_date)
        return [_log_to_read(log) for log in logs]
