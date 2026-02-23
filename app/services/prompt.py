"""Servicio para la gestión de prompts, incluyendo la creación, actualización y recuperación del prompt activo."""

from typing import Any

from sqlmodel.ext.asyncio.session import AsyncSession
from app.agents.flow import prompt_system
from app.repositories.prompt_repository import PromptRepository
from app.schemas.prompt_schema import PromptCreate, PromptUpdate, PromptRead

from app.exceptions.database import NotFoundException

class PromptService:
    def __init__(self, session: AsyncSession):
        self.prompt_repo = PromptRepository(session)

    async def get_active_prompt(self) -> tuple[list[dict[str, Any]], int | None]:
        """Obtiene la versión activa del prompt."""
        db_prompt = await self.prompt_repo.get_active_prompt()
        if db_prompt is None:
            return prompt_system(), None
        return db_prompt.system_message, db_prompt.id

    async def create(self, prompt_in: PromptCreate) -> PromptRead:
        """Crea un nuevo prompt."""
        if prompt_in.is_active:
            active_prompt = await self.prompt_repo.get_active_prompt()
            if active_prompt:
                await self.prompt_repo.deactivate_prompt(active_prompt)

        prompt = await self.prompt_repo.create(prompt_in)
        return PromptRead.model_validate(prompt)

    async def update(self, prompt_id: int, prompt_in: PromptUpdate) -> PromptRead:
        """Actualiza un prompt existente."""
        prompt_obj = await self.prompt_repo.get(prompt_id)
        if not prompt_obj:
            raise NotFoundException(f"Prompt con ID {prompt_id} no encontrado")

        if prompt_in.is_active and not prompt_obj.is_active:
            active_prompt = await self.prompt_repo.get_active_prompt()
            if active_prompt and active_prompt.id != prompt_obj.id:
                await self.prompt_repo.deactivate_prompt(active_prompt)

        updated_prompt = await self.prompt_repo.update(db_obj=prompt_obj, obj_in=prompt_in)
        return PromptRead.model_validate(updated_prompt)
