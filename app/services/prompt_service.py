"""Servicio para la gestión de prompts, incluyendo la creación, actualización y recuperación del prompt activo."""

from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from app.agents.flow import prompt_system
from app.repositories.prompt_repository import PromptRepository
from app.repositories.log_repository import LogRepository
from app.models.log_model import ResourceType
from app.schemas.prompt_schema import PromptCreate, PromptUpdate, PromptRead, PromptStructure
from app.schemas.log_schema import LogCreate
from app.exceptions.database import NotFoundException

class PromptService:
    def __init__(self, session: AsyncSession):
        self.prompt_repo = PromptRepository(session)
        self.log_repo = LogRepository(session)

    async def get_active_prompt(self) -> PromptRead:
        """Obtiene la versión activa del prompt."""
        db_prompt = await self.prompt_repo.get_active_prompt()
        if db_prompt is None:
            system_message = []
            for section in prompt_system():
                system_message.append(PromptStructure(section=section["section"], content=section["content"]))
            return PromptRead(
                id=0,
                version_name="default",
                system_message=system_message,
                user_id=None,
                is_active=True,
                created_at=datetime(2000, 1, 1)
            )
        return PromptRead.model_validate(db_prompt)

    async def create(self, prompt_in: PromptCreate, current_user_id: int) -> PromptRead:
        """Crea un nuevo prompt."""        
        active_prompt = None
        old_prompt = None
        old_state = None

        if prompt_in.is_active:
            active_prompt = await self.prompt_repo.get_active_prompt()

            if active_prompt:
                await self.prompt_repo.deactivate_prompt(active_prompt)

        prompt_in.user_id = current_user_id
        prompt = await self.prompt_repo.create(prompt_in)
        new_prompt = PromptRead.model_validate(prompt)

        if active_prompt:
            old_prompt = PromptRead.model_validate(active_prompt)
            old_state = [{"section": s.section, "content": s.content} for s in old_prompt.system_message] if old_prompt else None

        new_state = [{"section": s.section, "content": s.content} for s in new_prompt.system_message]

        log = LogCreate(
            resource_type=ResourceType.SYSTEM_PROMPT,
            resource_id=str(new_prompt.id),
            action="create",
            user_id=current_user_id,
            details =
                {
                    "old_state": {
                        "version_name": old_prompt.version_name if old_prompt else None,
                        "is_active": old_prompt.is_active if old_prompt else None,
                        "system_message": old_state
                    },
                    "new_state": {
                        "version_name": new_prompt.version_name,
                        "is_active": new_prompt.is_active,
                        "system_message": new_state
                    }
                }
        )
        await self.log_repo.create(log)
        return new_prompt

    async def update(self, prompt_id: int, prompt_in: PromptUpdate, current_user_id: int) -> PromptRead:
        """Actualiza un prompt existente."""
        prompt_obj = await self.prompt_repo.get(prompt_id)
        if not prompt_obj:
            raise NotFoundException(f"Prompt con ID {prompt_id} no encontrado")

        updated_data = prompt_in.model_dump(exclude_unset=True)

        before_state = {field: getattr(prompt_obj, field) for field in updated_data.keys()}

        if prompt_in.is_active and not prompt_obj.is_active:
            active_prompt = await self.prompt_repo.get_active_prompt()
            if active_prompt and active_prompt.id != prompt_obj.id:
                await self.prompt_repo.deactivate_prompt(active_prompt)

        updated_prompt = await self.prompt_repo.update(db_obj=prompt_obj, obj_in=prompt_in)

        log = LogCreate(
            resource_type=ResourceType.SYSTEM_PROMPT,
            resource_id=str(prompt_id),
            action="update",
            user_id=current_user_id,
            details={
                "fields_updated": list(updated_data.keys()),
                "before_state": before_state,
                "after_state": updated_data
            }
        )
        await self.log_repo.create(log)

        return PromptRead.model_validate(updated_prompt)
