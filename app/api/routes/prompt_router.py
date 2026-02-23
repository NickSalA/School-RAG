"""Router para la gestión de prompts."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.prompt_schema import PromptCreate, PromptRead, PromptStructure, PromptUpdate
from app.services.prompt import PromptService
from app.core.database import get_session

router = APIRouter()

@router.post("/", response_model=PromptRead)
async def create(prompt_in: PromptCreate, session: AsyncSession = Depends(get_session)):
    """Endpoint para crear un nuevo prompt."""
    service = PromptService(session)
    return await service.create(prompt_in)

@router.get("/active", response_model=list[PromptStructure])
async def get_active(session: AsyncSession = Depends(get_session)):
    """Endpoint para obtener el prompt activo."""
    service = PromptService(session)
    prompt, _ = await service.get_active_prompt()
    return prompt

@router.patch("/{prompt_id}", response_model=PromptRead)
async def update(prompt_id: int, prompt_in: PromptUpdate, session: AsyncSession = Depends(get_session)):
    """Endpoint para actualizar un prompt existente."""
    service = PromptService(session)
    return await service.update(prompt_id, prompt_in)
