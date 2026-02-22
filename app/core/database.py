"""Conexión a la base de datos y gestión de sesiones."""

# Logging
from loguru import logger

# SQLAlchemy y SQLModel
from sqlmodel import Session, create_engine
from sqlalchemy.exc import OperationalError, IntegrityError, SQLAlchemyError

# Excepciones personalizadas
from app.exceptions.database import DatabaseConnectionError, DatabaseQueryError, DatabaseIntegrityError

# Importar configuración
from app.core.config import settings

DATABASE_URL: str = settings.DATABASE_URL

try:
    connect_args = {}
    if DATABASE_URL and not str(DATABASE_URL).startswith("sqlite"):
        connect_args = {"sslmode": "require"}

    engine = create_engine(
        DATABASE_URL, echo=False, future=True,
        pool_pre_ping=True, connect_args=connect_args
        )
except OperationalError as e:
    raise DatabaseConnectionError("Error de configuración a la BD.") from e

def get_session():
    """Proporciona una sesión de base de datos."""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
            logger.debug("Sesión de base de datos comprometida exitosamente.")

        except IntegrityError as e:
            session.rollback()
            raise DatabaseIntegrityError("Violación de integridad en la BD.") from e

        except OperationalError as e:
            session.rollback()
            raise DatabaseConnectionError("Error de conexión a la BD.") from e

        except SQLAlchemyError as e:
            session.rollback()
            raise DatabaseQueryError("Error al ejecutar la consulta en la BD.") from e

        except Exception:
            session.rollback()
            raise
