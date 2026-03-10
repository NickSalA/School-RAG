"""Wrapper para crear y gestionar agentes conversacionales con memoria persistente."""

from loguru import logger

# Utilitario para el modelo de lenguaje
from langchain_core.language_models.chat_models import BaseChatModel

# Utilitario para crear agentes
from langchain.agents import create_agent

# Utilitarios para crear y ejecutar agentes
from app.agents.executor import execute

class BaseAgent:
    def __init__(self,
        llm: BaseChatModel,
        middlewares: list | None = None,
        tools: list | None = None,
        memory=None,
        store=None,
    ):
        self.store = store

        self.agent = create_agent(model=llm, tools=tools or [], checkpointer=memory, store=store, middleware=middlewares or [])
        logger.debug("[BaseAgent] create_agent completado.")

    def get_store(self):
        """Obtener el store del agente para acceder a la memoria."""
        return self.store

    async def answer(self, query: str, system_prompt: str, conversation_id: int, checkpoint_ns: int) -> str:
        """Responder una consulta usando el agente con memoria."""
        if not conversation_id or not checkpoint_ns:
            raise ValueError("conversation_id y checkpoint_ns deben ser proporcionados para la respuesta del agente.")
        config={
                "configurable": {
                    "thread_id": f"{conversation_id}",
                    "checkpoint_ns": f"user-{checkpoint_ns}",
                }
            }
        return await execute(self.agent, query=query, system_prompt=system_prompt, config=config)
