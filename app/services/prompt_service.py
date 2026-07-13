"""Servicio para la gestión de prompts, incluyendo la creación, actualización y recuperación del prompt activo."""

from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from app.agents.prompts import prompt_system

from app.models import ResourceType

from app.schemas import PromptCreate, PromptUpdate, PromptRead, PromptStructure
from app.schemas import LogCreate

from app.repositories import PromptRepository, LogRepository

from app.exceptions.database import NotFoundException
from app.exceptions.base import ConflictError, ValidationError


def _parse_version(version_name: str) -> tuple[int, int, int]:
    """Parsea una versión en formato X.Y.Z y la retorna como tupla de enteros."""
    parts = version_name.split(".")
    if len(parts) != 3:
        raise ValueError("El formato de versión debe ser X.Y.Z (ej: 26.1.0)")
    try:
        return tuple(int(p) for p in parts)  # type: ignore[return-value]
    except ValueError:
        raise ValueError("La versión debe contener solo números separados por puntos (ej: 26.1.0)")


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
                system_message.append(
                    PromptStructure(
                        section=section["section"], content=section["content"]
                    )
                )
            return PromptRead(
                id=0,
                version_name="default",
                system_message=system_message,
                user_id=None,
                is_active=True,
                created_at=datetime(2000, 1, 1),
            )
        return PromptRead.model_validate(db_prompt)

    async def create(self, prompt_in: PromptCreate, current_user_id: int) -> PromptRead:
        """Crea un nuevo prompt."""
        existing = await self.prompt_repo.get_by_version_name(prompt_in.version_name)
        if existing:
            raise ConflictError(f"Ya existe un prompt con la versión {prompt_in.version_name}")

        active_prompt = await self.prompt_repo.get_active_prompt()
        if active_prompt and active_prompt.version_name != "default":
            try:
                new_version = _parse_version(prompt_in.version_name)
                current_version = _parse_version(active_prompt.version_name)
                if new_version <= current_version:
                    raise ValidationError(
                        f"La nueva versión ({prompt_in.version_name}) debe ser superior a la versión activa actual ({active_prompt.version_name})"
                    )
            except ValueError as e:
                raise ValidationError(str(e))

        old_prompt = None
        old_state = None

        if prompt_in.is_active:
            if active_prompt:
                await self.prompt_repo.deactivate_other_prompts()
                old_prompt = PromptRead.model_validate(active_prompt)
                old_state = [
                    {"section": s.section, "content": s.content}
                    for s in old_prompt.system_message
                ]

        prompt_in.user_id = current_user_id
        prompt = await self.prompt_repo.create(prompt_in)
        if prompt.is_active:
            await self.prompt_repo.deactivate_other_prompts(prompt.id)
            prompt = await self.prompt_repo.get(prompt.id)
        new_prompt = PromptRead.model_validate(prompt)

        new_state = [
            {"section": s.section, "content": s.content}
            for s in new_prompt.system_message
        ]

        log = LogCreate(
            resource_type=ResourceType.SYSTEM_PROMPT,
            resource_id=str(new_prompt.id),
            action="create",
            user_id=current_user_id,
            details={
                "old_state": {
                    "version_name": old_prompt.version_name if old_prompt else None,
                    "is_active": old_prompt.is_active if old_prompt else None,
                    "system_message": old_state,
                },
                "new_state": {
                    "version_name": new_prompt.version_name,
                    "is_active": new_prompt.is_active,
                    "system_message": new_state,
                },
            },
        )
        await self.log_repo.create(log)
        return new_prompt

    async def update(
        self, prompt_id: int, prompt_in: PromptUpdate, current_user_id: int
    ) -> PromptRead:
        """Actualiza un prompt existente."""
        prompt_obj = await self.prompt_repo.get(prompt_id)
        if not prompt_obj:
            raise NotFoundException(f"Prompt con ID {prompt_id} no encontrado")

        updated_data = prompt_in.model_dump(exclude_unset=True)

        if "version_name" in updated_data:
            new_version_name = updated_data["version_name"]

            existing = await self.prompt_repo.get_by_version_name(new_version_name)
            if existing and existing.id != prompt_id:
                raise ConflictError(f"Ya existe un prompt con la versión {new_version_name}")

            active_prompt = await self.prompt_repo.get_active_prompt()
            if active_prompt and active_prompt.version_name != "default":
                try:
                    new_version = _parse_version(new_version_name)
                    current_version = _parse_version(active_prompt.version_name)
                    if new_version <= current_version:
                        raise ValidationError(
                            f"La nueva versión ({new_version_name}) debe ser superior a la versión activa actual ({active_prompt.version_name})"
                        )
                except ValueError as e:
                    raise ValidationError(str(e))

        before_state = {
            field: getattr(prompt_obj, field) for field in updated_data.keys()
        }

        if prompt_in.is_active and not prompt_obj.is_active:
            await self.prompt_repo.deactivate_other_prompts(prompt_obj.id)

        updated_prompt = await self.prompt_repo.update(
            db_obj=prompt_obj, obj_in=prompt_in
        )
        if updated_prompt.is_active:
            await self.prompt_repo.deactivate_other_prompts(updated_prompt.id)
            updated_prompt = await self.prompt_repo.get(updated_prompt.id)

        log = LogCreate(
            resource_type=ResourceType.SYSTEM_PROMPT,
            resource_id=str(prompt_id),
            action="update",
            user_id=current_user_id,
            details={
                "fields_updated": list(updated_data.keys()),
                "before_state": before_state,
                "after_state": updated_data,
            },
        )
        await self.log_repo.create(log)

        return PromptRead.model_validate(updated_prompt)
