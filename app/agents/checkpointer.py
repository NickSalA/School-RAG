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

    logger.info("[Checkpointer] Creando pool de conexiones (psycopg, sin prepared statements)...")
    pool: AsyncConnectionPool[AsyncConnection[DictRow]] = AsyncConnectionPool(
        conninfo=settings.CONN_STRING,
        open=False,
        kwargs={"prepare_threshold": 0, "row_factory": dict_row, "autocommit": True},
    )
    await pool.open()
    logger.info("[Checkpointer] Pool creado y abierto.")

    logger.info("[Checkpointer] Configurando AsyncPostgresSaver...")
    saver = AsyncPostgresSaver(pool)
    await saver.setup()
    logger.info("[Checkpointer] Saver configurado.")

    logger.info("[Checkpointer] Creando embeddings OpenAI para store...")
    embeddings = get_embedding()
    logger.info("[Checkpointer] Embeddings creados.")

    index_config = PostgresIndexConfig(
        embed=embeddings,
        dims=768,
    )

    logger.info("[Checkpointer] Configurando AsyncPostgresStore...")
    store = AsyncPostgresStore(pool, index=index_config)
    await store.setup()
    logger.info("[Checkpointer] Store configurado.")

    return pool, saver, store
