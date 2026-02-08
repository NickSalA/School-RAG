"""Funciones utilitarias para crear y ejecutar agentes de LangGraph."""

# Utilitario para crear y ejecutar agentes
from langchain.agents import create_agent

# Utilitario para el modelo de lenguaje
from langchain_google_genai import ChatGoogleGenerativeAI

# Manejo de memoria del agente
from langgraph.checkpoint.memory import InMemorySaver

from app.exceptions.cloud import AgentExecutionError

def get_agent(
    llm: ChatGoogleGenerativeAI,
    context: str,
    tools: list | None = None,
    memory=None
):
    """Crear un agente con las herramientas y contexto dados."""
    if tools is None:
        tools = []
    agent = create_agent(
        model=llm, tools=tools, checkpointer=memory if memory else InMemorySaver(), system_prompt=context,
    )
    return agent

async def execute(agent, query: str = "", config=None, verbose: bool = True):
    """Ejecutar el agente con la consulta dada y configuración opcional."""
    payload = {"messages": [{"role": "user", "content": query}]}

    response = await agent.ainvoke(payload, config=config)
    try:
        if not verbose:
            return response
        response = response["messages"][-1].content

        if isinstance(response, str):
            return response

        response = response[0].get("text", "")

        return response
    except Exception as e:
        raise AgentExecutionError(f'Error en la ejecución del agente: {e}') from e
