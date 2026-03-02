"""Servicio para la lógica de negocio relacionada con usuarios."""

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories import UserRepository
from app.schemas import UserCreate, UserUpdate, UserRead

from app.exceptions.auth import UserNotFoundError

class UserService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)

    async def create(self, user_in: UserCreate) -> UserRead:
        """Crea un nuevo usuario."""
        user = await self.user_repo.create(user_in)
        return UserRead.model_validate(user)

    async def get(self, user_id: int) -> UserRead:
        """Obtiene un usuario por su ID."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado")
        return UserRead.model_validate(user)

    async def list_users(self) -> list[UserRead]:
        """Lista todos los usuarios."""
        users = await self.user_repo.get_all()
        return [UserRead.model_validate(u) for u in users]

    async def update(self, user_id: int, user_in: UserUpdate) -> UserRead:
        """Actualiza un usuario existente."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado")

        updated_user = await self.user_repo.update(db_obj=user, obj_in=user_in)
        return UserRead.model_validate(updated_user)

    async def delete(self, user_id: int) -> None:
        """Elimina un usuario."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado")
        await self.user_repo.delete(user_id)
