"""Este módulo define el repositorio específico para la entidad "Prompt"""

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.models import Prompt
from app.schemas import PromptCreate, PromptUpdate
from app.repositories import BaseRepository


class PromptRepository(BaseRepository[Prompt, PromptCreate, PromptUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Prompt, session=session)

    async def get_active_prompt(self) -> Prompt | None:
        """Obtiene la versión activa del prompt."""
        query = (
            select(self.model)
            .where(self.model.is_active)
            .order_by(self.model.created_at.desc())
            .limit(1)
        )
        result = await self.session.exec(query)
        return result.first()

    async def get_by_version_name(self, version_name: str) -> Prompt | None:
        """Obtiene un prompt por su nombre de versión."""
        query = select(self.model).where(self.model.version_name == version_name)
        result = await self.session.exec(query)
        return result.first()

    async def deactivate_other_prompts(
        self, active_prompt_id: int | None = None
    ) -> None:
        """Desactiva todos los prompts activos, opcionalmente excluyendo uno."""
        query = select(self.model).where(self.model.is_active)
        if active_prompt_id is not None:
            query = query.where(self.model.id != active_prompt_id)

        result = await self.session.exec(query)
        prompts = result.all()
        for prompt in prompts:
            prompt.is_active = False
            self.session.add(prompt)

        if prompts:
            await self.session.commit()
