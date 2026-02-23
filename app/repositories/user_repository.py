"""Este módulo define el repositorio específico para la entidad "User."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_password_hash
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=User, session=session)

    async def create(self, obj_in: UserCreate) -> User:
        """Crea un usuario encriptando su contraseña antes de guardar."""
        hashed_password = get_password_hash(obj_in.password)
        obj_in.password = hashed_password

        return await super().create(obj_in)

    async def get_by_email(self, email: str) -> User | None:
        """Busca un usuario por su correo electrónico (útil para el Login)."""
        query = select(self.model).where(self.model.email == email)
        result = await self.session.exec(query)

        return result.first()

    async def get_by_name(self, name: str) -> User | None:
        """Busca un usuario por su nombre."""
        query = select(self.model).where(self.model.name == name)
        result = await self.session.exec(query)

        return result.first()
