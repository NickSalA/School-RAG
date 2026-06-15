"""Servicio para la lógica de negocio relacionada con usuarios."""

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import ResourceType, Role, User
from app.repositories import UserRepository, LogRepository
from app.schemas import UserCreate, UserUpdate, UserRead, LogCreate

from app.exceptions.auth import PermissionDeniedError, UserNotFoundError


class UserService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.log_repo = LogRepository(session)

    @staticmethod
    def _is_staff(user: User) -> bool:
        return user.role in {Role.ADMIN, Role.SUPERADMIN}

    async def create(self, user_in: UserCreate, current_user: User) -> UserRead:
        """Crea un nuevo usuario."""
        if not self._is_staff(current_user):
            raise PermissionDeniedError("No tienes permisos para crear usuarios.")
        if current_user.role != Role.SUPERADMIN and user_in.role != Role.USER:
            raise PermissionDeniedError(
                "Solo SUPERADMIN puede crear usuarios con roles administrativos."
            )

        user = await self.user_repo.create(user_in)

        if self.log_repo:
            log = LogCreate(
                resource_type=ResourceType.USER,
                resource_id=user.name,
                action="create",
                user_id=current_user.id,
                details={
                    "user_id": user.id,
                    "email": user.email,
                    "role": user.role.value,
                },
            )

            await self.log_repo.create(log)

        return UserRead.model_validate(user)

    async def get(self, user_id: int, current_user: User) -> UserRead:
        """Obtiene un usuario por su ID."""
        if current_user.id != user_id and not self._is_staff(current_user):
            raise PermissionDeniedError(
                "No tienes permisos para consultar este usuario."
            )

        user = await self.user_repo.get(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado")
        return UserRead.model_validate(user)

    async def list_users(self, current_user: User) -> list[UserRead]:
        """Lista todos los usuarios."""
        if not self._is_staff(current_user):
            raise PermissionDeniedError("No tienes permisos para listar usuarios.")

        users = await self.user_repo.get_all()
        return [UserRead.model_validate(u) for u in users]

    async def update(
        self, user_id: int, user_in: UserUpdate, current_user: User
    ) -> UserRead:
        """Actualiza un usuario existente."""
        if current_user.id != user_id and not self._is_staff(current_user):
            raise PermissionDeniedError(
                "No tienes permisos para modificar este usuario."
            )

        user = await self.user_repo.get(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado")
        if (
            current_user.id != user_id
            and current_user.role == Role.ADMIN
            and user.role != Role.USER
        ):
            raise PermissionDeniedError(
                "Solo SUPERADMIN puede modificar usuarios administrativos."
            )
        if user_in.role is not None and current_user.role != Role.SUPERADMIN:
            raise PermissionDeniedError("Solo SUPERADMIN puede cambiar roles.")

        if self.log_repo:
            log = LogCreate(
                resource_type=ResourceType.USER,
                resource_id=user.name,
                action="update",
                user_id=current_user.id,
                details={
                    "user_id": user.id,
                    "email": user.email,
                    "role": user.role.value,
                },
            )

            await self.log_repo.create(log)

        updated_user = await self.user_repo.update(db_obj=user, obj_in=user_in)
        return UserRead.model_validate(updated_user)

    async def delete(self, user_id: int, current_user: User) -> None:
        """Elimina un usuario."""
        if current_user.id != user_id and not self._is_staff(current_user):
            raise PermissionDeniedError(
                "No tienes permisos para eliminar este usuario."
            )

        user = await self.user_repo.get(user_id)
        if not user:
            raise UserNotFoundError(f"Usuario con ID {user_id} no encontrado")
        if (
            current_user.id != user_id
            and current_user.role == Role.ADMIN
            and user.role != Role.USER
        ):
            raise PermissionDeniedError(
                "Solo SUPERADMIN puede eliminar usuarios administrativos."
            )

        if self.log_repo:
            log = LogCreate(
                resource_type=ResourceType.USER,
                resource_id=user.name,
                action="delete",
                user_id=current_user.id,
                details={
                    "user_id": user.id,
                    "email": user.email,
                    "role": user.role.value,
                },
            )

            await self.log_repo.create(log)
        await self.user_repo.delete(user_id)
