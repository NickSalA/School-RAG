"""Configuración de logging para la aplicación."""

# Sistema
import sys

# Logging
import inspect
import logging

# Simplificación de logging
from loguru import logger

# Integración con Logtail (Better Stack) Logging en la nube
try:
    from logtail import LogtailHandler
except ImportError:
    LogtailHandler = None

# Configuración de la aplicación
from app.core.config import settings
class InterceptHandler(logging.Handler):
    """Documentación oficial de Loguru para interceptar logs estándar de logging."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emite un registro de log."""
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup():
    """Configura el logging de la aplicación."""
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    handlers = [
        {
            "sink": sys.stderr,
            "level": settings.LOG_LEVEL,
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            "diagnose": False,
            "backtrace": False,
        },
        {
            "sink": "logs/app.log",
            "rotation": "50 MB",
            "retention": "10 days",
            "compression": "zip",
            "serialize": True, 
            "level": "INFO",
            "diagnose": True,
            "backtrace": True,
        },
    ]
    if LogtailHandler and settings.BETTER_STACK_TOKEN:
        handler_better_stack = LogtailHandler(source_token=settings.BETTER_STACK_TOKEN, host=settings.BETTER_STACK_HOST)
        handlers.append(
            {
                "sink": handler_better_stack,
                "level": "INFO",
                "format": "{message}",
            }
        )

    logger.configure(handlers =handlers) # type: ignore
    logging.getLogger("uvicorn.error").handlers = []
    logging.getLogger("uvicorn.error").propagate = False
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)

    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn").propagate = False

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
