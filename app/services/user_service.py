"""Servicio para la lógica de negocio relacionada con usuarios."""

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import ResourceType
from app.repositories import UserRepository, LogRepository
from app.schemas import UserCreate, UserUpdate, UserRead, LogCreate

from app.exceptions.auth import UserNotFoundError

class UserService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.log_repo = LogRepository(session)

    async def create(self, user_in: UserCreate, user_id: int) -> UserRead:
        """Crea un nuevo usuario."""
        user = await self.user_repo.create(user_in)

        if self.log_repo:
            log = LogCreate(
            resource_type=ResourceType.USER,
            resource_id=user.name,
            action="create",
            user_id=user_id,
            details={"user_id": user.id, "email": user.email, "role": user.role.value}
        )

            await self.log_repo.create(log)

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

    async def update(self, user_id: int, user_in: UserUpdate, current_user_id: int) -> UserRead:
        """Actualiza un usuario existente."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado")
        if self.log_repo:
            log = LogCreate(
            resource_type=ResourceType.USER,
            resource_id=user.name,
            action="update",
            user_id=current_user_id,
            details={"user_id": user.id , "email": user.email, "role": user.role.value}
        )

            await self.log_repo.create(log)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado")

        updated_user = await self.user_repo.update(db_obj=user, obj_in=user_in)
        return UserRead.model_validate(updated_user)

    async def delete(self, user_id: int, current_user_id: int) -> None:
        """Elimina un usuario."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado")
        if self.log_repo:
            log = LogCreate(
            resource_type=ResourceType.USER,
            resource_id=user.name,
            action="delete",
            user_id=current_user_id,
            details={"user_id": user.id , "email": user.email, "role": user.role.value}
        )

            await self.log_repo.create(log)
        await self.user_repo.delete(user_id)
