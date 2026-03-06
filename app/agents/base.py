"""Wrapper para crear y gestionar agentes conversacionales con memoria persistente."""

# Manejo de UUID para identificar sesiones de usuario
import uuid

# Utilitario para el modelo de lenguaje
from langchain_core.language_models.chat_models import BaseChatModel

# Utilitario para crear agentes
from langchain.agents import create_agent

# Utilitarios para crear y ejecutar agentes
from app.agents.executor import execute

from loguru import logger

class BaseAgent:
    def __init__(self,
        llm: BaseChatModel,
        middlewares,
        checkpoint_ns: str = "school-rag",
        tools: list | None = None,
        memory=None,
        store=None,
    ):
        self.checkpoint_ns = checkpoint_ns
        self.store = store
        # Asegurar que middleware sea siempre una lista
        if middlewares is None:
            mw_list = []
        elif isinstance(middlewares, (list, tuple)):
            mw_list = list(middlewares)
        else:
            mw_list = [middlewares]
        logger.info("[BaseAgent] Llamando create_agent con model={}, tools={}, checkpointer={}, store={}, middleware count={}",
            type(llm).__name__, len(tools or []), type(memory).__name__, type(store).__name__, len(mw_list))
        self.agent = create_agent(model=llm, tools=tools or [], checkpointer=memory, store=store, middleware=mw_list)
        logger.info("[BaseAgent] create_agent completado.")

    def get_store(self):
        """Obtener el store del agente para acceder a la memoria."""
        return self.store

    async def answer(self, query: str, system_prompt: str, thread_id: str = "", user_id: str = "anon") -> str:
        """Responder una consulta usando el agente con memoria."""
        config={
                "configurable": {
                    "thread_id": f"{thread_id}",
                    "checkpoint_ns": f"{self.checkpoint_ns}",
                    "user_id": user_id,
                }
            }
        return await execute(self.agent, query=query, system_prompt=system_prompt, config=config)

    def generate_thread_id(self) -> str:
        """Generar un nuevo ID de hilo para resetear la memoria."""
        thread = f"user:{'anon'}-{uuid.uuid4().hex}"
        return thread
