"""Servicio de autenticación para manejar el login de usuarios y generación de tokens JWT."""

from sqlmodel.ext.asyncio.session import AsyncSession
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token
from app.schemas.auth_schema import LoginRequest, LoginResponse
from app.schemas.user_schema import UserRead

from app.exceptions.auth import InvalidCredentialsError, UserNotFoundError

class AuthService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)

    async def login(self, credentials: LoginRequest) -> LoginResponse:
        """Autentica a un usuario y genera un token de acceso JWT."""
        user = await self.user_repo.get_by_name(credentials.username)

        if not user:
            raise UserNotFoundError("Usuario no encontrado.")

        if not verify_password(credentials.password, user.password):
            raise InvalidCredentialsError("Credenciales inválidas.")

        access_token = create_access_token(data={"sub": user.id, "role": user.role.value if hasattr(user.role, 'value') else user.role})

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserRead.model_validate(user)
        )
