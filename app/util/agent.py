"""Funciones utilitarias para crear y ejecutar agentes de LangGraph."""

# Utilitario para crear y ejecutar agentes
from langchain.agents import create_agent

# Manejo de memoria del agente
from langgraph.checkpoint.memory import InMemorySaver

from google.api_core.exceptions import ServiceUnavailable, ResourceExhausted, DeadlineExceeded, Aborted
from app.exceptions.cloud import AgentExecutionError, AgentNotAvailableError, AgentResponseError, GenerativeAIQuotaError, GenerativeAITimeoutError

def get_agent(
    llm,
    tools: list | None = None,
    memory=None,
):
    """Crear un agente con las herramientas y contexto dados."""
    if tools is None:
        tools = []
    agent = create_agent(
        model=llm, tools=tools, checkpointer=memory if memory else InMemorySaver()
    )
    return agent

async def execute(agent, query: str, system_prompt: str, config=None, verbose: bool = True):
    """Ejecutar el agente con la consulta dada y configuración opcional."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": query})
    payload = {"messages": messages}

    try:
        response = await agent.ainvoke(payload, config=config)
        if not verbose:
            return response
        if not response or "messages" not in response or not response["messages"]:
            raise AgentExecutionError("Respuesta inválida del agente.")

        response = response["messages"][-1].content

        if isinstance(response, str):
            return response

        response = response[0].get("text", "")
        return response
    except (ServiceUnavailable, Aborted) as e:
        raise AgentNotAvailableError(f'El agente no está disponible: {e}') from e
    except ResourceExhausted as e:
        raise GenerativeAIQuotaError(f'El agente ha alcanzado su límite de recursos: {e}') from e
    except DeadlineExceeded as e:
        raise GenerativeAITimeoutError(f'El agente ha excedido el tiempo de espera: {e}') from e
    except (KeyError, IndexError, AttributeError) as e:
        raise AgentResponseError(f'Error al procesar la respuesta del agente: {e}') from e
    except Exception as e:
        raise AgentExecutionError(f'Error en la ejecución del agente: {e}') from e
