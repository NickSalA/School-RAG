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
        query = select(self.model).where(self.model.is_active)
        result = await self.session.exec(query)
        return result.one_or_none()

    async def deactivate_prompt(self, prompt: Prompt) -> Prompt:
        """Desactiva un prompt específico."""
        return await self.update(db_obj=prompt, obj_in={"is_active": False})
