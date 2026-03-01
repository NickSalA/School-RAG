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
            try:
                response = await call_next(request)
                process_time = time.time() - start_time
                log_message = f"{request.method} {request.url.path} | Status: {response.status_code} ({process_time:.2f}s)"
                if response.status_code >= 500:
                    logger.error(log_message)
                else:
                    logger.info(log_message)

                return response

            except Exception as e:
                process_time = time.time() - start_time
                error_type = type(e).__name__
                error_details = str(e).rsplit('\n', maxsplit=1)[0]
                logger.error(
                    f"{request.method} {request.url.path} | ERROR: {error_type}: {error_details} "
                    f"({process_time:.2f}s)"
                )
                raise e
