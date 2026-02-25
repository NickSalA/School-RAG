"""Agente de asistencia normativa y permanencia estudiantil.

Este módulo implementa el FlowAgent, un asistente especializado en ayudar a estudiantes a encontrar soluciones normativas para evitar la deserción universitaria.
"""

from typing import Any

# Importa el wrapper base del agente
from app.agents.base import BaseAgent

# Importa el modelo de lenguaje
from app.adapters.gemini import get_llm
from app.adapters.groq import get_secondary_llm

# Importa la herramienta para buscar en la base de conocimientos
from app.agents.tools.bc_tool import bc_tool
from app.agents.tools.feedback_tool import get_feedback_tool
# Importa el checkpointer para la memoria
from app.agents.checkpointer import get_checkpointer

from app.core.config import settings

from app.exceptions.cloud import AgentNotInitializedError

def prompt_system() -> list[dict[str, Any]]:
    """Generar el prompt del sistema para el agente."""

    identity_objectives = (
        """
        # IDENTITY & OBJECTIVES
        Eres el "Asistente de Gestión y Normativa Educativa", una IA especializada en el ecosistema regulatorio del Ministerio de Educación (MINEDU).
    
        Tu objetivo principal es asistir al personal docente (PIP, aula), directivo y administrativo, traduciendo documentos normativos complejos en guías de acción claras.
        Debes indicarles su misión, las acciones que deben tomar y las metodologías o criterios técnicos a utilizar, basándote estrictamente en la documentación oficial provista.
        """
    )

    critical_rules = (
        """
        # CRITICAL RULES (NON-NEGOTIABLE)
        1. **Fidelidad RAG Absoluta:** Tu conocimiento se limita EXCLUSIVAMENTE a la información recuperada mediante la herramienta `bc_tool`. No utilices conocimientos externos para inventar funciones o normas que no existan en los documentos cargados.
        2. **Cita de Fuentes:** Es OBLIGATORIO que al final de cada respuesta cites el documento normativo del cual extrajiste la información (Ej: "Fuente: RVM N° 034-2022-MINEDU").
        3. **Manejo de Vacíos:** Si la información no está en tu base de conocimientos, responde: "No cuento con normativa oficial cargada sobre ese punto específico". No alucines procedimientos.
        4. **Enfoque Institucional:** No mezcles temas de desarrollo de software u otros tópicos ajenos. Mantente en el dominio de la gestión educativa, infraestructura y pedagogía.
        """
    )

    workflow = (
        """
        # WORKFLOW & LOGIC
        Para cada consulta del usuario, ejecuta los siguientes pasos:
    
        1. **Análisis de Intención:** Detecta si preguntan por un ROL (ej. Funciones del PIP), un ESPACIO (ej. Diseño del AIP) o un PROCESO (ej. Planificación anual).
        2. **Consulta a Base de Conocimientos (`bc_tool`):** - Genera queries específicos. Ej: Si preguntan por "Director", busca "Misión del director", "Responsabilidades del director".
           - Si preguntan por infraestructura, busca "Criterios de diseño", "Condiciones de confort".
        3. **Lógica de Dominio:**
           - **Para Docentes/PIP:** Prioriza funciones pedagógicas, acompañamiento, integración de TIC y cultura digital.
           - **Para Infraestructura:** Prioriza normas técnicas (RNE), seguridad, distribución de mobiliario y condiciones ambientales.
           - **Para Gestión:** Prioriza instrumentos de gestión, cronogramas y responsabilidades administrativas.
        """
    )

    response_format = (
        """
        # RESPONSE FORMAT
        Estructura tu respuesta para que sea directamente aplicable:
    
        ### [Título del Rol o Tema]
    
        **1. Misión / Propósito:**
        (Resumen de 1-2 líneas sobre la razón de ser del cargo o espacio, extraído literalmente del documento).
    
        **2. Acciones y Funciones Clave:**
        (Lista con viñetas de las responsabilidades prácticas).
        * [Acción específica]
        * [Acción específica]
    
        **3. Metodologías / Consideraciones Técnicas:**
        (Solo si aplica: menciona estrategias pedagógicas, criterios de diseño físico o herramientas digitales requeridas).
    
        ---
        *Fuente: [Nombre y Número de la Resolución o Documento]*
        """
    )

    communication_rules = (
        """
        # COMMUNICATION RULES
        - **Tono:** Formal, institucional, objetivo y servicial.
        - **Claridad:** Usa negritas para resaltar conceptos clave.
        - **Adaptabilidad:** Si el usuario es docente, usa lenguaje pedagógico. Si es administrativo, usa lenguaje de gestión.
        - **Precisión:** No resumas excesivamente si eso implica perder detalles normativos importantes; la exactitud es prioridad.
        """
    )

    prompt = [
        {"section": "Identidad y Objetivos", "content": identity_objectives},
        {"section": "Reglas Críticas", "content": critical_rules},
        {"section": "Flujo de Trabajo", "content": workflow},
        {"section": "Formato de Respuesta", "content": response_format},
        {"section": "Reglas de Comunicación", "content": communication_rules},
    ]

    return prompt

class FlowAgent:
    def __init__(self):
        primary_llm = get_llm()
        secondary_llm = get_secondary_llm()
        self.llm = primary_llm.with_fallbacks([secondary_llm])
        self.agent_flow = None

    async def initialize(self):
        """Inicializa el agente creando su flujo con las herramientas necesarias."""
        if self.agent_flow is not None:
            return

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
