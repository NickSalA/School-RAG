"""Herramienta para crear feedback sobre las respuestas del modelo."""

from langchain_core.tools import tool

from app.schemas.feedback_schema import FeedbackCreate

from app.services.feedback import FeedbackService

from app.core.database import get_session_context


def get_feedback_tool():
    """Devuelve una herramienta para crear feedback sobre las respuestas del modelo."""
    @tool(
        "create_feedback",
        description=("Eres una herramienta que permite crear feedback sobre la respuesta generada por el modelo."\
                    "Usa esta herramienta para registrar si la respuesta fue útil, si resolvió la tarea y cualquier comentario adicional que el usuario quiera proporcionar."\
                    "rating debe ser un número entre 1 y 5, donde 1 es muy insatisfecho y 5 es muy satisfecho."\
                    "comments debe ser una cadena de texto con comentarios adicionales del usuario."\
                    ),
        args_schema=FeedbackCreate
    )
    async def create_feedback(task_resolved: bool, rating: int, comments: str, conversation_id: int) -> str:
        """Crea un nuevo feedback en la base de datos."""
        feedback = FeedbackCreate(
            task_resolved=task_resolved,
            rating=rating,
            comments=comments,
            conversation_id=conversation_id
        )

        async with get_session_context() as session:
            feedback_service = FeedbackService(session)
            await feedback_service.create(feedback)

        return "Feedback guardado, el administrador podrá revisarlo para mejorar el sistema. Gracias por tu colaboración."
