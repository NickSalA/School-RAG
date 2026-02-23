"""Este módulo define el router para los endpoints relacionados con los logs del sistema."""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.log_schema import LogRead
from app.services.log import LogService
from app.core.database import get_session
from app.models.log_model import ResourceType
router = APIRouter()

@router.get("/", response_model=list[LogRead])
async def get_all(session: AsyncSession = Depends(get_session)):
    """Endpoint para obtener todos los logs."""
    service = LogService(session)
    return await service.get_all()

@router.get("/resource/{resource_type}", response_model=list[LogRead])
async def get_by_resource(resource_type: ResourceType, session: AsyncSession = Depends(get_session)):
    """Endpoint para obtener logs por tipo de recurso."""
    service = LogService(session)
    return await service.get_by_resource(resource_type)

@router.get("/date-range", response_model=list[LogRead])
async def get_by_date_range(start_date: datetime, end_date: datetime, session: AsyncSession = Depends(get_session)):
    """Endpoint para obtener logs por rango de fechas."""
    service = LogService(session)
    return await service.get_by_date_range(start_date, end_date)
