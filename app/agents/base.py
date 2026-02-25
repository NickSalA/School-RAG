"""Wrapper para crear y gestionar agentes conversacionales con memoria persistente."""

# Manejo de UUID para identificar sesiones de usuario
import uuid

# Utilitario para el modelo de lenguaje
from langchain_core.runnables import Runnable

# Utilitarios para crear y ejecutar agentes
from app.agents.executor import get_agent, execute

class BaseAgent:
    def __init__(self,
        llm: Runnable,
        checkpoint_ns: str = "school-rag",
        tools: list | None = None,
        memory=None,
    ):
        self.checkpoint_ns = checkpoint_ns
        self.agent = get_agent(llm, tools or [], memory)

    async def answer(self, consulta: str, system_prompt: str, thread_id: str = "") -> str:
        """Responder una consulta usando el agente con memoria."""
        config={
                "configurable": {
                    "thread_id": f"{thread_id}",
                    "checkpoint_ns": f"{self.checkpoint_ns}",
                }
            }
        return await execute(self.agent, query=consulta, system_prompt=system_prompt, config=config)

    def generate_thread_id(self) -> str:
        """Generar un nuevo ID de hilo para resetear la memoria."""
        thread = f"user:{'anon'}-{uuid.uuid4().hex}"
        return thread
