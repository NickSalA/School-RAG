"""Agente de asistencia normativa y permanencia estudiantil.

Este módulo implementa el FlowAgent, un asistente especializado en ayudar a estudiantes a encontrar soluciones normativas para evitar la deserción universitaria.
"""

# Importa el wrapper base del agente
from app.agents.base import BaseAgent

# Importa el modelo de lenguaje
from app.adapters.gemini import get_llm
from app.adapters.groq import get_secondary_llm

# Importa la herramienta para buscar en la base de conocimientos
from app.agents.tools.retriever_tool import bc_tool
from app.agents.tools.feedback_tool import get_feedback_tool
# Importa el checkpointer para la memoria
from app.agents.checkpointer import get_checkpointer

from app.core.config import settings

from app.exceptions.cloud import AgentNotInitializedError


class FlowAgent:
    def __init__(self):
        self.llm = None
        self.agent_flow = None

    async def initialize(self):
        """Inicializa el agente creando su flujo con las herramientas necesarias."""
        if self.agent_flow is not None:
            return

        primary_llm = get_llm()
        secondary_llm = get_secondary_llm()
        self.llm = primary_llm.with_fallbacks([secondary_llm])

        bc_tool_instance = await bc_tool(settings.INDEX_NAME)

        self.agent_flow = BaseAgent(
            llm=self.llm,
            tools = [bc_tool_instance, get_feedback_tool],
            memory= get_checkpointer(),
            checkpoint_ns="school-rag",
        )

    async def answer_message(self, message: str, system_prompt: str, thread_id: str = "") -> str:
        """Respuesta del agente"""
        if self.agent_flow is None:
            raise AgentNotInitializedError("El agente no ha sido inicializado. Llama a initialize() antes de usarlo.")

        return await self.agent_flow.answer(message, system_prompt, thread_id)

    def generate_thread_id(self) -> str:
        """Generar un nuevo ID de hilo para resetear la memoria"""
        if self.agent_flow is None:
            raise AgentNotInitializedError("El agente no ha sido inicializado. Llama a initialize() antes de usarlo.")
        return self.agent_flow.generate_thread_id()
