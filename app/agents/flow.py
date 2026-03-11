"""Agente de asistencia normativa y permanencia estudiantil.

Este módulo implementa el FlowAgent, un asistente especializado en ayudar a estudiantes a encontrar soluciones normativas para evitar la deserción universitaria.
"""

from loguru import logger

from langchain.agents.middleware import ModelFallbackMiddleware

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore

# Importa el wrapper base del agente
from app.agents.base import BaseAgent

# Importa el modelo de lenguaje
from app.adapters.gemini import get_llm
from app.adapters.groq import get_secondary_llm

# Importa la herramienta para buscar en la base de conocimientos
from app.agents.tools.retriever_tool import bc_tool
from app.agents.tools.feedback_tool import get_feedback_tool
from app.agents.tools.learning_tools import tool_personal_pref, tool_suggest_technical_fix

from app.core.config import settings

from app.exceptions.cloud import AgentNotInitializedError

class FlowAgent:
    def __init__(self):
        self.llm = None
        self.agent_flow = None

    async def initialize(self, saver: AsyncPostgresSaver ,store: AsyncPostgresStore):
        """Inicializa el agente creando su flujo con las herramientas necesarias."""
        if self.agent_flow is not None:
            return

        logger.debug("[FlowAgent] Creando LLM primario (Gemini)...")
        primary_llm = get_llm()
        logger.debug("[FlowAgent] LLM primario creado.")

        logger.debug("[FlowAgent] Creando LLM secundario (Groq)...")
        secondary_llm = get_secondary_llm()
        logger.debug("[FlowAgent] LLM secundario creado.")

        logger.debug("[FlowAgent] Creando bc_tool (retriever)...")
        bc_tool_instance = await bc_tool(settings.INDEX_NAME)
        logger.debug("[FlowAgent] bc_tool creado.")

        logger.debug("[FlowAgent] Construyendo BaseAgent...")
        try:
            self.agent_flow = BaseAgent(
                llm=primary_llm,
                middlewares= [ModelFallbackMiddleware(secondary_llm)],
                tools = [bc_tool_instance, get_feedback_tool, tool_personal_pref, tool_suggest_technical_fix],
                memory=saver,
                store=store,
            )
            logger.debug("[FlowAgent] BaseAgent construido exitosamente.")
        except Exception as e:
            raise AgentNotInitializedError(f"Error al inicializar el agente: {e}") from e

    async def answer_message(self, message: str, system_prompt: str, conversation_id: int, checkpoint_ns: int) -> str:
        """Respuesta del agente"""
        if self.agent_flow is None:
            raise AgentNotInitializedError("El agente no ha sido inicializado. Llama a initialize() antes de usarlo.")

        return await self.agent_flow.answer(message, system_prompt, conversation_id, checkpoint_ns)
