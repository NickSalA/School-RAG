"""Gestión del estado/memoria de conversaciones del agente."""
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings
from loguru import logger

_raw_conn_string = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
# Agregar sslmode al connection string si no lo tiene
if "sslmode" not in _raw_conn_string:
    separator = "&" if "?" in _raw_conn_string else "?"
    _conn_string = f"{_raw_conn_string}{separator}sslmode=require"
else:
    _conn_string = _raw_conn_string

_pool = None
_saver = None
_store = None

async def init_postgres_memory():
    """Inicializa el pool de PostgreSQL y los recursos de estado del agente."""
    global _pool, _saver, _store
    if _saver is not None:
        return _saver, _store

    # prepare_threshold=0 desactiva prepared statements (requerido para pgbouncer/Supabase)
    # row_factory=dict_row requerido por LangGraph (AsyncConnection[DictRow])
    logger.info("[Checkpointer] Creando pool de conexiones (psycopg, sin prepared statements)...")
    _pool = AsyncConnectionPool(
        conninfo=_conn_string,
        open=False,
        kwargs={"prepare_threshold": 0, "row_factory": dict_row, "autocommit": True},
    )
    await _pool.open()
    logger.info("[Checkpointer] Pool creado y abierto.")

    logger.info("[Checkpointer] Configurando AsyncPostgresSaver...")
    _saver = AsyncPostgresSaver(_pool)
    await _saver.setup()
    logger.info("[Checkpointer] Saver configurado.")

    logger.info("[Checkpointer] Creando embeddings OpenAI para store...")
    embeddings = OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL_NAME,
        api_key=settings.OPENAI_API
    )
    logger.info("[Checkpointer] Embeddings creados.")

    # LangGraph Store: usa un dict con embed function y dims
    index_config = {
        "embed": embeddings,
        "dims": 768,
    }

    logger.info("[Checkpointer] Configurando AsyncPostgresStore...")
    _store = AsyncPostgresStore(_pool, index=index_config)
    await _store.setup()
    logger.info("[Checkpointer] Store configurado.")

    return _saver, _store

def get_checkpointer() -> AsyncPostgresSaver:
    if _saver is None:
        raise RuntimeError("Postgres memory not initialized. Llama init_postgres_memory() al iniciar la app.")
    return _saver

def get_store() -> AsyncPostgresStore:
    if _store is None:
        raise RuntimeError("Postgres memory not initialized. Llama init_postgres_memory() al iniciar la app.")
    return _store

async def close_postgres_memory():
    global _pool, _saver, _store
    if _pool:
        await _pool.close()
        _pool = None
    _saver = None
    _store = None
