"""Agente con memoria, personalizado por usuario"""

# Manejo de UUID para identificar sesiones de usuario
import uuid

# Utilitario para el modelo de lenguaje
from langchain_google_genai import ChatGoogleGenerativeAI

# Utilitarios para crear y ejecutar agentes
from app.core.agent import get_agent, execute

class CreateAgentFlow:
    def __init__(self,
        llm: ChatGoogleGenerativeAI,
        context: str,
        checkpoint_ns: str = "pucp-demo",
        tools: list | None = None,
        memory=None,
    ):
        self.llm = llm
        self.context = context
        self.tools = tools or []
        self.checkpoint_ns = checkpoint_ns
        self.memory = memory
        self.agent = get_agent(llm, context, self.tools, self.memory)

    async def answer(self, consulta: str = "", thread_id: str = ""):
        """Responder una consulta usando el agente con memoria."""
        return await execute(self.agent, consulta, config={
                "configurable": {
                    "thread_id": f"{thread_id}",
                    "checkpoint_ns": f"{self.checkpoint_ns}",
                }
            })

    def reset_memory(self) -> str:
        """Resetear la memoria del agente generando un nuevo ID de hilo."""
        thread = f"user:{'anon'}-{uuid.uuid4().hex}"
        return thread
