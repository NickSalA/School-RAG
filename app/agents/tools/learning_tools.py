"""Herramientas de aprendizaje y memoria del agente."""
import uuid
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

@tool
async def tool_personal_pref(preference: str, config: RunnableConfig) -> str:
    """Guarda una preferencia personal del usuario.
    
    Usa esta herramienta cuando el usuario exprese explícitamente una preferencia
    sobre cómo quiere interactuar o qué información prefiere.
    
    Args:
        preference (str): La preferencia explícita a guardar.
    """
    store = config.get("store")
    if not store:
        return "Error: Store (Memoria semántica) no disponible."

    user_id = config.get("configurable", {}).get("user_id")
    if not user_id:
        return "Error: Usuario no identificado."

    namespace = ("users", str(user_id), "prefs")

    key = str(uuid.uuid4())
    await store.aput(namespace, key, {"preference": preference})

    return "Preferencia guardada exitosamente."


@tool
async def tool_suggest_technical_fix(correction: str, config: RunnableConfig) -> str:
    """Registra una corrección técnica o sugerencia global proporcionada por el usuario.
    
    Usa esta herramienta cuando el usuario informe de un error en el conocimiento
    del agente, como un endpoint incorrecto o una regla normativa desactualizada.
    A los 3 votos acumulados, la sugerencia se vuelve una regla verificada global.
    
    Args:
        correction (str): La corrección técnica o validación sugerida.
    """
    store = config.get("store")
    if not store:
        return "Error: Store (Memoria semántica) no disponible."

    user_id = config.get("configurable", {}).get("user_id")
    if not user_id:
        return "Error: Usuario no identificado."

    candidate_ns = ("candidates", "learning")
    global_ns = ("global", "verified")

    # Check if a similar correction already exists in candidates
    results = await store.asearch(candidate_ns, query=correction, limit=1)

    if results and results[0].score > 0.8: # Umbral de similitud
        existing = results[0]
        voters = existing.value.get("voters", [])

        if str(user_id) in voters:
            return "Ya has registrado esta misma corrección anteriormente."

        voters.append(str(user_id))
        votes = len(voters)

        if votes >= 3:
            # Move to global verified
            new_key = str(uuid.uuid4())
            await store.aput(global_ns, new_key, {"rule": existing.value.get("correction")})
            await store.adelete(candidate_ns, existing.key)
            return "¡Gracias! Esta corrección ha alcanzado los 3 votos y ahora es una regla verificada globalmente."

        await store.aput(
            candidate_ns,
            existing.key,
            {"correction": existing.value.get("correction"), "voters": voters}
        )
        return f"Voto añadido a la corrección existente. Votos actuales: {votes}/3."

    else:
        # Create new candidate
        key = str(uuid.uuid4())
        await store.aput(candidate_ns, key, {"correction": correction, "voters": [str(user_id)]})
        return "Corrección registrada como candidata. Necesita 2 votos más de otros usuarios para volverse global."
