"""Agente de asistencia normativa y permanencia estudiantil.

Este módulo implementa el FlowAgent, un asistente especializado en ayudar a estudiantes a encontrar soluciones normativas para evitar la deserción universitaria.
"""

from langchain.agents.middleware import ModelFallbackMiddleware

# Importa el wrapper base del agente
from app.agents.base import BaseAgent

# Importa el modelo de lenguaje
from app.adapters.gemini import get_llm
from app.adapters.groq import get_secondary_llm

# Importa la herramienta para buscar en la base de conocimientos
from app.agents.tools.retriever_tool import bc_tool
from app.agents.tools.feedback_tool import get_feedback_tool
from app.agents.tools.learning_tools import tool_personal_pref, tool_suggest_technical_fix

# Importa el checkpointer para la memoria
from app.agents.checkpointer import get_checkpointer, init_postgres_memory, get_store
from app.core.config import settings

from app.exceptions.cloud import AgentNotInitializedError

from loguru import logger

class FlowAgent:
    def __init__(self):
        self.llm = None
        self.agent_flow = None

    async def initialize(self):
        """Inicializa el agente creando su flujo con las herramientas necesarias."""
        if self.agent_flow is not None:
            return

        logger.info("[FlowAgent] Inicializando memoria PostgreSQL...")
        # Inicializamos la memoria PostgreSQL asíncronamente
        await init_postgres_memory()
        logger.info("[FlowAgent] Memoria PostgreSQL inicializada.")

        logger.info("[FlowAgent] Creando LLM primario (Gemini)...")
        primary_llm = get_llm()
        logger.info("[FlowAgent] LLM primario creado.")

        logger.info("[FlowAgent] Creando LLM secundario (Groq)...")
        secondary_llm = get_secondary_llm()
        logger.info("[FlowAgent] LLM secundario creado.")

        logger.info("[FlowAgent] Creando bc_tool (retriever)...")
        bc_tool_instance = await bc_tool(settings.INDEX_NAME)
        logger.info("[FlowAgent] bc_tool creado.")

        logger.info("[FlowAgent] Construyendo BaseAgent...")
        try:
            self.agent_flow = BaseAgent(
                llm=primary_llm,
                middlewares= ModelFallbackMiddleware(secondary_llm),
                tools = [bc_tool_instance, get_feedback_tool, tool_personal_pref, tool_suggest_technical_fix],
                memory=get_checkpointer(),
                store=get_store(),
                checkpoint_ns="school-rag",
            )
            logger.info("[FlowAgent] BaseAgent construido exitosamente.")
        except Exception as e:
            logger.exception("[FlowAgent] ERROR construyendo BaseAgent: {}", e)
            raise

    async def answer_message(self, message: str, system_prompt: str, thread_id: str = "", user_id: str = "anon") -> str:
        """Respuesta del agente"""
        if self.agent_flow is None:
            raise AgentNotInitializedError("El agente no ha sido inicializado. Llama a initialize() antes de usarlo.")

        return await self.agent_flow.answer(message, system_prompt, thread_id, user_id)

    def generate_thread_id(self) -> str:
        """Generar un nuevo ID de hilo para resetear la memoria"""
        if self.agent_flow is None:
            raise AgentNotInitializedError("El agente no ha sido inicializado. Llama a initialize() antes de usarlo.")
        return self.agent_flow.generate_thread_id()
