"""Utilidades para formatear contenido y mensajes de conversación."""

from app.schemas.prompt_schema import PromptStructure

def format_prompt(obj: list[PromptStructure]) -> str:
    """Formatea una lista de diccionarios como texto legible."""
    if not isinstance(obj, list):
        return str(obj)

    formatted_lines = []
    for item in obj:
        if isinstance(item, dict):
            formatted_lines.extend(f"{key.upper()}: {value}" for key, value in item.items())
        else:
            formatted_lines.append(str(item))
    return "\n\n".join(formatted_lines)

def format_message(user: str, agent: str) -> list[dict]:
    """Formatea una conversación de mensajes en una lista de diccionarios con roles."""
    formatted = []
    formatted.append({"role": "user", "content": user})
    formatted.append({"role": "agent", "content": agent})
    return formatted
