"""Rutas para la gestión de feedbacks."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.feedback_schema import FeedbackRead
from app.services.feedback import FeedbackService
from app.core.database import get_session

router = APIRouter()

@router.get("/{feedback_id}", response_model=FeedbackRead)
async def get(feedback_id: int, session: AsyncSession = Depends(get_session)):
    """Endpoint para obtener un feedback por su ID."""
    service = FeedbackService(session)
    return await service.get(feedback_id)

@router.get("/", response_model=list[FeedbackRead])
async def get_all(session: AsyncSession = Depends(get_session)):
    """Endpoint para listar todos los feedbacks."""
    service = FeedbackService(session)
    return await service.get_all()
