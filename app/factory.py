"""Patrón Factory para crear la aplicación."""

# Context manager para lifespan
from contextlib import asynccontextmanager

# Logging
from loguru import logger

# SQLAlchemy
from sqlalchemy import text

# FastAPI y middlewares
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Configuración del sistema
from app.core.config import settings

# Configuración de logging
from app.core.logger import setup

# Middleware para logging
from app.core.middleware import LoguruMiddleware

# Excepciones personalizadas
from app.exceptions.base import AppError

from app.adapters.openai import configure_embedding

from app.core.database import engine

# Routers
from app.api.routes.chat_router import router as chat_router
from app.api.routes.documents_router import router as documents_router
from app.api.routes.auth_router import router as auth_router
from app.api.routes.user_router import router as user_router
from app.api.routes.prompt_router import router as prompt_router
from app.api.routes.conversation_router import router as conversation_router

def create() -> FastAPI:
    """Crea y configura la aplicación FastAPI."""

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        """
        Context manager para el ciclo de vida de la aplicación.
        """
        logger.info("Iniciando la aplicación Posgrado Backend...")
        setup()
        configure_embedding()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Configuración establecida exitosamente.")
        yield
        await engine.dispose()
        logger.info("Cerrando la aplicación Posgrado Backend...")

    app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)

    app.include_router(chat_router, prefix=settings.GLOBAL_PREFIX, tags=["Chat"])
    app.include_router(documents_router, prefix=f"{settings.GLOBAL_PREFIX}/documents", tags=["Documentos"])
    app.include_router(auth_router, prefix=f"{settings.GLOBAL_PREFIX}/auth", tags=["Autenticación"])
    app.include_router(user_router, prefix=f"{settings.GLOBAL_PREFIX}/users", tags=["Usuarios"])
    app.include_router(prompt_router, prefix=f"{settings.GLOBAL_PREFIX}/prompts", tags=["Prompts"])
    app.include_router(conversation_router, prefix=f"{settings.GLOBAL_PREFIX}/conversations", tags=["Conversaciones"])

    # CORS (ajusta origins a tu front real)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Cookie de sesión
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        same_site="lax",
        https_only=False,   # pon True en producción HTTPS
        # session_cookie="support_session",
    )

    # Middleware de logging con Loguru
    app.add_middleware(LoguruMiddleware)

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """
        Gestor global para excepciones de AppError.
        Args:
            request (Request): Objeto de la solicitud entrante.
            exc (AppError): Excepción capturada.
        Returns:
            JSONResponse: Respuesta JSON con detalles del error.
        """
        status_code = getattr(exc, "status_code", 500)
        request_id = getattr(request.state, "request_id", "Desconocido")
        if status_code >= 500:
            logger.error(f"[{request_id}] CRITICO: {str(exc)}")
        elif status_code >= 400:
            logger.warning(f"[{request_id}] CLIENTE: {str(exc)}")
        else:
            logger.info(f"[{request_id}] INFO: {str(exc)}")
        return JSONResponse(
            status_code=status_code,
            content={
                "error": True, 
                "type": exc.__class__.__name__, 
                "message": str(exc)},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Gestor global para excepciones no manejadas. Evita exponer detalles internos.
        Args:
            request (Request): Objeto de la solicitud entrante.
            exc (Exception): Excepción capturada.
        Returns:
            JSONResponse: Respuesta JSON genérica de error.
        """
        request_id = getattr(request.state, "request_id", "Desconocido")
        error_message = f"{type(exc).__name__}: {str(exc)}"
        logger.exception(f"[{request_id}] Error no manejado: {error_message}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "type": "InternalServerError",
                "message": "Ocurrió un error interno en el servidor.",
            },
        )

    @app.get("/")
    def home():
        """Endpoint raíz para verificar que la API está activa."""
        return {"ok": True, "msg": "API de Posgrado activa."}

    return app
