"""Middleware de logging usando Loguru y FastAPI."""

# Libreria para extraer el tiempo de procesamiento
import time

# Tipado
from typing import Callable
import uuid

# Logging
from loguru import logger

# FastAPI
from fastapi import Request, Response

from starlette.middleware.base import BaseHTTPMiddleware

class LoguruMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Intercepta la petición, agrega un Request ID único y contexto al logger."""

        request_id=request.headers.get("X-Request-ID", "Desconocido")
        if not request_id or request_id == "Desconocido":
            request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        with logger.contextualize(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "Desconocido",
        ):

            start_time = time.time()

            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Request-ID"] = request_id
            logger.info(
                f"{request.method} {request.url.path} | Request: {response.status_code} "
                f"(Tiempo: {process_time:.2f}s)"
            )
            return response
