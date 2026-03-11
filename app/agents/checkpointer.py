"""Gestión del estado/memoria de conversaciones del agente."""

from loguru import logger

from psycopg import AsyncConnection
from psycopg.rows import DictRow, dict_row
from psycopg_pool import AsyncConnectionPool

from langgraph.store.postgres.base import PostgresIndexConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore

from app.adapters.openai import get_embedding
from app.core.config import settings

async def init_postgres_memory():
    """Inicializa el pool de PostgreSQL y los recursos de estado del agente."""

    logger.debug("[Checkpointer] Creando pool de conexiones (psycopg, sin prepared statements)...")
    pool: AsyncConnectionPool[AsyncConnection[DictRow]] = AsyncConnectionPool(
        conninfo=settings.CONN_STRING,
        open=False,
        kwargs={"prepare_threshold": 0, "row_factory": dict_row, "autocommit": True},
    )
    await pool.open()
    logger.debug("[Checkpointer] Pool creado y abierto.")

    logger.debug("[Checkpointer] Configurando AsyncPostgresSaver...")
    saver = AsyncPostgresSaver(pool)
    await saver.setup()
    logger.debug("[Checkpointer] Saver configurado.")

    logger.debug("[Checkpointer] Creando embeddings OpenAI para store...")
    embeddings = get_embedding()
    logger.debug("[Checkpointer] Embeddings creados.")

    index_config = PostgresIndexConfig(
        embed=embeddings,
        dims=768,
    )

    logger.debug("[Checkpointer] Configurando AsyncPostgresStore...")
    store = AsyncPostgresStore(pool, index=index_config)
    await store.setup()
    logger.debug("[Checkpointer] Store configurado.")

    return pool, saver, store
