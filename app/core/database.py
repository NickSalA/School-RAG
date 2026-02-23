"""Conexión a la base de datos y gestión de sesiones."""

import ssl
from contextlib import asynccontextmanager

# Logging
from loguru import logger


# SQLAlchemy y SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import OperationalError, IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine

# Excepciones personalizadas
from app.exceptions.database import DatabaseConnectionError, DatabaseQueryError, DatabaseIntegrityError

# Importar configuración
from app.core.config import settings

DATABASE_URL: str = settings.DATABASE_URL

try:
    connect_args = {"server_settings": {"search_path": "school_rag, public"}}
    if DATABASE_URL and not str(DATABASE_URL).startswith("sqlite"):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # 3. Le pasamos el contexto en lugar de 'True'
        connect_args = {"ssl": ctx}

    engine = create_async_engine(
        DATABASE_URL, echo=False, future=True,
        pool_pre_ping=True, connect_args=connect_args
        )
except OperationalError as e:
    raise DatabaseConnectionError(f"Error de configuración a la BD: {e}") from e

async def get_session():
    """Proporciona una sesión de base de datos."""
    async with AsyncSession(engine) as session:
        try:
            yield session
            await session.commit()
            logger.debug("Sesión de base de datos comprometida exitosamente.")

        except IntegrityError as e:
            await session.rollback()
            raise DatabaseIntegrityError(f"Violación de integridad en la BD: {e}") from e

        except OperationalError as e:
            await session.rollback()
            raise DatabaseConnectionError(f"Error de conexión a la BD: {e}") from e

        except SQLAlchemyError as e:
            await session.rollback()
            raise DatabaseQueryError(f"Error al ejecutar la consulta en la BD: {e}") from e

        except Exception:
            await session.rollback()
            raise

get_session_context = asynccontextmanager(get_session)
